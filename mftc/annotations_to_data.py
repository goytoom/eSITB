# -*- coding: utf-8 -*-
"""
Created on Sun Jan 23 22:54:28 2022

@author: suhai
"""

# code to create csv files from mftc data
import pandas as pd
import ast
from collections import Counter

df = pd.read_csv("data/mftc_cleaned.csv", index_col = 0).drop_duplicates("tweet_id") #drop duplicates!

foundations_5 = ["care", "fairness", "loyalty", "authority", "purity", "non-moral"]
foundations_dict = {"harm": "care", "care": "care", "degradation": "purity", 
                    "purity": "purity", "betrayal": "loyalty", "loyalty": "loyalty", 
                    "subversion": "authority", "authority": "authority",
                    "cheating": "fairness", "fairness": "fairness", "non-moral": "non-moral"}

# find majority vote of annotators:
    
# create raw dataframe
df2 = df.iloc[:, :3].copy().reset_index(drop = True)

# transform anntotations to list of dicts
df2.annotations = df2.annotations.apply(lambda x: ast.literal_eval(x))

# transform to list of moral foundations (combine vices/virtues)
df2["cleaned_annotations"] = df2.annotations.apply(lambda x: list(
                                                                 [a for l in x for a in set(map(foundations_dict.get, l["annotation"].split(",")))]))
# get number of  annotators
df2["nr_annotators"] = df2.annotations.apply(lambda x: len([l["annotator"] for l in x]))

for foundation in foundations_5:
    df2[foundation] = df2.apply(lambda x: 1 if x["cleaned_annotations"].count(foundation)/x["nr_annotators"] >= 0.5 else 0, axis = 1)

#only count something as non-moral if its the most frequent annotation
df2["non-moral"] = df2.apply(lambda x: 1 if all([Counter(x["cleaned_annotations"])["non-moral"] > value for key, value in Counter(x["cleaned_annotations"]).items() if key != "non-moral"]) else 0, axis = 1)

# #if no foundation has required annotations (majority) count as non-moral
# df2["non-moral"] = df2.apply(lambda x: 1 if all([value/x["nr_annotators"] < 0.5 for value in Counter(x["cleaned_annotations"]).values()]) else x["non-moral"], axis = 1)

df2.to_csv("data/mftc_cleaned_combined.csv")