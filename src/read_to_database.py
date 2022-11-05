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




























