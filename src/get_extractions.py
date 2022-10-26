# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 13:19:18 2021

@author: suhai
"""

"""
Find the submissions from the list of conflicts (Kumar et al., 2018) in the pushshift data
Find the comments under the respective submissions in the pushshift data
Save the results in jsons
"""


import pandas as pd
import json 

import time
import os
from pathlib import Path
import sys

import zstandard as zstd
import lzma
from bz2 import BZ2File as bzopen

def getDumpComments(ids):  #fetches all comments from a dict of post ids
    folder = "../../status_raw/data/pushshift/comments/"
    comments = []
    
    #divide the folder into ranges for parallel processing
    nr_files = len(os.listdir(folder))
    chunk_size = int(nr_files/cluster_size) + (nr_files %cluster_size > 0)
    
    #change id check to subreddit name check!
    for filename in os.listdir(folder)[chunk_size*(time_range-1):chunk_size*(time_range)]:  #iterate over all files
        t = time.time()
        print("looking at: " + filename)
        if filename.endswith(".bz2"):                                                               #bz2 file support
             with bzopen(folder+filename, "r") as bzfin:                                            #open bz2 file
                try:                                                                                #in case file is corrupted at some point
                    for i, line in enumerate(bzfin):                                                #iterate over json
                        json_l = json.loads(line.rstrip().decode('utf8'))
                        if json_l.get("subreddit", "failedExtraction").split("_")[-1].lower() in ids:         #look for id
                            comments.append(json_l)
                except:
                    with open('logs/error_report.txt', 'a') as f:
                        f.write(filename + " at line: " + str(i) + '\n')
                    print('corruption at line: ' + str(i))

        #xz file support                
        elif filename.endswith(".xz"): 
             with lzma.open(folder+filename, "r") as bzfin:                                         #open xz file
                try:                                                                                #in case file is corrupted at some point
                    for i, line in enumerate(bzfin):                                                #iterate over json
                        json_l = json.loads(line.rstrip().decode('utf8'))
                        if json_l.get("subreddit", "failedExtraction").split("_")[-1].lower() in ids:         #look for id
                            comments.append(json_l)
                except:
                    with open('logs/error_report.txt', 'a') as f:
                        f.write(filename + " at line: " + str(i) + '\n')
                    print('corruption at line: ' + str(i))

        #zst file support
        if filename.endswith(".zst"):                                                               #open zst file
            with open(folder+filename, 'rb') as file_handle:
                buffer = ''
                reader = zstd.ZstdDecompressor(max_window_size=2**31).stream_reader(file_handle)    #2gb window
                while True:                                                                         #go through file in chunks
                    try:
                        chunk = reader.read(2**27).decode()                                         #128mb chunks, decode as utf-8
                    except: #in case chunk is compromised -> error message and move to next file
                        with open('logs/error_report.txt', 'a') as f:
                            f.write(filename + " while reading chunk\n")
                        break
                    if not chunk:
                        break
                    lines = (buffer + chunk).split("\n")                                            #get lines, buffer for first line
      
                    for i, line in enumerate(lines[:-1]):                                           #iterate over lines
                        json_l = json.loads(line)                                                   #read line as json
                        if json_l.get("subreddit", "failedExtraction").split("_")[-1].lower() in ids:         #look for id
                            comments.append(json_l)
                            
                    buffer = lines[-1]
                reader.close()

        print("time for one month comments: " + str(round(time.time() - t, 3)))
    if not comments:                    #if no match, return empty dict
        comments = [{'data': []}] 
    return comments

def getDumpSubmission(ids): #fetches json output from reddit dumps for all post ids in a dict
    folder = "../../status_raw/data/pushshift/submissions/"
    submissions = []
    nr_files = len(os.listdir(folder))
    chunk_size = int(nr_files/cluster_size) + (nr_files %cluster_size > 0)
    
    for filename in os.listdir(folder)[chunk_size*(time_range-1):chunk_size*(time_range)]:      #iterate over all files
        t = time.time()
        print("looking at: " + filename)                                                        #show which archive is beeing searched
        
        #zst file support
        if filename.endswith(".zst"):                                                           #open zst file
            with open(folder+filename, 'rb') as file_handle:
                buffer = ''
                reader = zstd.ZstdDecompressor(max_window_size=2**31).stream_reader(file_handle)              #2gb window
                while True:                                                                     #go through file in chunks
                    try: #in case a chunk is corrupted
                        chunk = reader.read(2**27).decode()                                     #128mb chunks, decode as utf-8
                    except:
                        with open('logs/error_report.txt', 'a') as f:
                            f.write(filename + " while reading chunk\n")
                        break
                    if not chunk:
                        break
                    lines = (buffer + chunk).split("\n")                                        #get lines, buffer for first line
      
                    for i, line in enumerate(lines[:-1]):                                       #iterate over lines
                        json_l = json.loads(line)                                               #read line as json
                        if json_l.get("subreddit", "failedExtraction").split("_")[-1].lower() in ids:          #look for id
                            submissions.append(json_l)
          
                    buffer = lines[-1]
                reader.close()

        #bz2 file support
        elif filename.endswith(".bz2"):
             with bzopen(folder+filename, "rb") as bzfin:
                """ Handle lines here """
                try:
                    for i, line in enumerate(bzfin):                                        #iterate over json
                        # if i == 10000: break
                        json_l = json.loads(line.rstrip().decode('utf8'))
                        if json_l.get("subreddit", "failedExtraction").split("_")[-1].lower() in ids:      #look for id
                            submissions.append(json_l)
                except:                                                                     #in case file is corrupted at some point
                    with open('logs/error_report.txt', 'a') as f:
                        f.write(filename + " at line: " + str(i) + '\n')
                    print('corruption at line: ' + str(i))

        #xz file support              
        elif filename.endswith(".xz"): 
             with lzma.open(folder+filename, "r") as bzfin:
                """ Handle lines here """
                try:
                    for i, line in enumerate(bzfin):                            #iterate over json
                        json_l = json.loads(line.rstrip().decode('utf8'))
                        if json_l.get("subreddit", "failedExtraction").split("_")[-1].lower() in ids:     #look for id
                            submissions.append(json_l)
                except:
                    with open('logs/error_report.txt', 'a') as f:
                        f.write(filename + " at line: " + str(i) + '\n')
                    print('corruption at line: ' + str(i))

        print("time for one month submissions: " + str(round(time.time() - t, 3)))
    if not submissions:                    #if no match, return empty dict
        submissions = [{'data': []}] 
    return submissions

""" Constants """
# get arguments for time range
time_range = int(sys.argv[1])
cluster_size = 20

sub_names = ["selfharm", "suicidewatch"]        #get submission by ID using Pushshift API
sub_names = {x:False for x in sub_names}        #transform to dict

""" Data """

folder = "../data/extractions/"
Path(folder).mkdir(parents=True, exist_ok=True) #create folder for data files

#test on server with with 1 id and check time!
submissions =  getDumpSubmission(sub_names)
comments    =  getDumpComments(sub_names)

nrows_s = len(submissions)
print("sub: " + str(nrows_s)) #how many submissions found?
nrows_c = len(comments)
print("com: " + str(nrows_c))

#save in chunks of 1000 jsons (submissions) or 10,000 jsons (comments)
temp = []
chunk_size_s = 1000
chunk_size_c = 10000
chunk_sub = int(nrows_s/chunk_size_s) + (int(nrows_s) % chunk_size_s > 0)
chunk_com = int(nrows_c/chunk_size_c) + (int(nrows_c) % chunk_size_c > 0)

for i in range(chunk_sub):
    temp.append({"submissions": submissions[chunk_size_s*(i):chunk_size_s*(i+1)]})
    with open(folder + "submissions_" + str(time_range) + "_" + str(i+1) + ".csv", 'w') as outfile:
        json.dump(temp, outfile)
    #naming convention: data + job number + chunk number .csv
    temp = [] #clean out temp storage

temp = [] #clean out temp storage    
for i in range(chunk_com):
    temp.append({"comments": comments[chunk_size_c*(i):chunk_size_c*(i+1)]})
    with open(folder + "comments_" + str(time_range) + "_" + str(i+1) + ".csv", 'w') as outfile:
        json.dump(temp, outfile)
    #naming convention: data + job number + chunk number .csv
    temp = [] #clean out temp storage
