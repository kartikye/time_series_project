#! /usr/bin/env python3

import tensorflow as tf
import numpy as np
from sklearn import datasets
import sys

from plaid_data_setup import get_input_len, get_labels_len, train_cycle_nn, gen_data, train_cycle_sequence_nn, train_cycle_hierarchy_nn


def build_nn():

    # Config:
    n_hidden         = 30
    n_input          = get_labels_len()
    n_labels         = get_labels_len()
    learning_rate    = 0.001

    # neural network inputs and expected results
    X = tf.placeholder("float", [None, n_input])
    Y = tf.placeholder("float", [None, n_labels])
    #dropout_prob = tf.placeholder_with_default(1.0, shape=())

    # neural network parameters
    weights = {
        'h1':  tf.Variable(tf.random_normal([n_input, n_hidden])),
        'out': tf.Variable(tf.random_normal([n_hidden, n_labels])),
    }
    biases = {
        'b1':   tf.Variable(tf.random_normal([n_hidden])),
        'out':  tf.Variable(tf.random_normal([n_labels])),
    }

    def neural_net(x):
        # hidden fully connected layer
        layer_1 = tf.nn.tanh(tf.add(tf.matmul(x, weights['h1']), biases['b1']))
        # dropout on hidden layer
        #layer_1_drop = tf.nn.dropout(layer_1, dropout_prob)
        # output fully connected layer, neuron for each class
        out_layer = tf.matmul(layer_1, weights['out']) + biases['out']
        return out_layer

    # construct model
    logits = neural_net(X)
    prediction = tf.nn.softmax(logits) # reduce unscaled values to probabilities

    # Define loss and optimizer
    loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=Y))
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    train_op = optimizer.minimize(loss_op)

    # Evaluate
    predictions = tf.argmax(prediction, 1)
    pred_scores = tf.reduce_max(prediction,1)
    correct_pred = tf.equal(predictions, tf.argmax(Y, 1)) # check the index with the largest value
    accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32)) # percentage of traces that were correct

    graphene = tf.get_default_graph()

    return graphene, X, Y, train_op, [loss_op, accuracy, predictions, pred_scores, correct_pred]

if __name__ == "__main__":
    # train the neural network on test data
    graph, X, Y, optimizer, evaluation_args = build_nn()
    train_cycle_hierarchy_nn(graph, X, Y, optimizer, evaluation_args, gen_data(), 'dense_single_layer')

