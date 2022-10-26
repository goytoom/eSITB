import pandas as pd

sub_names = ["selfharm", "suicidewatch"]
sub_names = [x.lower() for x in sub_names]

# save in csv file
df = pd.DataFrame({"subreddit":sub_names})
df.to_csv("../data/subreddit_list.csv")
