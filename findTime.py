timeList = [
    'd',
    'm',
    's',
    'w',
    'mo'
]


def findTime(string):
    global timeList
    if string[-1] in timeList:
        duration = int(string[:-1])
        Ti = string[-1]
        if Ti == 'd':
            time = 86400 * duration
        elif Ti == 'm':
            time = 60 * duration
        elif Ti == 's':
            time = duration
        elif Ti == 'w':
            time = 604800 * duration
        elif Ti == 'mo':
            time = 2629746 * duration
    else:
        time = 60 * int(string)
    return int(time)
