
def readSignalsData(path):
    sigData = {}
    sigData['SIGNALS'] = []

    types = []
    groups = []

    with open(path, 'r') as fs:
        for line in fs:
            line = line.rstrip('\n')

            signal = {}

            params = line.split(';')

            type = params[1].split('_')[0]

            if not type in types:
                types.append(type)

            if not params[3] in groups:
                groups.append(params[3])

            signal['KKS'] = params[0]
            signal['TYPE'] = type
            signal['TEXT'] = params[2]
            signal['GROUP'] = params[3]

            sigData['SIGNALS'].append(signal)

    types.sort()
    groups.sort()

    sigData['SIGNALTYPES'] = types
    sigData['SIGNALGROUPS'] = groups

    return sigData

