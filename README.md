# 🤔 What for?

This tool was created during a pentest because the classic tools did not allow to easily perform a 

dictionary attack on the Django administration site.

This tool allows to bypass the csrf token protection implemented on the login page.

# 📐 Installation 📏

## Cloning source
git clone https://github.com/n3bojs4/DjangoUnchained.git


## installing in python virtual env
```
cd DjangoUnchained && python3 -m venv .
source bin/activate
pip install -U pip && pip install -r requirements.txt
```
## installing on the system
```
cd DjangoUnchained && pip install -r requirements.txt

```

# 🏃‍♀️ Running DjangoUnchained

## 📕 Help

```
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

Django Admin Panel password testing tool v0.2 - by n3bojs4
https://github.com/n3bojs4/DjangoUnchained  python:3.10.6 

usage: DjangoUnchained.py [-h] -domain DOMAIN -scheme SCHEME -uri URI -userdict USERDICT -passwdict PASSWDICT [-onlygood] [-rua] [-l L] [-restore RESTORE]

options:
  -h, --help            show this help message and exit
  -domain DOMAIN        Domain for the django admin login page ( add the :port if non standard, eq: domain.com:8000 ).
  -scheme SCHEME        http or https scheme.
  -uri URI              uri for the admin login page, "/admin/login/" is the most common.
  -userdict USERDICT    dictionnary file for user list.
  -passwdict PASSWDICT  dictionnary file for password.
  -onlygood             Show only good attempts.
  -rua                  Use random user-agent.
  -l L                  Log to a file.
  -restore RESTORE      restore from a .session file, by default domain name is used to save the session.



```

## Usage Examples

Trying a dictionnary attack and logging to a file :


```

DjangoUnchained.py -domain MyDomain.com:8000 -scheme https -uri /admin/login/ -userdict /usr/share/wordlists/seclists/usernames -passwdict /usr/share/wordlists/rockyou.txt -l /home/myuser/file.log

```

Restore a previous session aborted :

```

DjangoUnchained.py -domain MyDomain.com:8000 -scheme https -uri /admin/login/ -userdict /usr/share/wordlists/seclists/usernames -passwdict /usr/share/wordlists/rockyou.txt -l /home/myuser/file.log -restore .MyDomain.com:8000.session


```

# Buy me a 🍺 / ☕

<a href="https://www.buymeacoffee.com/n3bojs4z" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
