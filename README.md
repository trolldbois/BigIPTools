#BigIPTool Documentation

Abstract:
#BigIP Toolis a tool written on python and using the grako (an EBNF parser generator) which is able to understand F5 exported config files.

Installation:
. and make F5utils.py executable (chmod 775 F5utils.py on *nix)
Yo will need Python >= 2.7, and grako >= 3.6.2 to run it.
If you run python scripts on Windows using Cygwin to install grako first install easy install:
https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
/usr/bin/easy_install-3.2 pip
Just Install grako via pip:
pip install grako


#Running:
./F5utils.py -h
Usage: F5utils.py [-h] [-m] file ip
Simple parser for F5 exported config files Author: Adrian Grebin
positional arguments:
file the input file to parse
ip Find VIPs and Pool names on which an IP is referenced as member
optional arguments:
-h, --help show this help message and exit
-m Show Pool Members
You have to provide an F5 config file, for example 439384-2015-08-06-bigip.conf 


