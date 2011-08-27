# -*- coding: utf-8 -*-

# Encryption imports.
#
import re
import urllib

# This method decodes the hex string.
#
def hexDecode(data):
  b16D ='0123456789abcdef'
  b16M = {}
  for i in range (0, 256):
    b16M[b16D[i>>4] + b16D[i&15]] = chr(i)

  if re.match("^[a-f0-9]*$", data, re.IGNORECASE) == None:
    return False

  if len(data) % 2:
    data = '0' + data

  result = []
  j = 0
  for i in range (0, len(data), 2):
    result.insert(j, b16M[data[i:i+2]])
    j += 1

  return "".join(["%s" % item for item in result])



def hexEncode(data):
  b16D='0123456789abcdef'
  b16M = []
  for i in range(0, 256):
    b16M.append(b16D[i>>4] + b16D[i & 15]);
  result = []
  for i in range(0, len(data)):
    result.append(b16M[ord(data[i])]);
  return ''.join(result);



# This method encrypts a string.
#
def rc4Encrypt(key, pt):
  s = []
  for i in range(0, 256):
    s.insert(i, i)

  j = 0
  x = 0
  for i in range(0, 256):
    j = (j + s[i] + ord(key[i % len(key)])) % 256
    x = s[i]
    s[i] = s[j]
    s[j] = x;

  i = 0
  j = 0
  ct = ''
  for y in range(0, len(pt)):
    i = (i + 1) % 256
    j = (j + s[i]) % 256
    x = s[i]
    s[i] = s[j]
    s[j] = x
    ct += chr(ord(pt[y]) ^ s[(s[i] + s[j]) % 256])

  return ct

def rc4EncryptStr(str, key):
  #return hexEncode(rc4Encrypt(key, unescape(encodeURIComponent(str))));
  return hexEncode(rc4Encrypt(key, urllib.unquote_plus(urllib.quote_plus(str))));

# RC4 decryption.
#
def rc4DecryptStr(hexStr, key):
  return rc4Encrypt(key, hexDecode(hexStr))
