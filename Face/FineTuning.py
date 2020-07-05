from __future__ import absolute_import, division, print_function, unicode_literals


import numpy as np
import matplotlib.pyplot as plt

import itertools
import os

import tensorflow as tf
import tensorflow_hub as hub

AUTOTUNE = tf.data.experimental.AUTOTUNE

import pathlib
import pickle
from sklearn.preprocessing import LabelEncoder

data_dir = '/media/huanbuster/Vision/Python/Parki/Face/CollectCopy'
output_dir = '/media/huanbuster/Vision/Python/Parki/Face/Output/'
num_classes = len(os.listdir(data_dir))
print('Number of classes: ',num_classes)
# Encoding Name 
# name = os.listdir(data_dir)
# # print(name)
# tag = LabelEncoder()
# labels = tag.fit(name)
# print(labels.classes_)
# # write the label encoder to disk
# f = open('/media/huanbuster/Vision/Python/Parki/Face/Output/label.pickle', "wb")
# f.write(pickle.dumps(tag))
# f.close()

BATCH_SIZE = 32
IMG_HEIGHT = 224
IMG_WIDTH = 224
IMG_SHAPE = (IMG_HEIGHT, IMG_WIDTH, 3)
# SHUFFLE_BUFFER_SIZE = 1000

#Load using keras.preprocessing
datagen_kwargs = dict(rescale=1./255, validation_split=.3)
dataflow_kwargs = dict(target_size=(IMG_HEIGHT, IMG_WIDTH),
                                    batch_size=BATCH_SIZE,
                                    interpolation="bilinear")

valid_generator = tf.keras.preprocessing.image.ImageDataGenerator(
    **datagen_kwargs)
valid_data = valid_generator.flow_from_directory(
    data_dir, subset="validation", shuffle=False, **dataflow_kwargs)

do_data_augmentation = False #@param {type:"boolean"}
if do_data_augmentation:
  train_generator = tf.keras.preprocessing.image.ImageDataGenerator(
      rotation_range=40,
      horizontal_flip=True,
      width_shift_range=0.2, height_shift_range=0.2,
      shear_range=0.2, zoom_range=0.2,
      **datagen_kwargs)
else:
  train_generator = valid_generator
train_data = train_generator.flow_from_directory(
    data_dir, subset="training", shuffle=True, **dataflow_kwargs)

print('Number of training images: ', train_data.samples)
print('Number of validating images: ', valid_data.samples)

for image_batch, label_batch in train_data:
  print("Image batch shape: ", image_batch.shape)
  print("Label batch shape: ", label_batch.shape)
  break

feature_extractor_url = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/feature_vector/4" #@param {type:"string"}
feature_extractor_layer = hub.KerasLayer(feature_extractor_url,
                                         input_shape=(224,224,3))
                                
feature_extractor_layer.trainable = False

model = tf.keras.Sequential([
  tf.keras.layers.InputLayer(input_shape=(224,224,3)),
  feature_extractor_layer,
  tf.keras.layers.Dropout(rate=0.01),
  tf.keras.layers.Dense(train_data.num_classes,
                          kernel_regularizer=tf.keras.regularizers.l2(0.00005))
])
model.build((None, 224, 224, 3))
model.summary()
model.compile(
  optimizer=tf.keras.optimizers.SGD(lr=0.00005, momentum=0.9),
  loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True,label_smoothing=0.1),
  metrics=['accuracy'])

print('Steps per epoch: ',train_data.samples // BATCH_SIZE)
print('Validations per epoch: ',valid_data.samples // BATCH_SIZE)

epochs=20
# Training 
history = model.fit(
    train_data,
    steps_per_epoch= train_data.samples // BATCH_SIZE,
    epochs=epochs,
    validation_data=valid_data,
    validation_steps= valid_data.samples // BATCH_SIZE)


acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss=history.history['loss']
val_loss=history.history['val_loss']

epochs_range = range(epochs)
# Plot the result 
plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()
# Save model 
model.save('Output/Recognizer_V6')





