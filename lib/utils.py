import pandas as pd
import psycopg2
from PyQt5.QtWidgets import QMessageBox
import datetime

def uploadFromDB(path, listOfSignals, dbLoginData, timeBeginEnd):
    with psycopg2.connect(dbname = dbLoginData['dbname'],
                          user = dbLoginData['user'],
                          password = dbLoginData['password'],
                          host = dbLoginData['host']) as conn:

        # No signal selected warning
        if len(listOfSignals) == 0:
            QMessageBox.warning(None, 'Некорректное количество сигналов', 'Не выбранно ни одного сигнала для выгрузки. \
                                Будут созданы пустые файлы.', QMessageBox.Ok)

        # Select from names all and filter
        with conn.cursor() as cursor:
            regexp = '(' + ''.join(['^.*' + x + '.*$|' for x in listOfSignals])[:-1] + ')'
            print(regexp)

            names_data = pd.DataFrame([], columns=['nodeid', 'tagname', 'description', 'unit']).squeeze()

            # Reading from database [ names ]
            try:
                if not len(listOfSignals) == 0:
                    cursor.execute('SELECT * FROM names')
                    rows = cursor.fetchall()
                    names_data = pd.DataFrame(rows, columns=['nodeid', 'tagname', 'description', 'unit'])
                    names_data = names_data[names_data['tagname'].str.extract(regexp).squeeze().notna()]
            except:
                QMessageBox.warning(None, 'Ошибка чтения', 'Возникла ошибка при попытке чтения данных из БД'
                                    ' \n [ names ]', QMessageBox.Ok)

            try:
                names_data.to_csv(path + '/names.csv', index=False)
            except:
                QMessageBox.warning(None, 'Ошибка записи', 'Возникла ошибка при записи файла с '
                                    'данными об именах на диск.\n[ {path} ]'.format(path=path + '/names.csv'),
                                    QMessageBox.Ok)

        # Warning about non found signals
        # May be time consuming
        if len(listOfSignals) != len(names_data):
            for signal in listOfSignals:
                if names_data['tagname'].str.extract('(^.*{}.*$)'.format(signal)).isna().values[0][0] == True:
                    QMessageBox.warning(None, 'Отсутствие информации', 'Информация о сигнале отсутствует в БД'
                                        '\n[ {name} ]'.format(name=signal), QMessageBox.Ok)

        # Values uploading
        with conn.cursor() as cursor:
            nodesToSelect = names_data['nodeid'].values
            expression = 'SELECT * FROM values WHERE (False' + \
                         ''.join(' OR nodeid = ' + str(x) for x in nodesToSelect)[:-2] + \
                         ') AND time > \'{begin}\' AND time < \'{end}\''.format(
                             begin=timeBeginEnd[0].strftime('%F %T'),
                             end=timeBeginEnd[1].strftime('%F %T'))

            print(expression)

            values_data = pd.DataFrame([], columns=['nodeid', 'actualtime', 'time', 'valint', 'valuint',
                                                    'valdouble', 'valbool', 'valstring', 'quality', 'recordtype'])

            # Reading from database [ values ]
            try:
                cursor.execute(expression)

                rows = cursor.fetchall()
                values_data = pd.DataFrame(rows, columns=['nodeid', 'actualtime', 'time', 'valint', 'valuint',
                                                          'valdouble', 'valbool', 'valstring', 'quality', 'recordtype'])
            except:
                QMessageBox.warning(None, 'Ошибка чтения', 'Возникла ошибка при попытке чтения данных из БД'
                                    ' \n [ values ]', QMessageBox.Ok)

            try:
                values_data.to_csv(path + '/values.csv', index=False)
            except:
                QMessageBox.warning(None, 'Ошибка записи', 'Возникла ошибка при записи файла с '
                                    'данными о значениях на диск. \n[ {path} ]'.format(path=path + '/values.csv'),
                                    QMessageBox.Ok)

def getMinMaxTime(dbLoginData):
    with psycopg2.connect(dbname = dbLoginData['dbname'],
                          user = dbLoginData['user'],
                          password = dbLoginData['password'],
                          host = dbLoginData['host']) as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT MIN(time), MAX(time) FROM values')
            rows = cursor.fetchall()

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
