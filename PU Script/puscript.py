## TODO
## Implement better security for pw
## Refactor code - decompose into classes
## Implement options
## Create README

## README
## Please try to pay it forward
## Created so that you can benefit
## Do things so that others can benefit
## Kudos

## DISCLAIMER:
## Script is provided as is
## Use at your own risk

import mechanize
import smtplib
import time, threading
from bs4 import BeautifulSoup

details = {}
subscribers = []

def foo(): ## change to decorator
    ## surround in try -except
    try:
        bar()
    except:
        print "Error occured - PU site down?"
    threading.Timer(600, foo).start()

def bar():
    print time.asctime(time.localtime())
    print "Checking for notices"
    ## Have to use try except clauses
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
            notice = notice[:3] + notice[-2:]
            notice_num = int(notice[0])
            if notice_num > last_notice_read:
                new_last_notice_read = max(new_last_notice_read, notice_num)
                notices += [notice]
            notice = []
        if len(notice) == 4:
            l.a['href'] = "http://pu/"+l.a['href']
            notice += [str(l.a)]
        else:
            notice += [l.text] ##str?
    notice = notice[:3] + notice[-2:]
    notice_num = int(notice[0])
    if notice_num > last_notice_read:
        new_last_notice_read = max(new_last_notice_read, notice_num)
        notices += [notice]
    notice = []

    if len(notices) > 0:
        print "New notice found"
        ## CREDIT: http://segfault.in/2010/12/sending-gmail-from-python/
        SMTP_SERVER = 'smtp.gmail.com'
        SMTP_PORT = 587
         
        email_sender = details["From"]
        email_password = details["GmailPassword"]
        recipients = subscribers
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo
        session.login(email_sender, email_password)
        for n in notices:
            n = map(str, n)
            n_SMS = n[:3] + n[-1:]
            subject = " ".join(n_SMS)
            body = " ".join(n)
            for recipient in recipients:
                headers = ["From: " + email_sender,
                           "Subject: " + subject,
                           "To: " + recipient,
                           "MIME-Version: 1.0",
                           "Content-Type: text/html"]
                headers = "\r\n".join(headers)
                session.sendmail(email_sender, recipient, headers + "\r\n\r\n" + body)
        session.quit()
        print "Mail Sent!"
        details["LastNoticeRead"] = str(new_last_notice_read)
        f = open('details.txt', 'w')
        for item in details:
            f.write(item + ": " + details[item] + "\n")
        f.close()
        print "Details written"
    else:
        print "No new notices"
    print "Will check again in 10 minutes"
    ## To send SMS: http://techawakening.org/free-sms-alerts-new-email-on-gmail-with-google-docs/1130/

def get_details():
    global subscribers ## REFACTOR
    f = open('details.txt', 'r')
    for line in f:
        data = line.split(':')
        details[data[0].strip()] = data[1].strip()  ##str?
    f.close()
    f = open('subscribers.txt', 'r')
    for line in f:
        subscribers += [line.strip()] ##str?
    f.close()

get_details()
foo()
