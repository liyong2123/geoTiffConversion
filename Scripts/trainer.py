from __future__ import absolute_import, division, print_function, unicode_literals

from warnings import simplefilter 
simplefilter(action='ignore', category=FutureWarning)

from keras.layers import Input, Dense, Dropout, Embedding, Flatten, Multiply, Concatenate, LeakyReLU
import os
from keras.models import Model
from keras.regularizers import l1
import numpy as np
import netCDF4
from tensorflow import keras
from sklearn.utils import shuffle
from keras.utils.vis_utils import plot_model


def create_model(input_features):
    in_ = Input((input_features,))
    # We are using l1, aka Lasso Regression, because we have 242 Bands, of which some are of less importance, so we want to have
    # Feature selection, therefore allowing us to pinpoint these more accuarately.(Prevents overfitting) .001 is for reducing variance 
    # of error without increasing bias(AKA makes it not learn specific details within graph)
    x = Dense(32, activation="relu", kernel_regularizer=l1(0.001))(in_)
    x = Dense(16, activation="relu", kernel_regularizer=l1(0.001))(in_)
    # Once again, used to prevent overfitting of data, by dropping out 50% of the nodes randomly
    x = Dropout(0.5)(x)
    x = Dense(3, activation="softmax")(x)

    model = Model(in_, x)

    model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

    return model
if __name__ == "__main__":
    main()

def main():
    fs = ""
    fc = []
    #FINDS THE NETCDF FILE in the directory
    for root, dirs, files in os.walk(os.getcwd()):
        files.sort()
        for f in files:
            if f.endswith(".nc"):
                fs = f

    openf = netCDF4.Dataset(fs, "r")
    n_features = openf.dimensions["Bands"].size
    #Initializes 3D array with all zeros in shape of (BANDS,Y,X)
    arr = np.zeros([n_features, openf.dimensions["y"].size, openf.dimensions["x"].size])
    arr[:] = openf.variables["Data"][:]

    #Changes the array to orient correctly(Could be changed )
    for c in range(0, n_features - 1):
        arr[c] = np.fliplr(np.rot90(arr[c, :, :], 2))

    print(arr.shape)

    #Array for training Data, coordinates are in (y,x)
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
        arr[:, 1865, 521],
        #Empty
        arr[:, 40, 40],
        arr[:, 40, 30],
        arr[:, 1, 1],
        arr[:,2900,900]

    ])
    #Classification array, correcsponds to arrtrain, number corresponds to the class
    arrOutput = np.array([
        [0],[0],[0],[0],[0],[0],[0], [1], [1], [1], [1], [1], [1], [1], [2], [2], [2], [2]
        ] 
    )
    #Testing Array
    arrpred = np.array(
        [
        arr[:, 2994, 253],
        arr[:, 1679, 568],
        arr[:, 2500, 700]
        ]
    )
    #Land Pred
    arrpred2 = np.array(
        [
            [0],
            [1],
            [2]
        ]
    )
    #creates the model
    model = create_model(242)

    model.summary()

    #Shuffles the data, arrtrain and arrOutput has to be shuffled the same way or classification will not work
    arrtrain, arrOutput = shuffle(arrtrain, arrOutput, random_state=0)
    # Tries to open the weights and imports it into model if it exists
    try:
        model.load_weights("weights")
    except Exception:
        print("New Weight File")

    # Trains the model based on array
    model.fit(arrtrain, arrOutput, epochs=40, steps_per_epoch=1000)

    plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)
    #saves the weights of trained model as "weights"
    model.save_weights("weights")

    test_loss, test_acc = model.evaluate(arrpred, arrpred2)
    print('\nTest accuracy:', test_acc)
