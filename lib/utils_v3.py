


@staticmethod
def readSignalsData(path):
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
        # QMessageBox.warning(None, 'Ошибка чтения файла', 'Возникла ошибка при попытке прочитать конфигурационный файл'
        #                                                  '\n[ {path} ]'.format(path=path), QMessageBox.Ok)
        return None

    sigtypes.sort()
    groups.sort()

    sigData['SIGNALTYPES'] = sigtypes
    sigData['SIGNALGROUPS'] = groups

    return sigData