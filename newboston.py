## Script by Ashwin
## To use:
## Change my_url as required
## Go to the command line and type:
## python newboston.py > mypage.html
## Open mypage.html and all the videos are on one page
## NOTE: So many videos on one page may cause your system to function slowly, so it is recommended you press "Stop" on your browser to prevent complete loading.

import urllib2
import re
from bs4 import BeautifulSoup

my_url = "http://thenewboston.org/list.php?cat=6"
webpage = urllib2.urlopen(my_url).read()
    
soup = BeautifulSoup(webpage)
content_links = soup.find_all("a")
download_links = []
for l in content_links:
    if l['href'][0:5] == "watch":
        download_links += ["http://thenewboston.org/" + l['href']]

for link in download_links:
    webpage = urllib2.urlopen(link).read()
    soup = BeautifulSoup(webpage)
    page_links = soup.find_all("center")
    for yt_link in page_links:
        print yt_link
