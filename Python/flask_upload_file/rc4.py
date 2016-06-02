#!/usr/bin/env python
# coding: utf-8
# author: Liu Yue
# Pw @ 2015-06-02 14:58:13

PUBLIC_KEY = [
    (u"5FB0995A-05B7-4A8A-99BC-9153A848B78B", 0),
    (u"40898636-3DE9-45E4-B534-FBB93F2FDDC9", 0),
    (u"20A93061-36C4-42F1-99F2-46EDEC554E52", 0),
    (u"F07FDB17-3AC6-4F35-A6AB-8207EA29ECB2", 1),
    (u"A4036BFA-984B-40DF-A6A6-A0A18301C1A3", 256),
]


def crypt(file_bytes, hex_index):

    key_bytes = [ord(i) for i in hex_index[0]]
    key_length = len(key_bytes)
    file_length = len(file_bytes)
    S = range(256)

    j = 0
    for i in range(256):
        j = (j + S[i] + key_bytes[i % key_length]) % 256
        S[i], S[j] = S[j], S[i]
    i = 0
    j = 0
    for m in range(hex_index[1]):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]

    for m in range(file_length):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        k = S[(S[i] + S[j]) % 256]
        file_bytes[m] = (file_bytes[m] ^ k)
    return file_bytes


def decrypt(file_name):

    file = open(file_name, 'rb')
    hex_string = file.read()
    file.close()

    hex_index = PUBLIC_KEY[ord(hex_string[0])]

    file_bytes = [ord(i) for i in hex_string[1:]]
    file_data = crypt(file_bytes, hex_index)
    file = open(file_name, 'wb')
    for byte in file_data:
        file.write(chr(byte))
    file.close()


if __name__ == '__main__':
    import sys
    decrypt(sys.argv[1])
