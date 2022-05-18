# for the twitter section
import tweepy
import os
import datetime
import re
from pprint import pprint

# for the lyrics scrape section
import requests
import time
from bs4 import BeautifulSoup
import shutil
from collections import defaultdict, Counter
from lxml import html
import random

def generate_filename_from_link(link) :
    if not link: return None
    # drop the http or https and the html
    name = link.replace("https","").replace("http","")
    name = link.replace(".html","")
    name = name.replace("/lyrics/","")
    # Replace useless chareacters with UNDERSCORE
    name = name.replace("://","").replace(".","_").replace("/","_")
    # tack on .txt
    name = name + ".txt"
    return(name)

artists = {
    'rihanna':"https://www.azlyrics.com/r/rihanna.html",
    'rema':"https://www.azlyrics.com/r/rema.html"
} 

# Let's set up a dictionary of lists to hold our links
print("Fetching Lyric Pages...")
lyrics_pages = defaultdict(list)
for artist, artist_page in artists.items() :
    # request the page and sleep
    r = requests.get(artist_page)
    webpage = html.fromstring(r.content)
    #get all the links in the artist page and slice out the links that are not necessary
    links = webpage.xpath('//a/@href')[31:-8]
    lyrics_pages[artist] = links
    time.sleep(5 + 10*random.random())


url_stub = "https://www.azlyrics.com" 
start = time.time()
total_pages = 0 


for artist in lyrics_pages:
    print(f"{artist}: {len(lyrics_pages[artist])}")


    # 1. Build a subfolder for the artist
    # if os.path.isdir(artist):
    #     shutil.rmtree(artist)

    if not os.path.isdir(artist): 
        os.mkdir("{}".format(artist))
    
    
    # 2. Iterate over the lyrics pages
    for i,link in enumerate(lyrics_pages[artist]):
        # 2.1 Prepare fileName for the current song
        fileName = generate_filename_from_link(link)
        print(fileName)
        filePath = os.path.join(artist, fileName)

        # 2.2 Skip song if we already scraped it in the past
        if os.path.isfile(filePath): continue;
        
        # 3. Request the lyrics page. 
        lyric_url = url_stub + link
        print("\t"+lyric_url)
        r = requests.get(lyric_url, timeout=5)
        soup = BeautifulSoup(r.content, 'html.parser')
        r.close()
        time.sleep(5 + 10*random.random()) # sleep after making the request

        # 4. Extract the title and lyrics from the page.
        titleelement=soup.findAll("title")
        song_title=soup.title.text.split("-")[1].split("|")[0].replace("Lyrics","").strip()
        start=soup.text.find(f'"{song_title}"')
        end=soup.text.find('Submit Corrections')
        

        # 5. Write out the title, two returns ('\n'), and the lyrics.
        with open(filePath, 'w') as f:
            f.write(song_title+'\n\n')
            for line in soup.text[start:end].split('\n')[11:]:
                f.write(line+'\n')
        f.close()
    
        # Remember to pull at least 20 songs per artist. It may be fun to pull all the songs for the artist
        if i>=21:
            break
