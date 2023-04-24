import datetime

import pandas as pd
from sqlalchemy import create_engine
from PyQt5.QtWidgets import QMessageBox
from PyQt5.Qt import QObject
from PyQt5.QtCore import pyqtSignal
import threading
import zipfile
import os
import hashlib
import subprocess
from datetime import datetime


class Uploader(QObject):
    signalChangeUploadState = pyqtSignal(str)
    signalSwitchInterface = pyqtSignal(bool)
    signalThrowMessageBox = pyqtSignal(str, str)

    def __init__(self):
        super(QObject, self).__init__()

    def uploadFromDB_thread(self, paths, signals, interval, logindata):
        # Uploading data in separated thread to make interface usable during upload
        t = threading.Thread(target=self.uploadFromDB, args=(paths, signals, interval, logindata))
        t.start()

    def uploadFromDB(self, path, signals, interval, logindata):
        now = datetime.now().strftime('%d-%m-%Y_%H-%M')

        folder = os.path.split(path)[0]
        curfolder = os.getcwd()
        names_tmp_path = 'names_' + now + '.csv'
        data_tmp_path = 'data_' + now + '.csv'

        # No signal selected warning
        if len(signals) == 0:
            self.signalThrowMessageBox.emit('Некорректное количество сигналов', 'Не выбранно ни одного сигнала для '
                                                                                'выгрузки.')
            return 0

        self.signalSwitchInterface.emit(True)

        # Connection open
        conn_string = "postgresql://" + logindata["user"] + ":" + logindata["password"] + "@" \
                      + logindata["host"] + ":" + logindata["port"] + "/" + logindata["dbname"]
        try:
            engine = create_engine(conn_string)
            conn = engine.raw_connection()

            # Select names
            with conn.cursor() as cursor:

                # Gen unique name for progress DB names counter
                try:
                    cursor.execute(f'DROP SEQUENCE IF EXISTS qProgressNames;')
                    cursor.execute(f'CREATE SEQUENCE qProgressNames START 1;')

                    conn.commit()
                except:
                    self.signalThrowMessageBox.emit('ERROR', 'Can not create telemetry for DB names')

                # Gen select names expression
                expression = 'SELECT nodeid, tagname FROM nodes WHERE ' +\
                                 'NEXTVAL(\'' + 'qProgressNames' + '\') !=0 AND ' + \
                                 ('tagname ~ \'' + ''.join(['^root..*' + x + '.PV_ARCHIVE$|' for x in signals])[:-1] + '\';'
                                  if (len(signals) > 0) else 'False;') #_ARCHIVE
                print(expression)

                # Uploading data from DB 'nodes'
                try:
                    self.signalChangeUploadState.emit('Начата выгрузка имен из базы данных...')

                    threadNamesU = threading.Thread(target=cursor.execute, args=[expression])
                    threadNamesU.start()

                    with conn.cursor() as cursor_telemetry_names:
                        self.signalChangeUploadState.emit('Начата выгрузка данных сигналов из базы данных...')

                        while (threadNamesU.is_alive()):
                            threadNamesU.join(0.3)
                            cursor_telemetry_names.execute(f'SELECT last_value FROM qProgressNames;')
                            res = cursor_telemetry_names.fetchall()
                            self.signalChangeUploadState.emit('Обработано ' + str(res[0][0]) + ' имен...')

                    rows = cursor.fetchall()
                    conn.commit()
                    names_data = pd.DataFrame(rows, columns=['nodeid', 'tagname'])

                    self.signalChangeUploadState.emit('Выгрузка имен из базы окончена.')
                except:
                    self.signalThrowMessageBox.emit('Ошибка записи', 'Возникла ошибка при попытке чтения данных '
                                                                         'из БД \n[ nodes ]')
                    self.signalSwitchInterface.emit(False)
                    return 2
                finally:
                    cursor.execute(f'DROP SEQUENCE IF EXISTS qProgressNames;')
                    conn.commit()

                # Names file writing to disk
                try:
                    names_data.to_csv(curfolder + os.sep + names_tmp_path, index=False)
                except:
                    self.signalThrowMessageBox.emit('Ошибка записи', 'Возникла ошибка при записи файла с данными '
                                                            'имен на диск.\n[ {path} ]'.format(path=folder))
                    self.signalSwitchInterface.emit(False)
                    return 3

                # Warning about non found signals
                # May be time-consuming
                if len(signals) != len(names_data):
                    self.signalChangeUploadState.emit('Выгрузка данных имен завершена успешно, '
                                                  'проверка несоответствий...')
                    missed = []

                    for signal in signals:
                        found = names_data['tagname'].str.extract('(^.*{}.*$)'.format(signal)).isna().values.tolist()

                        if found == [] or not [False] in found:
                            missed.append(signal)

                    if len(missed) <= 80:
                        self.signalThrowMessageBox.emit('Отсутствие информации', 'Информация о сигнале отсутствует'
                                                                             ' в БД\n{}'.format(str(missed)))
                    else:
                        self.signalThrowMessageBox.emit('Отсутствие информации', 'Информация о сигнале в БД\n'
                                                                             '{} и еще {} сигналов'.format(
                            str(missed[:80]), len(missed) - 80), QMessageBox.Ok)


                # Select data
                # Creating telemetry sequence
                try:
                    cursor.execute(f'DROP SEQUENCE IF EXISTS qProgressData;')
                    cursor.execute(f'CREATE SEQUENCE qProgressData START 1;')
                    conn.commit()
                except:
                    self.signalThrowMessageBox.emit('ERROR', 'Can not create telemetry for Data')

                # Gen select values expression
                nodesToSelect = names_data['nodeid'].values

                expression = 'COPY (SELECT  nodeid, valdouble, actualtime, quality FROM nodes_history WHERE (False' + \
                            ''.join(' OR nodeid = ' + str(x) for x in nodesToSelect) + \
                            ') AND NEXTVAL(\'' + 'qProgressData' + '\') !=0 AND time BETWEEN \'{begin}\' AND \'{end}\') ' \
                            'TO \'{path}\' WITH CSV DELIMITER \',\' HEADER;'.format(
                            begin=interval[0].strftime('%F %T'),
                            end=interval[1].strftime('%F %T'),
                            path=logindata["remfolder"] + os.sep + data_tmp_path)
                print(expression)

                # Uploading data from DB 'nodes_history'
                try:
                    with open(os.sep + os.sep + logindata["host"] + os.sep + logindata["folder"] + os.sep + data_tmp_path, 'w') as fs:

                        threadDataU = threading.Thread(target=cursor.copy_expert, args=[expression, fs, 4000000000])
                        threadDataU.start()

                        # Sending info about uploading status to interface
                        with conn.cursor() as cursor_telemetry_data:
                            self.signalChangeUploadState.emit('Начата выгрузка данных сигналов из базы данных...')

                            while(threadDataU.is_alive()):
                                threadDataU.join(0.3)
                                cursor_telemetry_data.execute(f'SELECT last_value FROM qProgressData;')
                                res = cursor_telemetry_data.fetchall()
                                self.signalChangeUploadState.emit('Обработано ' + str(res[0][0]) + ' строк...')

                    self.signalChangeUploadState.emit('Выгрузка имен из базы окончена.')

                except:
                    self.signalThrowMessageBox.emit('Ошибка чтения', 'Возникла ошибка при попытке чтения данных из '
                                                                         'БД \n [ nodes_history ]')
                    self.signalSwitchInterface.emit(False)
                    return 4

                finally:
                    try:
                        cursor.execute(f'DROP SEQUENCE IF EXISTS qProgressData;')
                        conn.commit()
                    except:
                        self.signalThrowMessageBox.emit('Ошибка удаления последовательности',
                                                        f'Ошибка в выполнении скрипта: DROP SEQUENCE IF EXISTS qProgressData!')
                        self.signalSwitchInterface.emit(False)

            cursor.close()
            conn.close()

        except:
            self.signalThrowMessageBox.emit('Ошибка открытия подключения', 'Ошибка открытия подключения для чтения из таблицы !')
            self.signalSwitchInterface.emit(False)
            return 1

        self.signalChangeUploadState.emit('Выполняется сжатие полученных данных...')


        if (logindata["host"] != "127.0.0.1" and logindata["host"] != "localhost"):
            try:
                msg = "copy /Y " + os.sep + os.sep + logindata["host"] + os.sep + logindata["folder"] + os.sep + data_tmp_path + " " + data_tmp_path
                print(msg)
                subprocess.check_output(msg, shell=True)
                msg = "del " + os.sep + os.sep + logindata["host"] + os.sep + logindata["folder"] + os.sep + data_tmp_path
                print(msg)
                subprocess.check_output(msg, shell=True)
            except:
                self.signalThrowMessageBox.emit('Ошибка копирования файла',
                                                'Ошибка копирования файла с удаленной машины !')
                self.signalSwitchInterface.emit(False)
                return 1

        try:
            BUF_SIZE = 65536
            hash_names = hashlib.sha1()
            hash_data = hashlib.sha1()

            with open(folder + os.sep + names_tmp_path, 'rb') as f:
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    hash_names.update(data)

            with open(folder + os.sep + data_tmp_path, 'rb') as f:
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    hash_data.update(data)

            with zipfile.ZipFile(path, 'w') as zip:
                zip.setpassword(b"intay#utz")
                zip.write(folder + os.sep + names_tmp_path, arcname=names_tmp_path, compress_type=zipfile.ZIP_DEFLATED)
                zip.getinfo(names_tmp_path).comment = hash_names.hexdigest().encode()
                zip.write(folder + os.sep + data_tmp_path, arcname=data_tmp_path, compress_type=zipfile.ZIP_DEFLATED)
                zip.getinfo(data_tmp_path).comment = hash_data.hexdigest().encode()

        except:
            self.signalThrowMessageBox.emit('Ошибка сжатия файла', path)

        self.signalSwitchInterface.emit(False)

    def readSignalsData(self, path):
        sigData = {}
        sigData['SIGNALS'] = []

        sigtypes = []
        groups = []

        try:
            with open(path, 'r') as fs:
                lines = fs.readlines()

                for row, line in enumerate(lines):
                    line = line.rstrip('\n')
                    params = line.split(';')
                    sigtype = params[1].split('_')[0]

                    while '9' >= sigtype[-1] >= '0':
                        sigtype = sigtype[:-1]

                    if not sigtype in sigtypes:
                        sigtypes.append(sigtype)

                    if not params[3] in groups:
                        groups.append(params[3])

                    sigData['SIGNALS'].append({'TYPE': sigtype,
                                               'KKS': params[0],
                                               'TAG': params[1],
                                               'TEXT': params[2],
                                               'GROUP': params[3]})
        except:
            QMessageBox.warning(None, 'Ошибка чтения файла', 'Возникла ошибка при попытке прочитать конфигурационный файл'
                                                             '\n[ {path} ]'.format(path=path), QMessageBox.Ok)
            return None

        sigtypes.sort()
        groups.sort()

        sigData['SIGNALTYPES'] = sigtypes
        sigData['SIGNALGROUPS'] = groups

        return sigData
