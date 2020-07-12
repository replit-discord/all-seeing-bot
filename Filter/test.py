from ctypes import *


class Word(Structure):
    _fields_ = [
        ('paranoid', c_char),
        ('word', c_char_p)
    ]


class GoSlice(Structure):
    _fields_ = [
        ('data', POINTER(c_void_p)),
        ('len', c_longlong),
        ('cap', c_longlong)
    ]


filter = cdll.LoadLibrary('./libfilter.so')


words = [
    Word(1, b'hello'),
    Word(2, b'bye'),
    Word(0, b'lol')
]


voidData = []

for w in words:
    voidData.append(cast(pointer(w), c_void_p))

sliceData = (c_void_p * len(voidData))(*voidData)
thing = GoSlice(sliceData, len(voidData), len(voidData))


while True:

    print(filter.check(bytes(input(), 'ascii'), thing))
