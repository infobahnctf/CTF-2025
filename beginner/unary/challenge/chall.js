#!/usr/bin/env node
const readline = require('readline');
const FLAG = process.env.FLAG;
process.env.flag = FLAG;

console.log("unary-only sandbox\r\n");

const purifier = (code) => {
    const allowed = /^[a-zA-Z0-9_/\s;!().+\-*]+$/;
    let codeForChecking = code.replace(/\/\/.*$/gm, '');
    if (!allowed.test(code.trim())) throw new Error('BLOCKED');
    const mathOnly = /^[0-9+\-*/\s()]+$/;
    if (!mathOnly.test(codeForChecking.trim()) && codeForChecking.length > 10) throw new Error('TOO_LONG');
    return code.trim();
};

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
});

rl.on('line', (input) => {
    try {
        const sanitized = purifier(input);
        const vm = require('vm');
        const result = vm.runInNewContext(`(function(){return ${sanitized}})();`, { console, process }, { timeout: 1000, displayErrors: false });
        if (result !== undefined && result !== null && !isNaN(result) || result === 0) console.log(result);
    } catch (error) {
        if (error.message === 'TOO_LONG') console.log("Can't handle that much math :(");
        else if (error.message === 'BLOCKED') console.log('Nice try !');
        else console.log('What are you doing ?');
    }
});