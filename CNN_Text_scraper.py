##########################################
# Name:  CNN Text Scraper
# Target : Accessing and processing data from the CNN Transcripts site for a given range of dates
# Parameters : Start and end dates for the data collection.
#              The script can without receiving dates, and ask for if this happens.
#              option: set working directory
# Returning: A collection of .txt files, a file for each transcript page.
# Author: Yonathan Guttel <yesguttel@gmail.com>
# Date: 28.01.2018
# Version: 2
###########################################

# Packages
from bs4 import BeautifulSoup
import re
import os
import math
import requests
import numpy as np
from datetime import date, timedelta
import urllib.request
from tqdm import tqdm



# The function recieve a URL (as string) and yield all the children pages URL which includes transcript
def get_urls(url):
    # Correct url in case "http" wasn't entered as part of it
    if url.startswith("http"):
        pass
    else:
        url = ("http://" +url)
    resp = urllib.request.urlopen(url)
    mega_soup = BeautifulSoup(resp, "html5lib")
    for link in mega_soup.find_all('a', href=True):
        if (link['href'].startswith("/TRANSCRIPTS/") and len(link['href']) > 13) == True:
            yield("http://transcripts.cnn.com" + link['href'])


# The function collect the text from a given url and process it to remove
# names of speaker, remark on the transcript and unnecessary characters
def text_scraper(url):
    if url.startswith("http"):
        data = urllib.request.urlopen(url)
    else:
        data  = urllib.request.urlopen("http://" +url)
    soup = BeautifulSoup(data, "html5lib")
    #raw_text=soup.get_text(strip=True) # if we want full text, less useful
    #raw text as list of paragraphs:
    raw_text_list =[text for text in soup.stripped_strings]
    # finding the borders between the transcript to the edges who aren't part of the transcript
    start_string="THIS IS A RUSH TRANSCRIPT. THIS COPY MAY NOT BE IN ITS FINAL FORM AND MAY BE UPDATED."
    start_ind=raw_text_list.index(start_string)+1
    #finding the ending string which is the lasst string writtem all in capital letters
    ind = []
    for item in raw_text_list:
        ind.append((item.isupper()))
    indi = np.where(ind)
    end_string=[raw_text_list[i] for i in np.array(indi).tolist()[0]][-1]
    #find a line were only CAPITAL and charachters
    end_ind=len(raw_text_list) - 1 -raw_text_list[::-1].index(end_string)
    #croping the text acording to indecies
    cut_text=raw_text_list[start_ind:end_ind]
    # Cleaning the data
    final_text_list=[]
    for i in range(len(cut_text)):
        cut_text[i] = re.sub(r'[A-Z\W\d]*?(:)', '', cut_text[i])
        cut_text[i] = re.sub(r'([A-Z]){3,}', '', cut_text[i])
        cut_text[i] = re.sub(r'([\[\]\\\/\)\(])', '', cut_text[i])
        final_text_list.append(cut_text[i])
    final_text= ' '.join(final_text_list)
    # Returning clean text
    return (final_text)

# The function recieves two dates and yeilds the days between them
def get_days_in_range(start_date_s,end_date_s):
    # Checking if both dates suits the desireable formats
    cond1 = re.match(r'^(\d{4}\.\d{2}\.\d{2})', str(start_date_s))
    cond2 = re.match(r'^(\d{4}\.\d{2}\.\d{2})', str(end_date_s))
    # If not, it request the dates
    if not (cond1 or cond2):
        print("You haven't inputted date range ")
        start_date_s = input("Please enter the start date in format YYYY.MM.DD: ")
        end_date_s = input("Please enter the end date in format YYYY.MM.DD: ")
    # After dates are set, find and yield the days between them
    start_date = date(int(start_date_s[0:4]), int(start_date_s[5:7]), int(start_date_s[9:11]))
    end_date = date(int(end_date_s[0:4]), int(end_date_s[5:7]), int(end_date_s[9:11]))
    delta = end_date - start_date  # time delta
    for i in range(delta.days + 1):
        yield((start_date + timedelta(days=i)).strftime("%Y.%m.%d"))


# The function recieves dates and use the functions above to output a the texts of al transcripts
# in the date ranges, the file are kept as seperate txt file in the directory
def get_texts_in_range(start_date_s=math.nan,end_date_s=math.nan):
    days_list=get_days_in_range(start_date_s,end_date_s)
    print("Please wait while processing request....")
    for day in tqdm(days_list):
        day_url = ("http://transcripts.cnn.com/TRANSCRIPTS//" + day + ".html")
        urls = get_urls(day_url)
        for url in tqdm(urls):
            raw_title = re.search(r'TRANSCRIPTS\/(.*?)\.html',url).group(1)
            final_title = re.sub(r'([\/\.])', '_', raw_title)
            with open((str(final_title)+".txt"), "w") as f:
                f.write(text_scraper(url))


if __name__ == "__main__":

    """
    #The following part is only for people who uses the script without setting the wd before, It is not really needed
        # See which directory is the current directory to keep files
        print("The files will be saved in the folder: ", os.getcwd())
        answer =input("If you wish to continue please type Y, if you wish to change directory please type N ")
        # If needed, set new directory
        if answer !="Y":
            new_wd=input("please enter the path to the folder where the file should be saved: ")
            os.chdir(new_wd)
    """
    # Run the script
    # With  given dates
    #get_texts_in_range("2018.01.01","2018.01.01")

    # Without given dates
    get_texts_in_range()

