import urllib2
import re
from bs4 import BeautifulSoup

comp = 'pl'
filemode = 'w'
if comp == 'pl':
    my_url = "http://www.bbc.co.uk/sport/football/premier-league/results"
    my_file = 'static/files/plfixturepage.txt'
elif comp == 'ucl':
    my_url = "http://www.bbc.co.uk/sport/football/champions-league/fixtures"
    my_file = 'static/files/uclfixturepage.txt'
else:
    print "ERROR"
    exit()

if filemode=='w':
    webpage = urllib2.urlopen(my_url).read()

    ##with open(my_file,filemode) as the_file:
        ##the_file.write(webpage)

else:
    with open(my_file,filemode) as the_file:
        webpage = the_file.read()
    
soup = BeautifulSoup(webpage)
matches = soup.find_all("td","match-details")
for l in matches:
    score = l("abbr")
    if score:
        score = score[0].text.strip()
    else:
        score = "no score"
    time = l.find_next_sibling("td")
    when = l.find_previous("h2","table-header").text.strip()
    status = time.text.strip()
    time = time.text.strip()
    if status == 'Full time':
        print l("span","team-home")[0].text.strip() + " versus " + l("span","team-away")[0].text.strip()
        print "AT " + time + " ON " + when
        print "SCORE WAS: " + score
        print
