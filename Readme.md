# eSITB

This is the repository to the paper Sharing is in Fact about Caring: Care Concerns Feature Prominently in Subreddits Devoted to Self-Injurious Thoughts and Behaviors".
The repository contains all necessary files and code to replicate the data and the analysis. Please read the following instructions to replicate the data used in the paper's analysis.

## Additional Data files

- `data/links_comments.txt`: URLs for the reddit archive files (comments)
- `data/links_submissions.txt`: URLs for the reddit archive files (submissions)

## Instructions (Training Moral Classifiier)
1. Run `dataset_moral.py` to create the dataset from raw annotation data
  - `python dataset_moral.py`
2. Run `moral_classifier.py` to create the dataset from raw annotation data
  - `python moral_classifier.py 1` (moral vs non moral concerns classifier)
  - `python moral_classifier.py 2` (binding vs individualizing concerns classifier)
  - `python moral_classifier.py 3` (all moral concerns classifier)

## Instructions (Topic Modelling)

*Note, that we used the combined texts (posts + comments) for all analyses.
Note, that we only used the moral/nonmoral and all concerns classifier.
Use the additional examples, if you want to focus on certain texts (e.g., only comments/posts) and certain moral concerns (e.g., binding vs individualizing)*

1. Use a command such as `aria2c` or equivalent to download the reddit data from the pushshift archives. Save the data under `data/pushshift/submissions` and `data/pushshift/comments` for posts and comments respectively.
  - `aria2c -c -s 16 -x 16 -k 1M -j 4 -i ../data/links_comments.txt -d ../data/pushshift/comments`
  - `aria2c -c -s 16 -x 16 -k 1M -j 4 -i ../data/links_submissions.txt -d ../data/pushshift/submissions`
2. Run the `get_extractions.py` files to extract the relevant data from the archives. If you have access to a computing cluster, you can use the `.job` files. Otherwise, adapt the code to run on your machine (potentially *very* slow).
  - `sbatch extractions.job`
3. Run `read_to_database.py` to load the data into a database (e.g., MongoDB)
  - `python read_to_database.py`
4. Run `get_messages.py` Create raw datasets from the data base entries
- `python get_messages.py`
5. Run `get_annotation_data.py` to create corpora 
  - `python get_annotation_data.py 1` (posts)
  - `python get_annotation_data.py 2` (comments)
6. Run `get_annotation_data_all.py` (all; combines posts and comments data for topic modelling)
  - `python get_annotation_data_all.py` 
7. Run `predict_foundations.py` to classify moral concerns in each message
  - `python predict_foundations.py 1` (moral vs non-moral classifier)
  - `predict_foundations.py 3` (individual moral foundations classifier)
8. Run `topic_modelling.py` to run the topic modelling (hyperparameter tuning, determine the best parameter, outputs a graph for hyperparameter performance). 
  - `python topic_modelling.py 1` (posts)
  - `python topic_modelling.py 2` (comments)
  - `python topic_modelling.py 3` (all)
9. Run `tm_nr.py` to get topic modelling for a fixed number of topic (e.g., manually checking performance/results of a given number of topics)
  - `python tm_nr.py N` (replace N with number of topics; outputs distribution of topics, list of prototypical messages for each topic, classification of each message into most dominant topic and interactive visualisation of topics)
11. Run `merge_data.py` to create final data set from topic modelling results (merges moral classifications with topics).
  - `python merge_data 1 N` (moral vs nonmoral concerns; replace N with number of topics in model)
  - `python merge_data 2 N` (binding vs individualizing concerns; replace N with number of topics in model)
  - `python merge_data 3 N` (all moral concerns; replace N with number of topics in model)
12. Run the `selfharm_analyses.Rmd` script in R to replicate the statistical analysis.

## Instructions (Additional Code)
- Run `ntopic_modelling.py` to get the coherence score for a given number of topics (loads existing model or extract topics if not; saves fitted model and its coherence score)
  - `python ntopic_modelling.py 1` (posts)
  - `python ntopic_modelling.py 2` (comments)
  - `python ntopic_modelling.py 3` (all)
- Run `coherence_graphs.py` to create a graph of coherence score over number of clusters for all manually trained/saved models
  - `python coherence_graphs.py` 
