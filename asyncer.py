import asyncio
from threading import Thread

coros = {}
debug_coros = True  # False
sync_thread = None


async def corowaiter():
    while 1:
        if sync_thread and not sync_thread.is_alive():
            # main process crashed, so this one should too
            if debug_coros:
                print(' ** coro-waiter stopping because main code seems to be stopped')
            return
        # use list so if `coros` changes size
        # while iterating, it doesnt break
        for c in list(coros):
            if coros[c]['status'] == 'pending':
                coros[c]['status'] = 'executing'
                if debug_coros:
                    print(' ** coro run %r' % c)
                try:
                    result = await coros[c]['coro']
                except BaseException as exc:  # if there was an error, store it
                    coros[c]['exception'] = exc
                else:  # if there was *not* an err, store return value
                    coros[c]['result'] = result
                coros[c]['status'] = 'done'
        await asyncio.sleep(0.2)


def syncawait(coro):
    unid = id(coro)  # or another form of unique coro id
    assert unid not in coros  # sanity check
    coros[unid] = {'coro': coro, 'status': 'pending'}
    while coros[unid]['status'] != 'done':
        pass
    if 'exception' in coros[unid]:
        # re-raise exception in the synchronous code
        raise coros[unid]['exception']
    result = coros[unid]['result']
    del coros[unid]
    return result


def start_waiter(callback):
    global sync_thread
    sync_thread = Thread(target=callback)
    sync_thread.start()
    asyncio.get_event_loop().run_until_complete(corowaiter())


async def _testasy(x):
    return float(x) * 2


def _main():
    print('starting asyncer test code')
    while 1:
        i = input('>')
        print(syncawait(_testasy(i)))


if __name__ == '__main__':
    start_waiter(_main)
