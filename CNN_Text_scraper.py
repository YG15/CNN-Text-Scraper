##########################################
# Name:  CNN Text Scraper
# Target : Accessing and processing data from the CNN Transcripts site for a given range of dates
# Parameters : days, months and years of start day and end day, "automated" if False,
#              the script run as an example without taking dates parameters
# Returning: A dictionary containing all the processed transcript from the CNN between the date range
# Author: Yonathan Guttel <yesguttel@gmail.com>
# Date: 26.01.2018
# Version: 1
###########################################

# Packages
from bs4 import BeautifulSoup
import re
import requests
import numpy as np
from datetime import date, timedelta
import urllib.request
from tqdm import tqdm



# The function recieve a URL (as string) and return all the children pages URL which includes transcript
def getURL(url):
    # correct url in case "http" wasn't entered as part of it
    if url.startswith("http"):
        pass
    else:
        url = ("http://" +url)
    resp = urllib.request.urlopen(url)
    mega_soup = BeautifulSoup(resp, "html5lib")
    urls = []
    #collected all suitable url in the webpage in the list "urls"
    for link in mega_soup.find_all('a', href=True):
        # Transcripts web page starts with:
        # "http://transcripts.cnn.com/TRANSCRIPTS/" and have an additional part afterwood
        if (link['href'].startswith("/TRANSCRIPTS/") and len(link['href']) > 13) == True:
            urls.append("http://transcripts.cnn.com" + link['href'])
    return (urls)

# the function collct the text from a given url and process it to remove
# names of speaker, remark on the transcript and unnessecary charchters
def text_scraper(url):
    if url.startswith("http"):
        r= requests.get(url)
    else:
        r  = requests.get("http://" +url)
    data = urllib.request.urlopen(url)
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
    #returning clean text
    return (final_text)

# The function recieves dates and use the function above to output a dictionary of processed texts
def all_dates_range_texts(automated):
    print("This is a CNN transcripts web text scraper, please enter the date from which you want to draw text from...")
    if automated == True:
        year_start = input("Enter the year to start from from [4 digits]: ")
        month_start = input("Enter the month to start from from [2 digits]: ")
        day_start = input("Enter the day to start from from [2 digits]: ")
        year_end = input("Enter the year to stop at [4 digits]: ")
        month_end = input("Enter the month to stop at [2 digits]: ")
        day_end = input("Enter the day to stop at [2 digits]: ")
    else:
        print("example case presented dates between 24.01.2018 to 24.01.2018")
        year_start = 2018
        year_end = 2018
        month_start = 1
        month_end = 1
        day_start = 24
        day_end = 24

    start_date = date(int(year_start), int(month_start), int(day_start))
    end_date = date(int(year_end), int(month_end), int(day_end))
    delta = end_date - start_date  # timedelta
    days_list = []
    for i in range(delta.days + 1):
        days_list.append((start_date + timedelta(days=i)).strftime("%Y.%m.%d"))

    all_urls = []
    for day in days_list:
        day_url = ("http://transcripts.cnn.com/TRANSCRIPTS//" + day + ".html")
        day_child_urls = getURL(day_url)
        all_urls.extend(day_child_urls)

    text_dic={}
    print ("Please wait while processing request....")
    for url in tqdm(all_urls):
        text_dic [str(url)] = text_scraper(url)
    return (text_dic)

if __name__ == "__main__":

    automated = True

    #run the script
    text_dic = all_dates_range_texts(automated)
    #checking if it worked on a sample
    print(next (iter (text_dic.values())))

