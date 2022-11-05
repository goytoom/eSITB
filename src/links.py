# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 13:36:22 2021

@author: suhai
"""

"""
Collects links to reddit dumps from the pushshift website
Download can be made with aria2c command: aria2c -i links_target.txt (or other filenames)
"""


""" Libraries """
import requests
import time
from bs4 import BeautifulSoup
import argparse


""" Function """

def parse_args(): #get commandline arguments
    parser = argparse.ArgumentParser(description="Getting link ids for reddit dump downloads")
    parser.add_argument('--mode', type=str, default = "comments", help='Type of post ("submission" or "comment")')
    parser.add_argument('--start', type=str, default = "2014-01", help='Type of post ("submission" or "comment")')
    parser.add_argument('--end', type=str, default = "2021-01", help='Type of post ("submission" or "comment")')
    args=parser.parse_args()
    return args

def main():

    #get command line arguments
    args = parse_args()
    mode = args.mode
    start = args.start
    end = args.end
    
    #link to pushshift
    url = "https://files.pushshift.io/reddit/" + mode + "/" 
    
    #define time range
    start_time = time.strptime(start, "%Y-%m")
    end_time = time.strptime(end, "%Y-%m")

    #get data from website (filenames)
    page = requests.get(url).text
    soup = BeautifulSoup(page, features="html.parser")
    
    #define prefixes for comments and submissions
    if mode == "comments":
        prefix = "RC"
    else:
        prefix = "RS"
    
    #find filenames that fit criteria (comment/submission, time range)
    files_link_all = [node.get("href") for node in soup.find_all("a") if prefix in node.get("href").split("_")[0]]
    files_link     = set([url + file for file in files_link_all if (time.strptime(file.split("_")[1].split(".")[0], "%Y-%m") >= start_time) and (time.strptime(file.split("_")[1].split(".")[0], "%Y-%m")<=end_time)])

    #save in text file
    with open("../data/General/links_" + mode + ".txt", "w") as f:
        f.write("\n".join(files_link))
    return 0

if __name__ == "__main__":
    main()