import pandas as pd
import psycopg2
from PyQt5.QtWidgets import QMessageBox
from PyQt5.Qt import QObject
from PyQt5.QtCore import pyqtSignal
import datetime
import threading
import zipfile
import os
import hashlib

class Uploader(QObject):
    signalChangeUploadState = pyqtSignal(str)
    signalSwitchInterface = pyqtSignal(bool)
    signalThrowMessageBox = pyqtSignal(str, str)

    def __init__(self):
        super(QObject, self).__init__()

    def uploadFromDB_thread(self, paths, now, listOfSignals, timeBeginEnd, dbLoginData):
        # Uploading data in separated thread to make interface usable during upload
        t = threading.Thread(target=self.uploadFromDB, args=(paths, now, listOfSignals, timeBeginEnd, dbLoginData))
        t.start()

    def uploadFromDB(self, paths, now, listOfSignals, timeBeginEnd, dbLoginData):
        folder = os.path.split(paths)[0]
        names_tmp_path = 'names_' + now + '.csv'
        data_tmp_path = 'data_' + now + '.csv'

        # No signal selected warning
        if len(listOfSignals) == 0:
            self.signalThrowMessageBox.emit('Некорректное количество сигналов', 'Не выбранно ни одного сигнала для '
                                                                                'выгрузки.')
            return 0

        self.signalSwitchInterface.emit(True)

        # Connection open
        try:
            with psycopg2.connect(dbname=dbLoginData['dbname'],
                                  user=dbLoginData['user'],
                                  password=dbLoginData['password'],
                                  host=dbLoginData['host']) as conn:

                # Select names
                with conn.cursor() as cursor:
                    # Gen unique name for progress DB names counter
                    qProgressNames = "progress_name_" + datetime.datetime.now().strftime("%H_%M_%S_%f")
                    try:
                        cursor.execute(f'DROP SEQUENCE IF EXISTS {qProgressNames};')
                        cursor.execute(f'CREATE SEQUENCE {qProgressNames} START 1;')

                        conn.commit()
                    except:
                        self.signalThrowMessageBox.emit('ERROR', 'Can not create telemetry for DB names')

                    # Gen select names expression
                    expression = 'SELECT nodeid, tagname FROM nodes WHERE ' +\
                                 'NEXTVAL(\'' + qProgressNames + '\') !=0 AND ' + \
                                 ('tagname ~ \'' + ''.join(['^root\..*' + x + '.PV$|' for x in listOfSignals])[:-1] + '\';'
                                  if (len(listOfSignals) > 0) else 'False;')
                    print(expression)

                    # Uploading data from DB 'nodes'
                    try:
                        self.signalChangeUploadState.emit('Начата выгрузка имен из базы данных...')

                        threadNamesU = threading.Thread(target=cursor.execute, args=[expression])
                        threadNamesU.start()

                        # Sending info about uploading status to interface
                        with psycopg2.connect(dbname=dbLoginData['dbname'],
                                              user=dbLoginData['user'],
                                              password=dbLoginData['password'],
                                              host=dbLoginData['host']) as conn_telemetry_names:
                            with conn_telemetry_names.cursor() as cursor_telemetry_names:
                                self.signalChangeUploadState.emit('Начата выгрузка данных сигналов из базы данных...')

                                while (threadNamesU.is_alive()):
                                    threadNamesU.join(0.3)
                                    cursor_telemetry_names.execute(f'SELECT last_value FROM {qProgressNames};')
                                    res = cursor_telemetry_names.fetchall()
                                    self.signalChangeUploadState.emit('Обработано ' + str(res[0][0]) + ' имен...')

                        rows = cursor.fetchall()
                        names_data = pd.DataFrame(rows, columns=['nodeid', 'tagname'])

                        self.signalChangeUploadState.emit('Выгрузка имен из базы окончена.')
                    except:
                        self.signalThrowMessageBox.emit('Ошибка записи', 'Возникла ошибка при попытке чтения данных '
                                                                         'из БД \n[ nodes ]')
                        self.signalSwitchInterface.emit(False)
                        return 2
                    finally:
                        cursor.execute(f'DROP SEQUENCE IF EXISTS {qProgressNames};')
                        conn.commit()

                    # Names file writing to disk
                    try:
                        names_data.to_csv(folder + os.sep + names_tmp_path, index=False)
                    except:
                        self.signalThrowMessageBox.emit('Ошибка записи', 'Возникла ошибка при записи файла с данными '
                                                            'имен на диск.\n[ {path} ]'.format(path=folder))
                        self.signalSwitchInterface.emit(False)
                        return 3

                    # Warning about non found signals
                    # May be time-consuming
                    if len(listOfSignals) != len(names_data):
                        self.signalChangeUploadState.emit('Выгрузка данных имен завершена успешно, '
                                                          'проверка несоответствий...')
                        missed = []

                        for signal in listOfSignals:
                            found = names_data['tagname'].str.extract('(^.*{}.*$)'.format(signal)).isna().values.tolist()

                            if found == [] or not [False] in found:
                                missed.append(signal)

                        if len(missed) <= 80:
                            self.signalThrowMessageBox.emit('Отсутствие информации', 'Информация о сигнале отсутствует'
                                                                                     ' в БД\n{}'.format(str(missed)))
                        else:
                            self.signalThrowMessageBox.emit('Отсутствие информации', 'Информация о сигнале в БД\n'
                                 '{} и еще {} сигналов'.format(str(missed[:80]), len(missed) - 80), QMessageBox.Ok)

                    # Creating telemetry sequence
                    qProgressData = "progress_" + datetime.datetime.now().strftime("%H_%M_%S_%f")
                    try:
                        cursor.execute(f'DROP SEQUENCE IF EXISTS {qProgressData};')
                        cursor.execute(f'CREATE SEQUENCE {qProgressData} START 1;')
                        conn.commit()
                    except:
                        self.signalThrowMessageBox.emit('ERROR', 'Can not create telemetry for Data')

                    # Gen select values expression
                    nodesToSelect = names_data['nodeid'].values
                    expression = 'COPY (SELECT  nodeid, valdouble, actualtime, quality FROM nodes_history WHERE (False' + \
                                 ''.join(' OR nodeid = ' + str(x) for x in nodesToSelect) + \
                                 ') AND NEXTVAL(\'' + qProgressData + '\') !=0 AND time BETWEEN \'{begin}\' AND \'{end}\') ' \
                                 'TO \'{path}\' WITH CSV DELIMITER \',\' HEADER;'.format(
                                     begin=timeBeginEnd[0].strftime('%F %T'),
                                     end=timeBeginEnd[1].strftime('%F %T'),
                                     path=folder + os.sep + data_tmp_path)

                    print(expression)

                    # Uploading data from DB 'nodes_history'
                    try:
                        with open(folder + os.sep + data_tmp_path, 'w') as fs:
                            threadDataU = threading.Thread(target=cursor.copy_expert, args=[expression, fs, 4000000000])
                            threadDataU.start()

                            with psycopg2.connect(dbname=dbLoginData['dbname'],
                                                  user=dbLoginData['user'],
                                                  password=dbLoginData['password'],
                                                  host=dbLoginData['host']) as conn_telemetry_data:

                                # Sending info about uploading status to interface
                                with conn_telemetry_data.cursor() as cursor_telemetry_data:
                                    self.signalChangeUploadState.emit('Начата выгрузка данных сигналов из базы данных...')

                                    while(threadDataU.is_alive()):
                                        threadDataU.join(0.3)
                                        cursor_telemetry_data.execute(f'SELECT last_value FROM {qProgressData};')
                                        res = cursor_telemetry_data.fetchall()
                                        self.signalChangeUploadState.emit('Обработано ' + str(res[0][0]) + ' строк...')

                    except:
                        self.signalThrowMessageBox.emit('Ошибка чтения', 'Возникла ошибка при попытке чтения данных из '
                                                                         'БД \n [ values ]')
                        self.signalSwitchInterface.emit(False)
                        return 4

                    finally:
                        cursor.execute(f'DROP SEQUENCE IF EXISTS {qProgressData};')
                        conn.commit()
        except:
            self.signalThrowMessageBox.emit('Ошибка открытия подключения', 'Ошибка открытия подключения')
            self.signalSwitchInterface.emit(False)
            return 1

        self.signalChangeUploadState.emit('Выполняется сжатие полученных данных...')

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

        with zipfile.ZipFile(paths, 'w') as zip:
            zip.write(folder + os.sep + names_tmp_path, arcname=names_tmp_path, compress_type=zipfile.ZIP_DEFLATED)
            zip.getinfo(names_tmp_path).comment = hash_names.hexdigest().encode()
            zip.write(folder + os.sep + data_tmp_path, arcname=data_tmp_path, compress_type=zipfile.ZIP_DEFLATED)
            zip.getinfo(data_tmp_path).comment = hash_data.hexdigest().encode()

        self.signalSwitchInterface.emit(False)

    def readSignalsData(self, path):
        sigData = {}
        sigData['SIGNALS'] = {}

        types = []
        groups = []

        try:
            with open(path, 'r') as fs:
                lines = fs.readlines()

                for line in lines:
                    line = line.rstrip('\n')
                    params = line.split(';')
                    type = params[1].split('_')[0]

                    while '9' >= type[-1] >= '0':
                        type = type[:-1]

                    if not type in types:
                        types.append(type)

                    if not params[3] in groups:
                        groups.append(params[3])

                    sigData['SIGNALS'][params[1]] = {'TYPE' : type,
                                                     'KKS' : params[0],
                                                     'TEXT' : params[2],
                                                     'GROUP' : params[3]}
        except:
            QMessageBox.warning(None, 'Ошибка чтения файла', 'Возникла ошибка при попытке прочитать конфигурационный файл'
                                '\n[ {path} ]'.format(path=path), QMessageBox.Ok)
            return None

        types.sort()
        groups.sort()

        sigData['SIGNALTYPES'] = types
        sigData['SIGNALGROUPS'] = groups

        return sigData

    # def getMinMaxTime(dbLoginData):
    #     try:
    #         with psycopg2.connect(dbname = dbLoginData['dbname'],
    #                               user = dbLoginData['user'],
    #                               password = dbLoginData['password'],
    #                               host = dbLoginData['host']) as conn:
    #             with conn.cursor() as cursor:
    #                 cursor.execute('SELECT MIN(time), MAX(time) FROM nodes_history;')
    #                 rows = cursor.fetchall()
    #     except:
    #         QMessageBox.warning(None, 'Ошибка чтения',
    #                             'Возникла ошибка при попытке получения временных границ из БД',
    #                             QMessageBox.Ok)
    #
    #         return [datetime.datetime.now(), datetime.datetime.now()]
    #     return rows[0]

