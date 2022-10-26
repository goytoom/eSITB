# -*- coding: utf-8 -*-
"""
Created on Sun Oct 31 04:31:02 2021

@author: suhai
"""

import pandas as pd
from pymongo import MongoClient

from pathlib import Path

folder = "../data/results/"
Path(folder).mkdir(parents=True, exist_ok=True) #create folder for data files

client = MongoClient()
db  = client.selfharm

print("Gathering comments from data base...")
#get comment texts and score
comments = list(db.collection.aggregate(
    [# //De-normalized the nested array of cars
    {"$unwind": "$comments"},
    {"$group": { "_id": '$comments.id', "comm": {"$addToSet": {"text": '$comments.body', 
                                                               "score": "$comments.score", 
                                                               "parent": "$comments.link_id",
                                                               "user": "$comments.author",
                                                               "parent_com": "$comments.parent_id",
                                                               "time": "$comments.created_utc",
                                                               "subreddit": "$comments.subreddit"}}}},
    ],
    allowDiskUse=True
))

#get submission texts and score
print("Gathering submissions from data base...")
submissions = list(db.collection.aggregate(
    [# //De-normalized the nested array of cars
    {"$unwind": "$submissions"},
    {"$group": { "_id": '$submissions.id', "sub": {"$addToSet": {"title": "$submissions.title", 
                                                                 "id":'$submissions.id', 
                                                                 "text": '$submissions.selftext', 
                                                                 "score": "$submissions.score",
                                                                 "num_comments":"$submissions.num_comments",
                                                                 "user": "$submissions.author",
                                                                 "subreddit": "$submissions.subreddit",
                                                                 "time": "$submissions.created_utc"}}}},
    ],
    allowDiskUse=True
))

#check if it works
val_s = [[x['sub'][0]['id'], x['sub'][0]['user'], x['sub'][0]['subreddit'], x['sub'][0]['time'], x['sub'][0]["title"], x['sub'][0]['text'], x['sub'][0]['score'], x['sub'][0]['num_comments']] for x in submissions if x["_id"] not None]
df_s = pd.DataFrame(val_s, columns=["id", "user", "subreddit", "time", "title", "text", "score", "num_comments"])
#if text empty add title instead? or in general merge title and text?
df_s.to_csv(folder + "all_posts.csv")

#controll for engagement/visibility
#can match by id with df_s
val_c = [[x["_id"], x['comm'][0]['user'], x['comm'][0]['subreddit'], x['comm'][0]['time'], x['comm'][0]['text'], x['comm'][0]['score'], x['comm'][0]['parent']] for x in comments if x["_id"] not None]
df_c = pd.DataFrame(val_c, columns=["id", "user", "subreddit", "time", "text", "score", "parent_post"])
df_c["parent_post"] = df_c.parent_post.apply(lambda x: x.split("_")[1])
df_c["parent_score"] = df_c['parent_post'].map(df_s.set_index('id')['score'])
df_c["parent_num_comments"] = df_c['parent_post'].map(df_s.set_index('id')['num_comments'])
df_c = df_c[(df_c.text!="[deleted]") & (df_c.text!="[removed]") & (df_c.text!="")] #remove comments that were deleted (by user or moderator) and comments that are empty (e.g., only space)

#107 comments cannot find parent post
df_c.to_csv(folder + "all_comments.csv")
