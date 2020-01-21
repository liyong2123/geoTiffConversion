from __future__ import absolute_import, division, print_function, unicode_literals

from warnings import simplefilter 
simplefilter(action='ignore', category=FutureWarning)

from keras.layers import Input, Dense, Dropout, Embedding, Flatten, Multiply, Concatenate, LeakyReLU
import os
from keras.models import Model
from keras.regularizers import l2, l1
import numpy as np
import tensorflow as tf
import netCDF4
from tensorflow import keras
import matplotlib.pyplot as plt
from sklearn.utils import shuffle

fs = ""
fc = []
for root, dirs, files in os.walk(os.getcwd()):
    files.sort()
    for f in files:
        if f.endswith(".nc"):
            fs = f

openf = netCDF4.Dataset(fs, "r")
n_features = openf.dimensions["Bands"].size
arr = np.zeros([n_features, openf.dimensions["y"].size, openf.dimensions["x"].size])
arr[:] = openf.variables["Data"][:]

for c in range(0, n_features - 1):
    arr[c] = np.fliplr(np.rot90(arr[c, :, :], 2))

print(arr.shape)

arrtrain = np.array([
    #Water
    arr[:, 714, 697],
    arr[:, 395, 926],
    arr[:, 2933, 149],
    arr[:, 432, 906],

    arr[:, 1725, 432],
    arr[:, 1681, 453],
    arr[:, 1674, 427],
    #Land
    arr[:, 1801, 510],
    arr[:, 1747, 571],
    arr[:, 1697, 543],
    arr[:, 1688, 613],
    arr[:, 1783, 532],
    arr[:, 1621, 646],
    arr[:, 1865, 521]

])
arrOutput = np.array([
    [0],[0],[0],[0],[0],[0],[0], [1], [1], [1], [1], [1], [1], [1]
    ] 
)
#Water Pred
arrpred = np.array(
    [
    arr[:, 2994, 253],
    arr[:, 1679, 568]
    ]
)
#Land Pred
arrpred2 = np.array(
    [
        [0],
        [1]
    ]
)

def create_model(input_features):
    in_ = Input((input_features,))
    x = Dense(32, activation="relu", kernel_regularizer=l1(0.001))(in_)
    x = Dropout(0.5)(x)
    x = Dense(2, activation="softmax")(x)

    model = Model(in_, x)
    return model

model = create_model(242)
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.summary()

#arrtrain = arrtrain[:,: -200]

arrtrain, arrOutput = shuffle(arrtrain, arrOutput, random_state=0)

model.fit(arrtrain, arrOutput, epochs=40, steps_per_epoch=1000)

model.save_weights("weights")

test_loss, test_acc = model.evaluate(arrpred, arrpred2)
print('\nTest accuracy:', test_acc)
