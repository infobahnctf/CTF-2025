#!/usr/local/bin/python3 -u
from ast import literal_eval

exc_table = bytes.fromhex(input("Exception Table > "))
code = input("Code > ")

literal_eval.__code__ = literal_eval.__code__.replace(co_exceptiontable=exc_table)
literal_eval(code)