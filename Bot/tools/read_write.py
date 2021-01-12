import ast
import json
from encryption_tools import encode, decode
import os
import motor.motor_asyncio

mongo_link = os.getenv('mlab_link') + '?retryWrites=false'
client = motor.motor_asyncio.AsyncIOMotorClient(mongo_link)
db = client.asb_dev
main_collection = db.main_collection

key = os.environ.get('KEY')


class Cache:
    _data = {}

    @property
    def data(self):
        return self._data

    def cache(self, key, value):
        '''Add data to cache'''
        data = self.data
        data[key] = value
        self._data = data

    def read_cache(self, key):
        cache = self.data

        if key in cache:

            return cache[key]

    def check_cache(self, key):
        cache = self.data
        return key in cache


cache = Cache()


async def read(src, l_eval=True, decrypt=True, read_from_cache=True):
    is_cached = cache.check_cache(src)
    if is_cached and read_from_cache:
        data = cache.read_cache(src)

        if isinstance(data, str):
            try:
                data = ast.literal_eval(data)
            except ValueError:
                pass
            except SyntaxError:
                pass
        return data

    if decrypt:
        try:
            data = decode(key, (
                (await main_collection.find_one({"_id": src}))['data'].decode("utf-8")))
        except AttributeError:
            data = decode(
                key,
                (await main_collection.find_one({"_id": src}))['data']
            )
        except TypeError:
            await main_collection.insert_one(
                {
                    "_id": src,
                    "data": encode(key, str({}))
                }
            )
            data = {}

        if l_eval:
            value = ast.literal_eval(str(data))

        else:
            value = str(data)

        cache.cache(src, value)
        return value

    else:

        try:

            data = (await main_collection.find_one({"_id": src}))['data']

        except TypeError:

            await main_collection.insert_one({"_id": src, "data": str({})})
            data = {}

        if l_eval:
            value = ast.literal_eval(data)

        else:
            value = str(data)

        cache.cache(src, value)
        return value


async def write(src, data, encrypt=True):
    cache.cache(src, data)
    if encrypt:
        data = encode(key, str(data))
        try:
            await main_collection.insert_one({"_id": src, "data": str(data)})
        except:
            await main_collection.update_one(
                {"_id": src},
                {"$set": {"data": str(data)}}
            )
    else:
        try:
            await main_collection.insert_one({"_id": src, "data": str(data)})
        except:
            await main_collection.update_one(
                {"_id": src},
                {"$set": {"data": str(data)}}
            )
