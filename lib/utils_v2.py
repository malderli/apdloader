import pandas as pd
import psycopg2
from PyQt5.QtWidgets import QMessageBox
from PyQt5.Qt import QObject
from PyQt5.QtCore import pyqtSignal
import datetime
import threading

class Uploader(QObject):
    signalChangeUploadState = pyqtSignal(str)
    signalSwitchInterface = pyqtSignal(bool)
    signalThrowMessageBox = pyqtSignal(str, str)

    def __init__(self):
        super(QObject, self).__init__()

    def uploadFromDB_thread(self, paths, listOfSignals, dbLoginData, timeBeginEnd):
        t = threading.Thread(target=self.uploadFromDB, args=(paths, listOfSignals, dbLoginData, timeBeginEnd))
        t.start()
        # t.join()

    def uploadFromDB(self, paths, listOfSignals, dbLoginData, timeBeginEnd):
        self.signalSwitchInterface.emit(True)

        # No signal selected warning
        if len(listOfSignals) == 0:
            # QMessageBox.warning(None, 'Некорректное количество сигналов', 'Не выбранно ни одного сигнала для выгрузки. \
            #                     Будут созданы пустые файлы.', QMessageBox.Ok)
            self.signalThrowMessageBox.emit('Некорректное количество сигналов', 'Не выбранно ни одного сигнала для '
                                                                                'выгрузки. Будут созданы пустые файлы.')

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

                    try:
                        self.signalChangeUploadState.emit('Начата выгрузка имен из базы данных...')

                        tDbNames = threading.Thread(target=cursor.execute, args=[expression])

                        tDbNames.start()
                        with psycopg2.connect(dbname=dbLoginData['dbname'],
                                              user=dbLoginData['user'],
                                              password=dbLoginData['password'],
                                              host=dbLoginData['host']) as conn_DbNamesT:
                            with conn_DbNamesT.cursor() as cursor_telemetry_names:
                                self.signalChangeUploadState.emit('Начата выгрузка данных сигналов из базы данных...')

                                while (tDbNames.is_alive()):
                                    tDbNames.join(0.3)
                                    cursor_telemetry_names.execute(f'SELECT last_value FROM {qProgressNames};')
                                    res = cursor_telemetry_names.fetchall()
                                    self.signalChangeUploadState.emit('Обработано ' + str(res[0][0]) + ' имен...')

                        # cursor.execute(expression)
                        rows = cursor.fetchall()
                        names_data = pd.DataFrame(rows, columns=['nodeid', 'tagname'])

                        self.signalChangeUploadState.emit('Выгрузка имен из базы данных окончена.')
                    except:
                        # QMessageBox.warning(None, 'Ошибка чтения', 'Возникла ошибка при попытке чтения данных из БД'
                        #                                            '\n[ nodes ]', QMessageBox.Ok)
                        self.signalThrowMessageBox.emit('Ошибка записи', 'Возникла ошибка при попытке чтения данных '
                                                                         'из БД \n[ nodes ]')
                        self.signalSwitchInterface.emit(False)
                        return 2
                    finally:
                        cursor.execute(f'DROP SEQUENCE IF EXISTS {qProgressNames};')
                        conn.commit()


                    # Names file writing to disk
                    try:
                        names_data.to_csv(paths[0], index=False)
                    except:
                        self.signalThrowMessageBox.emit('Ошибка записи', 'Возникла ошибка при записи файла с данными об '
                                                                    'именах на диск.\n[ {path} ]'.format(path=paths[0]))
                        # QMessageBox.warning(None, 'Ошибка записи', 'Возникла ошибка при записи файла с '
                        #                     'данными об именах на диск.\n[ {path} ]'.format(path=paths[0]), QMessageBox.Ok)
                        self.signalSwitchInterface.emit(False)
                        return 3

                    # Warning about non found signals
                    # May be time consuming
                    # if len(listOfSignals) != len(names_data):
                    #     missed = []
                    #
                    #     for signal in listOfSignals:
                    #         found = names_data['tagname'].str.extract('(^.*{}.*$)'.format(signal)).isna().values.tolist()
                    #
                    #         if found == [] or not [False] in found:
                    #             missed.append(signal)
                    #
                    #     if len(missed) <= 80:
                    #         QMessageBox.warning(None, 'Отсутствие информации', 'Информация о сигнале отсутствует в БД'
                    #                                                            '\n{}'.format(str(missed)), QMessageBox.Ok)
                    #     else:
                    #         QMessageBox.warning(None, 'Отсутствие информации', 'Информация о сигнале отсутствует в БД'
                    #                                                            '\n{} и еще {} сигналов'.format(
                    #             str(missed[:80]), len(missed) - 80), QMessageBox.Ok)


                    qProgressData = "progress_" + datetime.datetime.now().strftime("%H_%M_%S_%f")
                    try:
                        cursor.execute(f'DROP SEQUENCE IF EXISTS {qProgressData};')
                        cursor.execute(f'CREATE SEQUENCE {qProgressData} START 1;')
                        conn.commit()
                    except:
                        self.signalThrowMessageBox.emit('ERROR', 'Can not create telemetry for Data')

                    # Gen select values expression
                    nodesToSelect = names_data['nodeid'].values
                    expression = 'COPY (SELECT * FROM nodes_history WHERE (False' + \
                                 ''.join(' OR nodeid = ' + str(x) for x in nodesToSelect) + \
                                 ') AND NEXTVAL(\'' + qProgressData + '\') !=0 AND time BETWEEN \'{begin}\' AND \'{end}\') ' \
                                 'TO \'{path}\' WITH CSV DELIMITER \',\' HEADER;'.format(
                                     begin=timeBeginEnd[0].strftime('%F %T'),
                                     end=timeBeginEnd[1].strftime('%F %T'),
                                     path=paths[1])

                    # expression = 'SELECT * FROM nodes_history WHERE (False' + \
                    #              ''.join(' OR nodeid = ' + str(x) for x in nodesToSelect) + \
                    #              ') AND NEXTVAL(\'' + qProgress + '\') !=0 AND time BETWEEN \'{begin}\' ' \
                    #              'AND \'{end}\''.format(
                    #                  begin=timeBeginEnd[0].strftime('%F %T'),
                    #                  end=timeBeginEnd[1].strftime('%F %T'))

                    print(expression)

                    try:
                        with open(paths[1], 'w') as fs:
                            t = threading.Thread(target=cursor.copy_expert, args=[expression, fs, 4000000000])
                            t.start()

                            with psycopg2.connect(dbname=dbLoginData['dbname'],
                                                  user=dbLoginData['user'],
                                                  password=dbLoginData['password'],
                                                  host=dbLoginData['host']) as conn2:

                                with conn2.cursor() as cursor_telemetry:
                                    self.signalChangeUploadState.emit('Начата выгрузка данных сигналов из базы данных...')

                                    while(t.is_alive()):
                                        t.join(0.3)
                                        cursor_telemetry.execute(f'SELECT last_value FROM {qProgressData};')
                                        res = cursor_telemetry.fetchall()
                                        self.signalChangeUploadState.emit('Обработано ' + str(res[0][0]) + ' строк...')

                    except:
                        # QMessageBox.warning(None, 'Ошибка чтения', 'Возникла ошибка при попытке чтения данных из БД'
                        #                                            ' \n [ values ]', QMessageBox.Ok)
                        self.signalThrowMessageBox.emit('Ошибка чтения', 'Возникла ошибка при попытке чтения данных из '
                                                                         'БД \n [ values ]')
                        self.signalSwitchInterface.emit(False)
                        return 4

                    finally:
                        cursor.execute(f'DROP SEQUENCE IF EXISTS {qProgressData};')
                        conn.commit()
        except:
            self.signalSwitchInterface.emit(False)
            return 1

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

