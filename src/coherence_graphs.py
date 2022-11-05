# ##import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
import sys
import pickle

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

""" Set Mode """
mode = int(sys.argv[1])
Path("../data/images").mkdir(exist_ok=True, parents=True)

""" Import Data """
text_types = ["posts", "comments", "all"]
text_type = text_types[mode-1]

# check topics folder for coherence_score_ + text_type files
files = next(os.walk("../data/results/topics"))[2]
files = [x for x in files if "coherence_score_" + text_type in x]

# load and append list (score) with values
scores = []
nrs = []
path = "../data/results/topics/"
for file in files:
    with open(path + file, "rb") as f:
        score = pickle.load(f)
        scores.append(score)
        # append list (x) with opt_nr from file name
    nr = int(file.split("_")[-1].split(".")[0])
    nrs.append(nr)

lists = sorted(zip(*[nrs, scores]))
x, y = list(zip(*lists))

# create graph
plt.plot(x, y)
plt.xlabel("Num Topics")
plt.ylabel("Coherence score")
plt.legend(("coherence_values"), loc='best')

# save in images
plt.savefig('../data/images/coherence_values_' + text_type + '.png')






















