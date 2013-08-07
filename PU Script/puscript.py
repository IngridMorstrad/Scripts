## TODO
## Try to send SMSes
## Refactor code
## Probably change file details
## Implement better security for pw

## README
## Please try to pay it forward
## Created so that you can benefit
## Do things so that others can benefit
## Kudos

## DISCLAIMER:
## Script is provided as is
## NO GUARANTEE ON SECURITY
## Your email COULD be compromised...
## Use at your own risk

import mechanize
import smtplib
import time, threading
from bs4 import BeautifulSoup

details = {}

def foo(): ## change to decorator
    bar()
    threading.Timer(600, foo).start()

def bar():
    print "Checking for notices"
    br = mechanize.Browser()
    my_url = "http://pu/index.php?option=login"
    br.open(my_url)
    br.select_form(name = 'formElem')
    username = details["PU_Username"]
    password = details["PU_Password"]
    br['username'] = username
    br['password'] = password
    br.submit()
    my_url = "http://pu/index.php?option=notices"
    r = br.open(my_url)
    webpage = br.response().read()
    soup = BeautifulSoup(webpage)
    matches = soup.find_all("td")
    notice = []
    last_notice_read = int(details["LastNoticeRead"])
    notices = []
    new_last_notice_read = last_notice_read
    for l in matches:
        if len(notice) == 6:
            notice = notice[:3]+notice[5:]
            if notice[0] > last_notice_read:
                new_last_notice_read = max(new_last_notice_read, notice[0])
                notices += [notice]
            notice = []
        if len(notice) == 0:
            notice += [int(l.text)]
        else:
            notice += [str(l.text)]

    notice = notice[:3]+notice[5:]
    if notice[0] > last_notice_read:
        new_last_notice_read = max(new_last_notice_read, notice[0])
        notices += [notice]

    if len(notices) > 0:
        print "New notice found"
        ## CREDIT: http://segfault.in/2010/12/sending-gmail-from-python/
        SMTP_SERVER = 'smtp.gmail.com'
        SMTP_PORT = 587
         
        email_sender = details["From"]
        email_password = details["GmailPassword"]
        recipient = details["From"]
        subject = 'New PU notice'
        body = ""
        for n in notices:
            body += " ".join(map(str,n))
            body += "<br>"
        headers = ["From: " + email_sender,
                   "Subject: " + subject,
                   "To: " + recipient,
                   "MIME-Version: 1.0",
                   "Content-Type: text/html"]
        headers = "\r\n".join(headers)
         
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
         
        session.ehlo()
        session.starttls()
        session.ehlo
        session.login(email_sender, email_password)
        
        session.sendmail(email_sender, recipient, headers + "\r\n\r\n" + body)
        session.quit()
        print "Mail Sent!"
        details["LastNoticeRead"] = str(new_last_notice_read)
        f = open('details.txt', 'w')
        for a in details:
            f.write(a + ": " + details[a] + "\n")
        print "Details written"
        print "Will check again in 10 minutes"

def get_details():
    f = open('details.txt', 'r')
    for line in f:
        data = line.split(':')
        details[str(data[0].strip())] = str(data[1].strip())
    print details
    f.close()

get_details()
foo()
