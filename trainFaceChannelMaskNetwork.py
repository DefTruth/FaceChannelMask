"""
Emotion Recognition - Vision-Frame-Based Face Channel

__author__ = "Pablo Barros"

__version__ = "0.1"
__maintainer__ = "Pablo Barros"
__email__ = "barros@informatik.uni-hamburg.de"

More information about the implementation of the model:

Barros, P., & Wermter, S. (2016). Developing crossmodal expression recognition based on a deep neural model. Adaptive behavior, 24(5), 373-396.
http://journals.sagepub.com/doi/full/10.1177/1059712316664017

"""

import cv2
import modelLoader
import numpy
import os
import tensorflow as tf
import matplotlib.pyplot as plt

config = tf.ConfigProto()
config.gpu_options.allow_growth=True
sess = tf.Session(config=config)

def createHistogram(arousal, valence, directory, name):

    fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)

    # We can set the number of bins with the `bins` kwarg
    axs[0].hist(arousal, bins=20)
    axs[1].hist(valence, bins=20)

    plt.savefig(directory + "/_"+str(name)+"_dataDistribution_.png")

    plt.clf()

def preProcess(image, imageSize=(64, 64)):
    image = numpy.array(image)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    image = numpy.array(cv2.resize(image, imageSize))

    image = numpy.expand_dims(image, axis=0)

    image = image.astype('float32')

    image /= 255

    return image



finalImageSize = (1024,768) # Size of the final image generated by the demo
categoricalInitialPosition = 260 # Initial position for adding the categorical graph in the final image
faceSize = (64,64) # Input size for both models: categorical and dimensional
faceDetectionMaximumFrequency = 20 # Frequency that a face will be detected: every X frames.

modelDimensional = modelLoader.modelLoader("/home/pablo/Documents/Workspace/EmotionsWithMasks/trainedModels/FaceChannel_Dimensional.h5")

saveNetwork = "/home/pablo/Documents/Workspace/EmotionsWithMasks/trainedModels/"

trainDataSet = "/home/pablo/Documents/Datasets/AffectNet_Mask/Training" #AffectNet-Mask
# trainDataSet = "/home/pablo/Documents/Datasets/AffectNet/AffectNetProcessed_Training" #AffectNet

images = []
amount = 0
labels = []
arousals = []
valences = []

print ("Loading Images")

imageList =os.listdir(trainDataSet)

for imgFile in imageList:
    img = preProcess(cv2.imread(trainDataSet+"/"+imgFile))
    images.append(img)
    arousals.append(float(imgFile.split('__')[2]))
    valences.append(float(imgFile.split('__')[3][0:-4]))
    amount +=1
    if amount % 10000 == 0:
        print ("Still loading...")


images = numpy.array(images)
modelDimensional.buildModel(images.shape[1:])

createHistogram(arousals, valences, "/home/pablo/Documents/Datasets/AffectNet_Mask", "original_all")
#
print ("Total images: " + str(amount))

modelDimensional.trainModel(images,numpy.array(arousals), numpy.array(valences), saveNetwork)

results = numpy.array(modelDimensional.evaluate(images, numpy.array(arousals), numpy.array(valences)))

arousalCCC = results[-2]
valenceCCC = results[-1]
print ("arousalCCC: " + str(arousalCCC))
print ("valenceCCC: " + str(valenceCCC))