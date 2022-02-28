import pandas as pd
import psycopg2
import datetime

def uploadFromDB(path, listOfSignals, dbLoginData, timeBeginEnd):
    with psycopg2.connect(dbname = dbLoginData['dbname'],
                          user = dbLoginData['user'],
                          password = dbLoginData['password'],
                          host = dbLoginData['host']) as conn:

        # Select from names all and filter
        with conn.cursor() as cursor:
            regexp = '(' + ''.join(['^.*' + x + '.*$|' for x in listOfSignals])[:-1] + ')'
            print(regexp)

            if len(listOfSignals) == 0:
                names_data = pd.DataFrame([], columns=['nodeid', 'tagname', 'description', 'unit'])
            else:
                cursor.execute('SELECT * FROM names')
                rows = cursor.fetchall()
                names_data = pd.DataFrame(rows, columns=['nodeid', 'tagname', 'description', 'unit'])
                names_data = names_data[names_data['tagname'].str.extract(regexp).squeeze().notna()]

            names_data.to_csv(path + '/names.csv', index=False)

        with conn.cursor() as cursor:
            nodesToSelect = names_data['nodeid'].values
            expression = 'SELECT * FROM values WHERE (False' + \
                         ''.join(' OR nodeid = ' + str(x) for x in nodesToSelect)[:-2] + \
                         ') AND time > \'{begin}\' AND time < \'{end}\''.format(
                             begin=timeBeginEnd[0].strftime('%F %T'),
                             end=timeBeginEnd[1].strftime('%F %T'))

            print(expression)

            cursor.execute(expression)

            rows = cursor.fetchall()
            values_data = pd.DataFrame(rows, columns=['nodeid', 'actualtime', 'time', 'valint', 'valuint',
                                                      'valdouble', 'valbool', 'valstring', 'quality', 'recordtype'])

            values_data.to_csv(path + '/values.csv', index=False)

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

    with open(path, 'r') as fs:
        for line in fs:
            line = line.rstrip('\n')

            params = line.split(';')

            type = params[1].split('_')[0]

            while '9' >= type[-1] >= '0':
                type = type[:-1]

            if not type in types:
                types.append(type)

            if not params[3] in groups:
                groups.append(params[3])

            sigData['SIGNALS'][params[1]] = {'TYPE' : type, 'KKS' : params[0], 'TEXT' : params[2], 'GROUP' : params[3]}

    types.sort()
    groups.sort()

    sigData['SIGNALTYPES'] = types
    sigData['SIGNALGROUPS'] = groups

    return sigData


if __name__ == '__main__':
    tags = ['AT_FeedWaBefBoiler', 'AP_mFeedWaAftPVD', 'AFM_FeedWaAftPVD', 'AG_FeedWaBefECO_L1', 'AG_FeedWaBypBefECO_L2']

    # uploadFromDB('/home/malerli/', tags, {'dbname' : 'postgres',
    #                                           'user' : 'postgres',
    #                                           'password' : 'root',
    #                                           'host' : 'localhost'})

    getMinMaxTime({'dbname' : 'postgres',
                   'user' : 'postgres',
                   'password' : 'root',
                   'host' : 'localhost'})

