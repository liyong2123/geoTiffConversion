from __future__ import absolute_import, division, print_function, unicode_literals
from warnings import simplefilter 
simplefilter(action='ignore', category=FutureWarning)

from keras.layers import Input, Dense, Dropout, Embedding, Flatten, Multiply, Concatenate, LeakyReLU
import os
from keras.models import Model
from keras.regularizers import l1, l2
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
    x = Dense(200, activation="relu", kernel_regularizer=l1(.0001))(in_)
    x = Dense(200, activation="relu", kernel_regularizer=l1(.0001))(x)
    x = Dense(200, activation="relu", kernel_regularizer=l1(.0001))(x)
    x = Dense(200, activation="relu", kernel_regularizer=l1(.0001))(x)
    x = Dense(200, activation="relu", kernel_regularizer=l1(.0001))(x)



    x = Dropout(0.5)(x)

    # Once again, used to prevent overfitting of data, by dropping out 50% of the nodes randomly
    #x = Dropout(0.5)(x)
    x = Dense(8, activation="softmax")(x)

    model = Model(in_, x)

    model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy', 
              metrics=['accuracy'])

    return model


def main():
    fs = ""
    fc = []
    #FINDS THE NETCDF FILE in the directory
    #for root, dirs, files in os.walk(os.getcwd()):
    #    files.sort()
    #    for f in files:
    #        if f.endswith(".nc"):
    #            fs = f

    #openf = netCDF4.Dataset(fs, "r")
    #n_features = openf.dimensions["Bands"].size
    #Initializes 3D array with all zeros in shape of (BANDS,Y,X)
    #arr = np.zeros([n_features, openf.dimensions["y"].size, openf.dimensions["x"].size])
    #arr[:] = openf.variables["Data"][:]

    #Changes the array to orient correctly(Could be changed )
    #for c in range(0, n_features - 1):
    #    arr[c] = np.fliplr(np.rot90(arr[c, :, :], 2))

    #print(arr.shape)
    #np.save("Array.npy", arr)
    #Array for training Data, coordinates are in (y,x)
    arr = np.load("Array.npy")
    arrtrain = np.array([
        #Houses
        arr[:, 1559, 629],
        #arr[:, 1593, 557],
        #arr[:, 1600, 553],
        #arr[:, 1595, 566],

        #Trees
        arr[:, 1740, 578],

        # Parking Lot
        arr[:, 1556, 630],
        #arr[:, 2070, 478],
        #arr[:, 2043, 479],
        #arr[:, 2042, 477],

        # Shallow Water
        arr[:, 2049, 476],
        arr[:, 2046, 474],
        #arr[:, 2059, 487],
        #arr[:, 2073, 471],

        #Field
        arr[:, 1966, 542],
        #arr[:, 2015, 482],
        #arr[:, 2021, 480],

        # Deep Water
        arr[:, 2034, 384],
        arr[:, 2034, 385],
        #arr[:, 2562, 273],
        #arr[:, 2182, 375],

        # Road
        arr[:, 1536, 607],
        arr[:, 1549, 621],
        #arr[:, 1563, 609],
        #arr[:, 1562, 609],

        #Empty
        arr[:, 40, 40],
        arr[:, 40, 30]
        #arr[:, 1, 1],
        #arr[:,2900,900]

    ])
    #Classification array, correcsponds to arrtrain, number corresponds to the class
    # 0 = House
    # 1 = Trees
    # 2 = Shallow Water
    # 3 = Fields
    # 4 = Deep Water
    # 5 = Concrete
    # 6 = Empty
    arrOutput = np.array([
        [0],
        #[0],
        #[0],
        [1],
        #[1],
        #[1],
        [2],
        #[1],
        #[2],
        [3],
        [3],
        [4],
        #[3],
        #[3],
        [5],
        [5],
        #[4],
        #[4],
        [6],
        #[4],
        #[5],
        #[5],
        [6],
        [7],
        #[6],
        #[6],
        [7]
        #[6],
        ] 
    )
  
    #creates the model
    model = create_model(242)

    model.summary()

    #Shuffles the data, arrtrain and arrOutput has to be shuffled the same way or classification will not work
    #arrtrain, arrOutput = shuffle(arrtrain, arrOutput, random_state=0)
    # Tries to open the weights and imports it into model if it exists
    try:
        model.load_weights("weights")
    except Exception:
        print("New Weight File")

    # Trains the model based on array
    model.fit(arrtrain, arrOutput, epochs=100, steps_per_epoch=500)

    plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)
    #saves the weights of trained model as "weights"
    model.save_weights("weights")

    #test_loss, test_acc = model.evaluate(arrpred, arrpred2)
    #print('\nTest accuracy:', test_acc)


if __name__ == "__main__":
    main()