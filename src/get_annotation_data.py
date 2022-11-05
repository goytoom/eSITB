# -*- coding: utf-8 -*-
"""
Created on Wed May 25 13:08:24 2022

@author: suhai
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

""" Functions """

def preprocessing(df, col):
    df          = df[~df[col].isnull()]
    texts       = df[col].values.flatten()                                              #get all the section texts (discard listings without)
    texts       = [re.sub("\n", " ", x.lower()) for x in texts]                         #remove line break and get lower case
    texts       = [re.sub(r"(?P<url>http[s]?:\/\/[^\s]+)", "", x) for x in texts]       #remove url  (with https)
    texts       = [re.sub(r"(?P<url>www.[^\s]+)", "", x) for x in texts]                #remove url  (without https)
    texts       = [re.sub(r'[\w\.-]+@[\w\.-]+', "", x) for x in texts]                  #replace emails 
    texts       = [re.sub(r'-(?!\w)|(?<!\w)-', '', x) for x in texts]                   #remove hyphen except within words
    texts       = [re.sub(r'[,\.!?():]', '', x) for x in texts]                             #remove punctuation
    texts       = [re.sub(r'\[deleted\]', '', x) for x in texts] 
    texts       = [re.sub(r'\[removed\]', '', x) for x in texts] 

    empty_idx   = [i for i,x in enumerate(texts) if (not x or len(x.split(" ")) < 4)] #find empty posts (or less than 4 words)
    for idx in empty_idx[::-1]:
        del texts[idx] #remove from texts
        
    idx = np.delete(df.index. values, empty_idx)
    
    if idx.size != df.shape[0]: #if there are empty rows, remove them
        df = df.iloc[idx,:]
    df["cleaned_text"] = texts
    
    return df #return dataframe with processed texts

# auxiliaryiliary functions       
def lemmatizing(sentences, allowed_postags=set(['NOUN', 'ADJ', 'VERB', 'ADV']), n_process = 2, batch_size = 64):
    for doc in nlp.pipe(sentences, batch_size=batch_size, n_process=n_process, disable=['ner', "parser"]):
        yield [token.lemma_ for token in doc if (token.pos_ in allowed_postags and token.lemma_.lower() not in stop_words)]

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

""" Corpora """
allowed_postags = set(['NOUN', 'ADJ', 'VERB', 'ADV'])
files = ["posts", "comments"]

data = df.cleaned_text.values.tolist()
words = [" ".join([token for token in tokens.split() if token not in stop_words]) for tokens in data]
lemmatized = list(lemmatizing(words, allowed_postags=allowed_postags, n_process=int(CPU_CORES/2)-1, batch_size=64)) # includes remove stopwords

#create dictionary and filter extreme words (in too many docs or in too few)    
id2word = corpora.Dictionary(lemmatized)
id2word.filter_extremes(no_above=0.5, no_below=20)

keep_tokens = set(list(id2word.values())) #creat set of tokens that are in the dictionary

#dicts
with open('../data/auxiliary/dict_' + files[mode-1] + '.pkl', 'wb') as f:
pickle.dump(id2word, f)

lemmatized = [[token for token in tokens if token in keep_tokens] for tokens in lemmatized] #filter out extreme words from corpus

with open('../data/auxiliary/lemma_' + files[mode-1] + '.pkl', 'wb') as f:
    pickle.dump(lemmatized, f)

# Create Corpus
# Term Document Frequency
corpus = [id2word.doc2bow(text) for text in lemmatized]

#save corpus
with open('../data/auxiliary/corpus_' + files[mode-1] + '.pkl', 'wb') as f:
pickle.dump(corpus, f)


















