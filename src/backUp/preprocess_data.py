#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 12:58:35 2022

@author: sabdurah
"""

""" Libraries """
import pandas as pd
import os
from pathlib import Path
import re
import sys
import numpy as np
import pickle 

import gensim.corpora as corpora
from gensim.utils import simple_preprocess

import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
stop_words = stopwords.words('english')
stop_words.extend(["'", "'s", "'ve", "'m", "'d", "'re", "’re", "’ve", "’m", "’s", "’d", "’"])

import spacy
nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner', "textcat"])

import multiprocessing
CPU_CORES = multiprocessing.cpu_count()

# Create preprocessed files for comments and posts
# Use these files for:
    # Tokens for topic modelling
    # 

""" Functions """

def preprocessing(df, col):
    df          = df[~df[col].isnull()]
    texts       = df[col].values.flatten()                                              #get all the section texts (discard listings without)
    texts       = [re.sub("\n", " ", x.lower()) for x in texts]                         #remove line break and get lower case
    texts       = [re.sub(r"(?P<url>http[s]?:\/\/[^\s]+)", "", x) for x in texts]       #remove url (with https)
    texts       = [re.sub(r"(?P<url>www.[^\s]+)", "", x) for x in texts]                #remove url
    texts       = [re.sub(r'[\w\.-]+@[\w\.-]+', "", x) for x in texts]                  #remove emails
    texts       = [re.sub(r'-(?!\w)|(?<!\w)-', '', x) for x in texts]                   #remove hyphen except within words
    texts       = [re.sub(r'[,\.!?(){}:]', '', x) for x in texts]                       # remove punctuation
    texts       = [re.sub(r'\[delete\]', '', x) for x in texts] 
    texts       = [re.sub(r'\[removed\]', '', x) for x in texts] 

    empty_idx   = [i for i,x in enumerate(texts) if (not x or len(list(filter(None, x.split(" ")))) < 4)] #find empty posts (or less than 4 words), dont count empty strings
    for idx in empty_idx[::-1]:
        del texts[idx] #remove from texts
        
    idx = np.delete(df.index. values, empty_idx)
    
    if idx.size != df.shape[0]: #if there are empty rows, remove them
        df = df.iloc[idx,:]
    df["cleaned_text"] = texts
    
    return df #return dataframe with processed texts

""" Preprocess Data """

file_names = ["all_posts_processed.csv", "all_comments_processed.csv"]
Path("../data/auxiliary").mkdir(parents=True, exist_ok=True)

mode = int(sys.argv[1])

if mode == 1: #posts
    if not set(file_names[0]).issubset(set(os.listdir("../data/auxiliary/"))):
        ##LOAD DATA
        df_posts = pd.read_csv('../data/results/all_posts.csv', delimiter=',', encoding="utf-8", keep_default_na=False)
        df_posts["combined_text"] = df_posts["title"] + " " + df_posts["text"]
        posts = df_posts.loc[:,["id", "combined_text"]] #.sample(100).reset_index(drop=True)
        
        df = preprocessing(posts, "combined_text")
        df.to_csv("../data/auxiliary/all_posts_processed.csv", index=False)
        
    else:
        df = pd.read_csv("../data/auxiliary/all_posts_processed.csv", keep_default_na=False)
        
elif mode == 2:
    if not set(file_names[1]).issubset(set(os.listdir("../data/auxiliary/"))):
        ##LOAD DATA
        df_comments = pd.read_csv('../data/results/all_comments.csv', delimiter=',', encoding="utf-8", keep_default_na=False)
        comments    = df_comments.loc[:,["id", "text"]] #.sample(100).reset_index(drop=True)
        
        df = preprocessing(comments, "text")
        df.to_csv("../data/auxiliary/all_comments_processed.csv", index=False)
       
    else:
        df = pd.read_csv("../data/auxiliary/all_comments_processed.csv", keep_default_na=False)

else:
    pass





