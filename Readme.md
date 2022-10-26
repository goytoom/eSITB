# eSITB

This is the repository to the paper Sharing is in Fact about Caring: Care Concerns Feature Prominently in Subreddits Devoted to Self-Injurious Thoughts and Behaviors".
The repository contains all necessary files and code to replicate the data and the analysis.

## Data

...

## Code files

...

## Instructions (PLACEHOLDER)

1.) Use a command such as `aria2c` or equivalent to download the reddit data from the pushshift archives. Save the data under `data/pushshift/submissions` and `data/pushshift/comments` for posts and comments respectively.
2.) Run the `extraction-file` to extract the relevant data from the archives. If you have access to a computing cluster, you can use the `.job` files. Otherwise, adapt the code to run on your machine (potentially *very* slow).
3.) Run `database-file` to load the data into a database (e.g., MongoDB)
4.) Run `data-creation-file` to create the datasets as `.csv` files.
5.) Run `LDA-prep-file` to create all neccessary data for the topic modelling
6.) Run `LDA-file` to run the topic modelling
7.) Run `misc-file` to run the remaining analysis.
.
.
.
N) Run the `stats-file` in R to replicate the statistical analysis.
