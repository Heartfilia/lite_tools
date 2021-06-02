# -*- coding: utf-8 -*-
from lite_tools import get_md5, get_sha, get_sha3, get_b64e, get_b64d


# about hashlib  ==> get_md5, get_sha, get_sha3  || default mode=256
s = "test_information"  # 这里只能丢字符串 
print(get_md5(s))                # 5414ffd88fcb58417e64ecec51bb3a6b
print(get_md5(s, upper=True))    # 5414FFD88FCB58417E64ECEC51BB3A6B
print(get_md5(s, to_bin=True))   # b'T\x14\xff\xd8\x8f\xcbXA~d\xec\xecQ\xbb:k'  # 转成二进制的需求没什么用但是可以保留
print(get_sha(s))                # d09869fdf901465c8566f0e2debfa3f6a3d878a8157e199c7c4c6dd755617f33
print(get_sha(s, to_bin=True))   # b'\xd0\x98i\xfd\xf9\x01F\\\x85f\xf0\xe2\xde\xbf\xa3\xf6\xa3\xd8x\xa8\x15~\x19\x9c|Lm\xd7Ua\x7f3'
print(get_sha(s, mode=1))        # ada5dfdf0c9a76a84958310b838a70b6fd6d01f6   # default mode=256  // mode: 1 224 256 384 512
print(get_sha3(s))               # 9c539ca35c6719f546e67837ff37fe7791e53fe40715cd4da0167c78c9adc2e8
print(get_sha3(s, to_bin=True))  # b'\x9cS\x9c\xa3\\g\x19\xf5F\xe6x7\xff7\xfew\x91\xe5?\xe4\x07\x15\xcdM\xa0\x16|x\xc9\xad\xc2\xe8'
print(get_sha3(s, mode=1))       # return "" // SUPPORT: sha3_224 sha3_256 sha3_384 sha3_512// only need inputting: 224 256 384 512  # default mode=256 // mode: 224 256 384 512
print(get_sha3(s, mode=384))     # 95c09e20a139843eae877a64cd95d6a629b3c9ff383b5460557aab2612682d4228d05fe41606a79acf5ae1c4de35160c


# about base64  ==> get_b64e, get_b64d
res_b64_encode = get_b64e(s)              
print(res_b64_encode)          # dGVzdF9pbmZvcm1hdGlvbg==

res_b64_bin = get_b64e(s, to_bin=True)
print(res_b64_bin)               # b'dGVzdF9pbmZvcm1hdGlvbg=='

res_b32_encode = get_b64e(s, mode=32)  # default mode=64  // mode: 16 32 64 85
print(res_b32_encode)            # ORSXG5C7NFXGM33SNVQXI2LPNY======

res_b64_decode = get_b64d(res_b64_encode)
print(res_b64_decode)            # test_information

res_b32_decode = get_b64d(res_b32_encode, mode=32)  # default mode=64  // mode: 16 32 64 85
print(res_b32_decode)            # test_information
