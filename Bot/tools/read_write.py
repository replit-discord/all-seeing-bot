import ast


async def read(src, l_eval=True, decrypt=True, read_from_cache=True):
    try:
        data = open(f'db/{src}.txt', 'r').read()
    except:
        data = '{}'

    if read_from_cache:
        return ast.literal_eval(data)

    return data


async def write(src, data, encrypt=True):
    open(f'db/{src}.txt', 'w').write(str(data))
