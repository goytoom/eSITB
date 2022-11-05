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
import spacy

import multiprocessing
CPU_CORES = multiprocessing.cpu_count()

""" Corpora """
if set(["lemma_posts.pkl", "lemma_comments.pkl"]).issubset(set(os.listdir("../data/auxiliary/"))):
	# get all by combining other two:
	    # maybe put this in other file
	with open('../data/auxiliary/lemma_posts.pkl', 'rb') as f:
	    lemmatized_posts = pickle.load(f)
	    
	with open('../data/auxiliary/lemma_comments.pkl', 'rb') as f:
	    lemmatized_comments = pickle.load(f)
	    
	lemmatized_all = lemmatized_posts + lemmatized_comments

	with open('../data/auxiliary/lemma_all.pkl', 'wb') as f:
	    pickle.dump(lemmatized_all, f)

	# Create Dictionary
	id2word_all = corpora.Dictionary(lemmatized_all)

	with open('../data/auxiliary/dict_all.pkl', 'wb') as f:
	    pickle.dump(id2word_all, f)

	# Create Corpus
	# Term Document Frequency
	corpus_all = [id2word_all.doc2bow(text) for text in lemmatized_all]

	#corpus            
	with open('../data/auxiliary/corpus_all.pkl', 'wb') as f:
	    pickle.dump(corpus_all, f)
else:
	pass



















