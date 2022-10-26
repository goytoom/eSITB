# -*- coding: utf-8 -*-
"""
Created on Sun Oct 10 13:56:57 2021

@author: suhai
"""

""" Import Packages """
from pymongo import MongoClient
import os
import json

""" Functions """
# def findById_Sub(db, id): #given a post id and a database, return the respective submissions
#     #change to function:
#     submissions = list(db.collection.aggregate(
#     [# //De-normalized the nested array of cars
#     {"$unwind": "$submissions"},
#     # //match carId to 3C
#     {"$match": {"submissions.id" : id}},
#     # //Project the submissions object only
#     {"$group": { "_id": '$submissions.id', "sub": { "$addToSet": '$submissions'}}},
#     ]))
#     return submissions

# def findById_Comm(db, id): #given a post id and a database, return ALL the respective comments
#     #change to function:
#     id = "t3_" + id #add prefix
#     comments = list(db.collection.aggregate(
#     [# //De-normalized the nested array of cars
#     {"$unwind": "$comments"},
#     # //match carId to 3C
#     {"$match": {"comments.link_id" : id}},
#     # //Project the submissions object only
#     {"$group": { "_id": '$comments.id', "sub": { "$addToSet": '$comments'}}},
#     ]))
#     return comments

def readToDB(folders):
    file_data = []
    for filename in folders:
        #iterate over json files
        with open(folder + filename) as file:
            file_data.extend(json.load(file))                 #load as json
    if isinstance(file_data, list):                 #dump into database
        collection_t.insert_many(file_data)  
    else:
        collection_t.insert_one(file_data)
    return 0

def splitReadingToDB(folders, s):
    l = len(folders)
    n = int(l/s) + (l%s >0)
    for i in range(s):
        readToDB(folders[i*n:(i+1)*n])
    return 0

""" Import Data """
folder = "../data/extractions/"

#Create mongoDB
client = MongoClient()
db  = client.selfharm
collection_t = db.collection

#read in jsons (csv)
folders = os.listdir(folder)        #read path of all files
s = 4 #how many splits?
if len(folders)>100: #for large lists split the reading in half
    splitReadingToDB(folders, s)
else: #for small read at once
    readToDB(folders)

client.close()




























