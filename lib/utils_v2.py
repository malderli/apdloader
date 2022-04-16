import pandas as pd
import psycopg2
from PyQt5.QtWidgets import QMessageBox
import datetime


def uploadFromDB(paths, listOfSignals, dbLoginData, timeBeginEnd):
    # No signal selected warning
    if len(listOfSignals) == 0:
        QMessageBox.warning(None, 'Некорректное количество сигналов', 'Не выбранно ни одного сигнала для выгрузки. \
                            Будут созданы пустые файлы.', QMessageBox.Ok)

    # Connection open
    try:
        with psycopg2.connect(dbname=dbLoginData['dbname'],
                              user=dbLoginData['user'],
                              password=dbLoginData['password'],
                              host=dbLoginData['host']) as conn:

            # Select names
            with conn.cursor() as cursor:
                # Gen select names expression
                expression = 'SELECT * FROM nodes WHERE ' + \
                             ('tagname ~ \'' + ''.join(['^.*' + x + '.PV$|' for x in listOfSignals])[:-2] + '\';'
                              if (len(listOfSignals) > 0) else 'False;')
                print(expression)

                try:
                    cursor.execute(expression)
                    rows = cursor.fetchall()
                    names_data = pd.DataFrame(rows, columns=['nodeid', 'tagname', 'description', 'unit'])
                except:
                    QMessageBox.warning(None, 'Ошибка чтения', 'Возникла ошибка при попытке чтения данных из БД'
                                                               '\n[ nodes ]', QMessageBox.Ok)
                    return 2

                # Names file writing to disk
                try:
                    names_data.to_csv(paths[0], index=False)
                except:
                    QMessageBox.warning(None, 'Ошибка записи', 'Возникла ошибка при записи файла с '
                                        'данными об именах на диск.\n[ {path} ]'.format(path=paths[0]), QMessageBox.Ok)
                    return 3

                # Warning about non found signals
                # May be time consuming
                if len(listOfSignals) != len(names_data):
                    missed = []

                    for signal in listOfSignals:
                        found = names_data['tagname'].str.extract('(^.*{}.*$)'.format(signal)).isna().values.tolist()

                        if found == [] or not [False] in found:
                            missed.append(signal)

                    if len(missed) <= 80:
                        QMessageBox.warning(None, 'Отсутствие информации', 'Информация о сигнале отсутствует в БД'
                                                                           '\n{}'.format(str(missed)), QMessageBox.Ok)
                    else:
                        QMessageBox.warning(None, 'Отсутствие информации', 'Информация о сигнале отсутствует в БД'
                                                                           '\n{} и еще {} сигналов'.format(
                            str(missed[:80]), len(missed) - 80), QMessageBox.Ok)

                # Gen select values expression
                nodesToSelect = names_data['nodeid'].values
                expression = 'COPY (SELECT * FROM nodes_history WHERE (False' + \
                             ''.join(' OR nodeid = ' + str(x) for x in nodesToSelect) + \
                             ') AND time BETWEEN \'{begin}\' AND \'{end}\') TO \'{path}\' With CSV DELIMITER \',\'' \
                             ' HEADER;'.format(
                                 begin=timeBeginEnd[0].strftime('%F %T'),
                                 end=timeBeginEnd[1].strftime('%F %T'),
                                 path=paths[1])
                print(expression)

                try:
                    cursor.execute(expression)
                except:
                    QMessageBox.warning(None, 'Ошибка чтения', 'Возникла ошибка при попытке чтения '
                                                               'данных из БД, их записи'
                                                               ' \n [ values ]', QMessageBox.Ok)
                    return 4
    except:
        return 1

def getMinMaxTime(dbLoginData):
    try:
        with psycopg2.connect(dbname = dbLoginData['dbname'],
                              user = dbLoginData['user'],
                              password = dbLoginData['password'],
                              host = dbLoginData['host']) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT MIN(time), MAX(time) FROM nodes_history')
                rows = cursor.fetchall()
    except:
        QMessageBox.warning(None, 'Ошибка чтения',
                            'Возникла ошибка при попытке получения временных границ из БД',
                            QMessageBox.Ok)

        return [datetime.datetime.now(), datetime.datetime.now()]

    return rows[0]

def readSignalsData(path):
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
