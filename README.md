#F5Utils Documentation

Abstract:
F5utils is a tool written on python and using the grako (an EBNF parser generator) which is able to understand F5 exported config files.

Installation:
Get //depot/fifaops/ShellScripts/F5utils/ folder from Perforce. and make F5utils.py executable (chmod 775 F5utils.py on *nix)
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


#Example:
./F5utils.py 439384-2015-08-06-bigip.conf 10.99.39.124
Finding: 10.99.39.124
Vip Name : VS-pal-stage-10.99.34.59-20101-internal-public
Vip Pool : POOL_pal_stage_public
Vip Dest : 10.99.34.59 Port: 20101
Vip Profiles : [u'ONECONNECT-VS-pal_stage_public ', u'PROF-TCP-2hr-timeout-LAN ',
u'http-xff ']
Pool Members:

IP: 10.99.39.121 Port: 20103
IP: 10.99.39.122 Port: 20103
IP: 10.99.39.123 Port: 20103
IP: 10.99.39.124 Port: 20103
IP: 10.99.39.125 Port: 20103


Vip Name : VS-pal-stage-10.99.34.59-20292-internal-private
Vip Pool : POOL_pal_stage_private
Vip Dest : 10.99.34.59 Port: 20292
Vip Profiles : [u'ONECONNECT-VS-pal_stage_private ', u'PROF-TCP-2hr-timeout-LAN ',
u'http-xff ']
Pool Members:

IP: 10.99.39.121 Port: 20102
IP: 10.99.39.122 Port: 20102
IP: 10.99.39.123 Port: 20102
IP: 10.99.39.124 Port: 20102
IP: 10.99.39.125 Port: 20102


NOTE
Note that the previous output, is looking for IP: 10.99.39.124 on 439384-2015-08-06-bigip.conf file, and its output tells us that VIP
VS-pal-stage-10.99.34.59-20101-internal-public, and VS-pal-stage-10.99.34.59-20292-internal-private
mentions
POOL_pal_stage_public and POOL_pal_stage_private, and on those pools our beloved ip is found.
But if you search on the file, you'll find that 10.99.39.124 POOL_THI9_load_private_back and
POOL_THI9_load_public_back.
These POOls are not referenced by any VIPS, so they're not mentioned.
Also please note that the return code of the script, will be the number of vips wich have pools
referencing our ip.
