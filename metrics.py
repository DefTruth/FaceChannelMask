#Set of custom metrics used by the loaded models
import numpy

def precision(y_true, y_pred):
    from keras import backend as Kend
    """Precision metric.
    Only computes a batch-wise average of precision.
    Computes the precision, a metric for multi-label classification of
    how many selected items are relevant.
    """
    true_positives = Kend.sum(Kend.round(Kend.clip(y_true * y_pred, 0, 1)))
    predicted_positives = Kend.sum(Kend.round(Kend.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + Kend.epsilon())
    return precision


def recall(y_true, y_pred):
    from keras import backend as Kend
    """Recall metric.
    Only computes a batch-wise average of recall.
    Computes the recall, a metric for multi-label classification of
    how many relevant items are selected.
    """
    true_positives = Kend.sum(Kend.round(Kend.clip(y_true * y_pred, 0, 1)))
    possible_positives = Kend.sum(Kend.round(Kend.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + Kend.epsilon())
    return recall


def fbeta_score(y_true, y_pred, beta=0.5):
    from keras import backend as Kend
    """Computes the F score.
    The F score is the weighted harmonic mean of precision and recall.
    Here it is only computed as a batch-wise average, not globally.
    This is useful for multi-label classification, where input samples can be
    classified as sets of labels. By only using accuracy (precision) a model
    would achieve a perfect score by simply assigning every class to every
    input. In order to avoid this, a metric should penalize incorrect class
    assignments as well (recall). The F-beta score (ranged from 0.0 to 1.0)
    computes this, as a weighted mean of the proportion of correct class
    assignments vs. the proportion of incorrect class assignments.
    With beta = 1, this is equivalent to a F-measure. With beta < 1, assigning
    correct classes becomes more important, and with beta > 1 the metric is
    instead weighted towards penalizing incorrect class assignments.
    """
    if beta < 0:
        raise ValueError('The lowest choosable beta is zero (only precision).')

    # If there are no true positives, fix the F score at 0 like sklearn.
    if Kend.sum(Kend.round(Kend.clip(y_true, 0, 1))) == 0:
        return 0

    p = precision(y_true, y_pred)
    r = recall(y_true, y_pred)
    bb = beta ** 2
    fbeta_score = (1 + bb) * (p * r) / (bb * p + r + Kend.epsilon())
    return fbeta_score


def fmeasure(y_true, y_pred):
    """Computes the f-measure, the harmonic mean of precision and recall.
    Here it is only computed as a batch-wise average, not globally.
    """
    return fbeta_score(y_true, y_pred, beta=1)


def ccc(y_true, y_pred):
    from keras import backend as K
    if K.backend() == 'tensorflow':
        import tensorflow as tf

        true_mean, true_variance = tf.nn.moments(y_true, axes=[0])
        pred_mean, pred_variance = tf.nn.moments(y_pred, axes=[0])

        cov = tf.reduce_mean(tf.multiply(tf.subtract(y_pred, pred_mean), tf.subtract(y_true, true_mean)))

        numerator = 2 * cov
        denominator = pred_variance + true_variance + tf.square(tf.subtract(pred_mean, true_mean))

        ccc = tf.divide(numerator, denominator)
        return ccc

def rmse(y_true, y_pred):
    from keras import backend as K
    return K.sqrt(K.mean(K.square(y_pred - y_true), axis=-1))



def ccc_numpy(y_true, y_pred):
    from scipy.stats import pearsonr
    import math


    true_mean = numpy.mean(y_true)
    true_variance = numpy.var(y_true)
    pred_mean = numpy.mean(y_pred)
    pred_variance = numpy.var(y_pred)


    rho,_ = pearsonr(y_pred,y_true)

    if math.isnan(rho):
        rho = 0

    std_predictions = numpy.std(y_pred)

    std_gt = numpy.std(y_true)

    ccc = 2 * rho * std_gt * std_predictions / (
        std_predictions ** 2 + std_gt ** 2 +
        (pred_mean - true_mean) ** 2)

    return ccc, rho