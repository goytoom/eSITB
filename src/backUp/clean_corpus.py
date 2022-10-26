# ##import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# from pprint import pprint

#Gensim
# import little_mallet_wrapper as lmw
from gensim.models import CoherenceModel
from gensim.models.ldamulticore import LdaMulticore
import gensim.corpora as corpora

#lda vis
import pyLDAvis
import pyLDAvis.gensim_models
import pyLDAvis.gensim_models as gensimvis

import os
from pathlib import Path
import sys
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import pickle 
from collections import defaultdict
from itertools import chain

mode = int(sys.argv[1])
text_types = ["posts", "comments", "all"]
text_type = text_types[mode-1]

""" Import Data """

#import corpora/lemmas etc.
#remove new stop words
#remove rare/too frequent words
#save files

with open('../data/auxiliary/lemma_' + text_type + '.pkl',  'rb') as f:
    lemma = pickle.load(f)
    
#clean:
remove_words = set(["'re", "'ve", "'s", "'m", "'", "'d", "’", "’d", "’ve", "’re", "’s", "’m"])
lemma = [[token for token in tokens if token not in remove_words] for tokens in lemma]

# #dictionary
id2word = corpora.Dictionary(lemma)
id2word.filter_extremes(no_below=20, no_above=0.3)

#dicts
with open('../data/auxiliary/dict_' + text_type + '.pkl', 'wb') as f:
    pickle.dump(id2word, f)

keep_tokens = set(list(id2word.values()))

#update tokens
lemma = [[token for token in tokens if token in keep_tokens] for tokens in lemma]

#lemma
with open('../data/auxiliary/lemma_' + text_type + '.pkl', 'wb') as f:
    pickle.dump(lemma, f)

# Create Corpus
# Term Document Frequency
corpus = [id2word.doc2bow(text) for text in lemma]

#save corpus
with open('../data/auxiliary/corpus_' + text_type + '.pkl', 'wb') as f:
    pickle.dump(corpus, f)
