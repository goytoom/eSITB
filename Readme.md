# eSITB

This is the repository to the paper Sharing is in Fact about Caring: Care Concerns Feature Prominently in Subreddits Devoted to Self-Injurious Thoughts and Behaviors".
The repository contains all necessary files and code to replicate the data and the analysis.

## Data files

- `links_comments.txt`: URLs for the reddit archive files (comments)
- `links_submissions.txt`: URLs for the reddit archive files (submissions)

## Code files

* Main code files (in order of execution, use relevant `.job` files for parallel execution on a computing cluster):
  * `links.py`: This code scrapes the links to the Reddit dumps on pushshift.io. This step is only necessary if the Reddit dumps need to be downloaded for manual extraction of the data. The files can then be downloaded with, e.g., aria2c
  * `get_extractions.py`: This code returns submissions and comments from downloaded Reddit dumps for any given list of post ids, then saves them in csv files. This should best be run on a server in parallel! Again, this is only necessary if the data files themselves need to be reproduced. Other wise, the analyses can be run with the produced final data set.
  * `read_to_database.py`: This code reads csv files into mongoDB databases
  * `get_messages.py`: Create raw datasets from the data base entries
  * `get_annotation_data.py`: Preprocess reddit data and create files for topic modelling
  * `topic_modelling.py`: Run topic modelling without specifying parameters (automatic hyperparameter tuning; creates metrics for multiple parameters and saves results for manual parameter identification)
  * `tm_nr.py`: Runs LDA with specific parameters
  * `merge_data.py`: Creates final data set by merging topic modelling results and extracted messages
  * `selfharm_analyses.Rmd`: Statistical analyses (R script)

## Instructions (PLACEHOLDER)

1. Use a command such as `aria2c` or equivalent to download the reddit data from the pushshift archives. Save the data under `data/pushshift/submissions` and `data/pushshift/comments` for posts and comments respectively.
  - aria2c -c -s 16 -x 16 -k 1M -j 4 -i ../data/links_comments.txt -d ../data/pushshift/comments
  - aria2c -c -s 16 -x 16 -k 1M -j 4 -i ../data/links_submissions.txt -d ../data/pushshift/submissions
2. Run the `get_extractions.py` files to extract the relevant data from the archives. If you have access to a computing cluster, you can use the `.job` files. Otherwise, adapt the code to run on your machine (potentially *very* slow).
  - `sbatch extractions_target.job`
  - `sbatch extractions_source.job`
3. Run `read_to_database.py` to load the data into a database (e.g., MongoDB)
  - `python read_to_database.py source`
  - `python read_to_database.py target`
4. Run `get_messages.py` Create raw datasets from the data base entries
- `python get_messages.py`
5. Run `get_annotation_data` to create all neccessary data for the topic modelling
  - SPLIT CODE for combo into separate file (executed afterwards)
6. Run `topic_modelling.py` to run the topic modelling (hyperparameter tuning, determine the best parameter). 
  - ... 
7. Run `tm_nr.py` to run the topic modelling with specific parameters (can be determined from metric plots, etc.)
  - ...
8. Run `merge_data.py` to create final data set from topic modelling results.
  - ...
9. Run the `selfharm_analyses.Rmd` in R to replicate the statistical analysis.
