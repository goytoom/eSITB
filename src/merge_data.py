import pandas as pd
import sys

#"""" Load Data """"

i = int(sys.argv[1])
nr = int(sys.argv[2])

modes = ["full", "binding", "moral"]
mode = modes[i-1]

df_posts = pd.read_csv("../data/results/all_posts_" + mode + ".csv", keep_default_na=False, lineterminator="\n")
df_comments = pd.read_csv("../data/results/all_comments_" + mode + ".csv", keep_default_na=False, lineterminator="\n")
df_comments["type"] = "comment"
df_posts["type"] = "post"

df_topics = pd.read_csv("../data/results/topics/topics_all_" + str(nr) + ".csv", keep_default_na=False, lineterminator="\n").drop(["Text", "Document_No"], axis=1)

df_concat = pd.concat([df_posts, df_comments])
df_merged = pd.merge(df_concat, df_topics, on="id")

df_merged.to_csv("../data/results/merged_data_all_" + mode + "_" + str(nr) + ".csv", index=False)
