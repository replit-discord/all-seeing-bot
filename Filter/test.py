import ctypes


class Word(ctypes.Structure):
    _fields_ = [
        ('paranoid', ctypes.c_char),
        ('word', ctypes.c_char_p)
    ]


class GoSlice(ctypes.Structure):
    _fields_ = [
        ('data', ctypes.POINTER(ctypes.c_void_p)),
        ('len', ctypes.c_longlong),
        ('cap', ctypes.c_longlong)
    ]


filter = ctypes.cdll.LoadLibrary('./libfilter.so')

# Feel free to add more words.
words = [
    # Word(0, b'hello'),-
    Word(1, b'bye'),
    Word(2, b'lol'),
    Word(1, b'anime'),
    Word(2, b'word'),
    Word(1, b'fuck')
]


voidData = []

for w in words:
    voidData.append(ctypes.cast(ctypes.pointer(w), ctypes.c_void_p))

sliceData = (ctypes.c_void_p * len(voidData))(*voidData)
thing = GoSlice(sliceData, len(voidData), len(voidData))

filter.test(bytes(input("String to test \n> "), 'utf-8'), thing)


# Feel free to add more words.
words = [
    # Word(0, b'hello'),-
    Word(1, b'bye'),
    Word(2, b'lol'),
    Word(1, b'anime'),
    Word(2, b'word'),
    Word(1, b'fuck'),
    Word(1, b'oof')
]


voidData = []

for w in words:
    voidData.append(ctypes.cast(ctypes.pointer(w), ctypes.c_void_p))

sliceData = (ctypes.c_void_p * len(voidData))(*voidData)
thing = GoSlice(sliceData, len(voidData), len(voidData))


while True:

    filter.test(bytes(input("String to test (v2)\n> "), 'utf-8'), thing)
