import ast
from encryption_tools import encode, decode
import os
from json_store_client import *
client = AsyncClient(os.environ.get('JSON_LINK'))

key = os.environ.get('KEY')

async def read(src, lEval=True, decrypt=True):
    if decrypt:
        data = decode(key, await client.retrieve(src))
        if lEval:
            value = ast.literal_eval(data)
        else:
            value = str(data)
        return value
    else:
        data = await client.retrieve(src)
    
        if lEval:
            value = ast.literal_eval(data)
        else:
            value = str(data)
        return value

async def write(src, value, encrypt=True):
    if encrypt:
        with open(src, 'w') as f:
            await client.store(src, encode(key, str(value)))
    else:
        with open(src, 'w') as f:
            await client.store(src, str(value))