"""
Parameteric categorical distributions.
"""

import numpy as np
import tensorflow as tf

from .base import Distribution

class CategoricalSoftmax(Distribution):
    """
    A probability distribution that uses softmax to decide
    between a discrete number of options.
    """
    def __init__(self, num_options):
        self.num_options = num_options

    @property
    def param_size(self):
        return self.num_options

    def sample(self, param_batch):
        param_batch = np.array(param_batch)
        max_vals = param_batch.max(axis=-1)
        unnorm = np.exp(param_batch - max_vals)
        probs = unnorm / np.sum(unnorm, axis=-1)
        return [np.random.choice(len(p), p=p) for p in probs]

    def to_vecs(self, samples):
        return np.array(samples)

    def log_probs(self, param_batch, sample_vecs):
        loss_func = tf.nn.softmax_cross_entropy_with_logits
        indices = tf.to_int32(sample_vecs)
        one_hot = tf.one_hot(indices=indices, depth=self.num_options)
        return tf.negative(loss_func(labels=one_hot, logits=param_batch))

    def entropy(self, param_batch):
        log_probs = tf.nn.log_softmax(param_batch)
        probs = tf.exp(log_probs)
        return tf.negative(tf.reduce_sum(log_probs * probs, axis=-1))

    def kl_divergence(self, param_batch_1, param_batch_2):
        log_probs_1 = tf.nn.log_softmax(param_batch_1)
        log_probs_2 = tf.nn.log_softmax(param_batch_2)
        probs = tf.exp(log_probs_1)
        return tf.reduce_sum(probs * (log_probs_1 - log_probs_2))
