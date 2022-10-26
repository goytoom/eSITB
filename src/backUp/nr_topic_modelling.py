# ##import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# from pprint import pprint

#Gensim
# import little_mallet_wrapper as lmw
from gensim.models import CoherenceModel
from gensim.models.ldamulticore import LdaMulticore

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

""" Set Mode """
mode = int(sys.argv[1])
#os.environ["mallet_home"] = r"D:\USC\Research\self-injury\data\auxiliary\mallet-2.0.8"
#path_to_mallet  = r"D:\USC\Research\self-injury\data\auxiliary\mallet-2.0.8\bin\mallet"
#output_directory_path = r"D:/USC/Research/self-injury/data/results/lmw_output"

#check mallet implementation -> how to incorporate into workflow?

""" Functions """
def format_topics_sentences(ldamodel, corpus, texts, ids):
    # Init output
    sent_topics_df = pd.DataFrame()
    # Get main topic in each document
    for i, row in enumerate(ldamodel[corpus]):
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        # Get the Dominant topic, Perc Contribution and Keywords for each document
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:  # => dominant topic
                wp = ldamodel.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wp])
                sent_topics_df = pd.concat([sent_topics_df, pd.DataFrame([int(topic_num), round(prop_topic,4), topic_keywords]).T], axis=0, ignore_index=True)
            else:
                break
    sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']

    # Add original text to the end of the output
    ids = pd.Series(ids)
    contents = pd.Series(texts)
    sent_topics_df = pd.concat([sent_topics_df, contents, ids], axis=1)
    return(sent_topics_df)

""" Import Data """
text_types = ["posts", "comments", "all"]
text_type = text_types[mode-1]

print("Load corpora")
#lemma
with open('../data/auxiliary/lemma_' + text_type + '_removed.pkl',  'rb') as f:
    lemma = pickle.load(f)
    
#corpus
with open('../data/auxiliary/corpus_' + text_type + '_removed.pkl',  'rb') as f:
    corpus = pickle.load(f)
    
#dicts
with open('../data/auxiliary/dict_' + text_type + '_removed.pkl',  'rb') as f:
    id2word = pickle.load(f)

print("Load data")
if mode == 1:
    df = pd.read_csv("../data/auxiliary/all_posts_processed.csv", keep_default_na=False, lineterminator="\n")
    df["text_type"] = text_type
    texts       = df.combined_text.tolist() #.sample(100).reset_index(drop=True)
    ids = df["id"].tolist()
elif mode == 2:
    df = pd.read_csv("../data/auxiliary/all_comments_processed.csv", keep_default_na=False, lineterminator = "\n")
    df["text_type"] = text_type
    texts    = df.text.tolist()
    ids = df["id"].tolist()
else:
    df_posts = pd.read_csv("../data/auxiliary/all_posts_processed.csv", keep_default_na=False, lineterminator = "\n")
    df_posts["text_type"] = text_type
    df_comments = pd.read_csv("../data/auxiliary/all_comments_processed.csv", keep_default_na=False, lineterminator = "\n")
    df_comments["text_type"] = text_type
    df = pd.concat([df_posts, df_comments], ignore_index=True)
    posts       = df_posts.combined_text
    comments    = df_comments.text
    texts = posts.tolist() + comments.tolist()
    ids = df["id"].tolist()

""" Model Evaluation/Comparison """
Path("../data/images").mkdir(exist_ok=True, parents=True)
Path("../data/auxiliary/pylda").mkdir(exist_ok=True, parents=True)
#Path("../data/results/lmw_output").mkdir(exist_ok=True, parents=True)

opt_nrs = {"posts": 14, "comments": 22, "all": 22} #all: {10, 22, 26}, #comments: {18, 22}, #posts: {10,14,22}
opt_nr = opt_nrs[text_type]

if not os.path.isfile("../data/results/model_" + text_type + "_" + str(opt_nr) + ".pkl"):
    print("Fit Model")
    if mode == 1:
        passes = 5
        iterations = 250
    else:
        passes = 2
        iterations = 50
        
    model=LdaMulticore(corpus=corpus, id2word=id2word, num_topics=opt_nr, alpha="asymmetric", chunksize=10000, random_state=0, iterations=iterations, passes=passes, workers=4)
    coherencemodel = CoherenceModel(model=model, texts=lemma, coherence='c_npmi')
    coherence_score = coherencemodel.get_coherence()

    with open("../data/results/coherence_score_" + text_type + "_" + str(opt_nr) + ".pkl", "wb") as f:
        pickle.dump(coherence_score, f)
        
    with open("../data/results/ldamodel_" + text_type + "_" + str(opt_nr) + ".pkl", "wb") as f:
        pickle.dump(model, f)
else:
    with open("../data/results/ldamodel_" + text_type + "_" + str(opt_nr) + ".pkl", "rb") as f:
           model = pickle.load(f)

    with open("../data/results/coherence_score_" + text_type + "_" + str(opt_nr) + ".pkl", "rb") as f:
            coherence_score = pickle.load(f)
           
print("Coherence score: " + str(round(coherence_score, 3)))
            
# # Print the coherence scores
# for m, u_mass in zip(x, coherence_values):
#     print("Num Topics =", m, " has Coherence Value of", round(u_mass, 4))
    
""" Visualize the topics (interactive) """
file_paths = ['../data/auxiliary/pylda/ldavis_posts_' + str(opt_nr), 
              '../data/auxiliary/pylda/ldavis_comments_' + str(opt_nr),
              '../data/auxiliary/pylda/ldavis_all_' + str(opt_nr)]

#posts
# pyLDAvis.enable_notebook()
LDAvis_data_filepath = os.path.join(file_paths[mode-1])
if not os.path.isfile(LDAvis_data_filepath + ".html"):
    print("Create pyLDA")
    LDAvis_prepared = gensimvis.prepare(model, corpus, id2word, mds='mmds')
    with open(LDAvis_data_filepath, 'wb') as f:
        pickle.dump(LDAvis_prepared, f)
    # load the pre-prepared pyLDAvis data from disk
    with open(LDAvis_data_filepath, 'rb') as f:
        LDAvis_prepared = pickle.load(f)
    pyLDAvis.save_html(LDAvis_prepared, LDAvis_data_filepath + '.html')



#apply model on texts, adjust based on best score
print("Get topics for each doc")
if not os.path.isfile("../data/auxiliary/df_sent_" + text_type + "_" + str(opt_nr) + ".csv"):
    df_topic_sents_keywords = format_topics_sentences(ldamodel=model, corpus=corpus, texts=texts, ids=ids)
    df_topic_sents_keywords.to_csv("../data/auxiliary/df_sent_" + text_type + "_" + str(opt_nr) + ".csv", index=False)

    # Format
    df_dominant_topic = df_topic_sents_keywords.reset_index()
    df_dominant_topic.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords', 'Text', 'Id']

    #save new dataframe:
    df_dominant_topic.to_csv("../data/results/topics_" + text_type + "_" + str(opt_nr) + ".csv", index = False)
else:
    df_topic_sents_keywords = pd.read_csv("../data/auxiliary/df_sent_" + text_type + "_" + str(opt_nr) + ".csv", lineterminator="\n")

    # Format
    df_dominant_topic = df_topic_sents_keywords.reset_index()
    df_dominant_topic.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords', 'Text', 'Id']
    
    #save new dataframe:
    df_dominant_topic.to_csv("../data/results/topics_" + text_type + "_" + str(opt_nr) + ".csv", index = False) 

""" Meta-analysis - Topic distributions """
#Find most representative docs
if not os.path.isfile("../data/results"):
    print("Get typical docs")
    sent_topics_sorteddf = pd.DataFrame()
    sent_topics_outdf_grpd = df_topic_sents_keywords.groupby('Dominant_Topic')

    for i, grp in sent_topics_outdf_grpd:
        sent_topics_sorteddf = pd.concat([sent_topics_sorteddf, 
                                                 grp.sort_values(['Perc_Contribution'], ascending=[0]).head(1)], 
                                                axis=0)
    # Reset Index    
    sent_topics_sorteddf.reset_index(drop=True, inplace=True)
    # Format
    sent_topics_sorteddf.columns = ['Topic_Num', "Topic_Perc_Contrib", "Keywords", "Text", 'Id']

    # Save file
    sent_topics_sorteddf.to_csv("../data/results/typical_docs_" + text_type + "_" + str(opt_nr) + ".csv", index = False)
else:
    pass

##Get topic distribution
# Number of Documents for Each Topic
if not os.path.isfile("../data/results/topic_distribution_" + text_type + "_" + str(opt_nr) + ".csv"):
    print("Get topic distribution")
    topic_counts = df_topic_sents_keywords['Dominant_Topic'].value_counts()
    # Percentage of Documents for Each Topic
    topic_contribution = round(topic_counts/topic_counts.sum(), 4)
    # Topic Number and Keywords
    topic_num_keywords = df_topic_sents_keywords[['Dominant_Topic', 'Topic_Keywords']].drop_duplicates().reset_index(drop=True)
    # Concatenate Column wise
    df_dominant_topics = pd.concat([topic_num_keywords, topic_counts, topic_contribution], axis=1)
    # Change Column names
    df_dominant_topics.columns = ['Dominant_Topic', 'Topic_Keywords', 'Num_Documents', 'Perc_Documents']

    # Save file
    df_dominant_topics.to_csv("../data/results/topic_distribution_" + text_type + "_" + str(opt_nr) + ".csv", index = False)
else:
    pass



















