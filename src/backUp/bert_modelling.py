# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 21:39:08 2022

@author: suhai
"""

""" Import Packages """
import numpy as np
import pandas as pd
import sys
import os
from pathlib import Path

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer

""" Set configuration """
mode = int(sys.argv[1])
text_types = ["posts", "comments", "all"]
text_type = text_types[mode-1]
cluster_sizes = {"posts": 14, "comments": 18, "all": 22} #take from best LDA
cluster_size = cluster_sizes[text_type]

""" Load Data """
Path("../data/auxiliary/bertopic/").mkdir(exist_ok=True, parents=True)
Path("../data/results/bertopic/").mkdir(exist_ok=True, parents=True)

if mode!=3:
    df_moral = pd.read_csv("../data/results/all_" + text_type + "_full.csv", keep_default_na=False, lineterminator="\n")
    docs = df_moral["text"].tolist()
else:
    df_moral_p = pd.read_csv("../data/results/all_posts_full.csv", keep_default_na=False, lineterminator="\n")
    df_moral_c = pd.read_csv("../data/results/all_comments_full.csv", keep_default_na=False, lineterminator="\n")
    posts = df_moral_p["text"].tolist()
    comments = df_moral_c["text"].tolist()
    docs = posts + comments

""" Pre-train and save embeddings """

embeddings_path = "../data/auxiliary/bertopic/embeddings_" + text_type + ".npy"

if not os.path.isfile(embeddings_path):
    if mode == 3 and os.path.isfile("../data/auxiliary/bertopic/embeddings_posts.npy") and os.path.isfile("../data/auxiliary/bertopic/embeddings_comments.npy"):
        embeddings_p = np.load("../data/auxiliary/bertopic/embeddings_posts.npy")
        embeddings_c = np.load("../data/auxiliary/bertopic/embeddings_comments.npy")
        embeddings = np.vstack([embeddings_p, embeddings_c])
        np.save(embeddings_path, embeddings)
    else:
        sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = sentence_model.encode(docs, show_progress_bar=False)
        np.save(embeddings_path, embeddings)
    
else:
    embeddings = np.load(embeddings_path)
        
""" Set parameters and fit model """

# create two models:
    # fixed n
    # auto + min size
bertopic_path = "../data/auxiliary/bertopic/" + text_type

if not os.path.isfile(bertopic_path + "_" + str(cluster_size)):
    vectorizer_model = CountVectorizer(ngram_range=(1, 2), stop_words="english", min_df=10, max_df=1.0)
    topic_model = BERTopic(vectorizer_model=vectorizer_model, nr_topics=cluster_size)
    topics, probs = topic_model.fit_transform(docs, embeddings)
    hierarchical_topics = topic_model.hierarchical_topics(docs, topics)
    nr_topics = len(topic_model.get_topic_freq())
    
    #Save models    
    topic_model.save(bertopic_path + "_" + str(cluster_size))
    np.save(bertopic_path + "_topics_" + str(cluster_size) + ".npy", topics)
    np.save(bertopic_path + "_probs_" + str(cluster_size) + ".npy", probs)
    np.save(bertopic_path + "_hierarchy_" + str(cluster_size) + ".npy", hierarchical_topics)
    
else:
    """ Re-load trained model """
    topic_model = BERTopic.load(bertopic_path + "_" + str(cluster_size))
    topics = np.load(bertopic_path + "_topics_" + str(cluster_size) + ".npy")
    probs = np.load(bertopic_path + "_probs_" + str(cluster_size) + ".npy")
    hierarchical_topics = np.load(bertopic_path + "_hierarchy_" + str(cluster_size) + ".npy")
    
""" Merge Topics with texts """

if mode!=3:
    df_moral["topics"] = topics
    df_moral.to_csv("../data/results/bertopic/merged_" + text_type + "_" + str(cluster_size) + "_full.csv")
else:
    #alternative: fit then predict for posts and comments separately
    pass
    df_moral = pd.concat([df_moral_p, df_moral_c])
    df_moral["topics"] = topics
    df_moral.to_csv("../data/results/merged_" + text_type + "_" + str(cluster_size) + "_full.csv")
    

#drop outliers?
#df_moral[df_moral["topics"]!=-1]
    
""" Visualise Results """

visualise_path = "../data/results/bertopic/" + text_type

fig = topic_model.visualize_heatmap()
fig.write_html(visualise_path + "_topic_similarity_" + str(cluster_size) + ".html")

fig = topic_model.visualize_hierarchy()
fig.write_html(visualise_path + "_hierarchy_" + str(cluster_size) + ".html")

fig = topic_model.visualize_topics()
fig.write_html(visualise_path + "_topics_" + str(cluster_size) + ".html")

fig = topic_model.visualize_term_rank()
fig.write_html(visualise_path + "_score_decline_" + str(cluster_size) + ".html")


"""Fit model with auto parameters """
if not os.path.isfile(text_type):
    vectorizer_model = CountVectorizer(ngram_range=(1, 2), stop_words="english", min_df=25, max_df=1.0)
    topic_model = BERTopic(vectorizer_model=vectorizer_model, min_topic_size=20, nr_topics="auto")
    topics, probs = topic_model.fit_transform(docs, embeddings)
    hierarchical_topics = topic_model.hierarchical_topics(docs, topics)
    nr_topics = len(topic_model.get_topic_freq())
    
    #Save models    
    topic_model.save(bertopic_path)
    np.save(bertopic_path + "_topics.npy", topics)
    np.save(bertopic_path + "_probs.npy", probs)
    np.save(bertopic_path + "_hierarchy.npy", hierarchical_topics)
else:
    topic_model = BERTopic.load(bertopic_path)
    topics = np.load(bertopic_path + "_topics.npy")
    probs = np.load(bertopic_path + "_probs.npy")
    hierarchical_topics = np.load(bertopic_path + "_hierarchy.npy")

""" Merge Topics with texts """

if mode!=3:
    df_moral["topics"] = topics
    df_moral.to_csv("../data/results/bertopic/merged_" + text_type + "_full.csv")
else:
    #alternative: fit then predict for posts and comments separately
    pass
    df_moral = pd.concat([df_moral_p, df_moral_c])
    df_moral["topics"] = topics
    df_moral.to_csv("../data/results/merged_" + text_type + "_full.csv")

""" Visualise Results """

fig = topic_model.visualize_heatmap()
fig.write_html(visualise_path + "_topic_similarity.html")

fig = topic_model.visualize_hierarchy()
fig.write_html(visualise_path + "_hierarchy.html")

fig = topic_model.visualize_topics()
fig.write_html(visualise_path + "_topics.html")

fig = topic_model.visualize_term_rank()
fig.write_html(visualise_path + "_score_decline.html")













