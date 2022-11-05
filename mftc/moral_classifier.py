# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 10:46:22 2022

@author: suhai
"""

import tensorflow_hub as hub
import tensorflow as tf
from tensorflow_addons.metrics import FBetaScore
from tensorflow.keras.models import load_model 
from keras.metrics import Precision, Recall
import sys
from pathlib import Path

import pickle as pkl

from sklearn.metrics import f1_score as f1Score

# import nltk
# nltk.download('stopwords')

def f1_loss(y_true, y_pred):
	tp = K.sum(K.cast(y_true*y_pred, "float"), axis = 0)
	tn = K.sum(K.cast((1-y_true)*(1-y_pred), "float"), axis = 0)
	fp = K.sum(K.cast((1-y_true)*y_pred, "float"), axis = 0)
	fn = K.sum(K.cast(y_true*(1-y_pred), "float"), axis = 0)
	
	p = tp/(tp + fp + K.epsilon())
	r = tp/(tp + fn + K.epsilon())
	
	f1 = 2*p*r/(p + r + K.epsilon())
	f1 = tf.where(tf.math.is_nan(f1), tf.zeros_like(f1), f1)
	return 1 - K.mean(f1)

def build_model(bert_layer, max_len=512, classes = 5, activation = "sigmoid"):
    input_word_ids = tf.keras.Input(shape=(max_len,), dtype=tf.int32, name="input_word_ids")
    input_mask = tf.keras.Input(shape=(max_len,), dtype=tf.int32, name="input_mask")
    segment_ids = tf.keras.Input(shape=(max_len,), dtype=tf.int32, name="segment_ids")

    outputs= bert_layer(dict(input_word_ids=input_word_ids,
    input_mask=input_mask,
    input_type_ids=segment_ids))

    # pooled_output=outputs["pooled_output"]
    sequence_output=outputs["sequence_output"]

    clf_output = sequence_output[:, 0, :]
    net = tf.keras.layers.Dense(64, activation='relu')(clf_output) #128|0.5|64|0.5|32|0.5
    net = tf.keras.layers.Dropout(0.2)(net)
    net = tf.keras.layers.Dense(32, activation='relu')(net)
    net = tf.keras.layers.Dropout(0.2)(net)
    out = tf.keras.layers.Dense(classes, activation=activation)(net)

    model = tf.keras.models.Model(inputs=[input_word_ids, input_mask, segment_ids], outputs=out)
    model.compile(tf.keras.optimizers.Adam(learning_rate=1e-5),
                  loss="binary_crossentropy", metrics=[Precision(), Recall(), FBetaScore(num_classes = classes, average = "macro", threshold = 0.5, name="f1_score", dtype = None)])
    model.summary()
    return model


def get_binary(_y, threshold):
    y = _y.copy()
    y[y >= threshold] = 1
    y[y < threshold] = 0
    return y

def F1Measure(y_true, y_pred, threshold=0.5):
    y_binary = get_binary(y_pred, threshold)

    return f1Score(y_true, y_binary, average = "weighted")    

def train(model_file, mode, bert_layer):
    
    classes = {"full": 5, "moral": 1, "binding": 2}
    activation = {"full": "sigmoid", "moral": "sigmoid", "binding": "sigmoid"}
    model = build_model(bert_layer, max_len=256, classes = classes[mode], activation = activation[mode])

    print(model.summary())
    with open("data/train_" + mode + ".pkl", "rb") as f:
        X_train, y_train = pkl.load(f)

    checkpoint = tf.keras.callbacks.ModelCheckpoint(model_file, monitor='val_loss', save_best_only=True, verbose=1)
    earlystopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, verbose=1)

    print("start training")
    t = model.fit(
        X_train, y_train,
        validation_split=0.2,
        epochs=200,
        callbacks=[checkpoint, earlystopping],
        batch_size=32, #32 works best so far
        verbose=1)
    print(t)
    print("Saving the model")
    # t.save

def evaluate(model_file, data_file, bert_layer, threshold=0.5):

    model = load_model(model_file, compile=True, custom_objects={"KerasLayer": bert_layer})

    with open(data_file, "rb") as f:
        X_test, y_test = pkl.load(f)

    y_pred = model.predict(X_test)
    print('predicted')
    
    f1_score = F1Measure(y_test, y_pred, threshold=0.9)
    print(f"threshold: {0.9}, score :{f1_score}")
    f1_score = F1Measure(y_test, y_pred, threshold=0.8)
    print(f"threshold: {0.8}, score :{f1_score}")
    f1_score = F1Measure(y_test, y_pred, threshold=0.7)
    print(f"threshold: {0.7}, score :{f1_score}")
    f1_score = F1Measure(y_test, y_pred, threshold=0.6)
    print(f"threshold: {0.6}, score :{f1_score}")
    f1_score = F1Measure(y_test, y_pred, threshold=0.5)
    print(f"threshold: {0.5}, score :{f1_score}")
    f1_score = F1Measure(y_test, y_pred, threshold=0.4)
    print(f"threshold: {0.4}, score :{f1_score}")
    f1_score = F1Measure(y_test, y_pred, threshold=0.3)
    print(f"threshold: {0.3}, score :{f1_score}")
    f1_score = F1Measure(y_test, y_pred, threshold=0.2)
    print(f"threshold: {0.2}, score :{f1_score}")
    f1_score = F1Measure(y_test, y_pred, threshold=0.1)
    print(f"threshold: {0.1}, score :{f1_score}")

    results = model.evaluate(X_test, y_test)
    print(results)


if __name__ == '__main__':

    i = int(sys.argv[1])
    Path("models").mkdir(parents=True, exist_ok=True)
    
    module_url = "https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-12_H-256_A-4/2"
    bert_layer = hub.KerasLayer(module_url, trainable=True)

    modes = ["moral", "binding", "full"]
    mode = modes[i-1]
    print(mode)
    
    data_file = "data/test_" + mode + ".pkl"
    model_file = "models/model_" + mode + "_new.h5"
    
    train(model_file, mode, bert_layer)
    evaluate(model_file, data_file, bert_layer) 
    
    
    
    
    
    
    
    
