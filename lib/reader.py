
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

            while '9' >= type[-1] >= '0' :
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

