import numpy as np # helps with the math
import matplotlib.pyplot as plt # to plot error during training
import pandas as pd
import netCDF4
import os
import earthpy.plot as ep
import Neuro2

class NeuralNetwork:

    # intialize variables in class
    def __init__(self, inputs, outputs, bands):
        self.inputs  = inputs
        self.outputs = outputs
        # initialize weights as .50 for simplicity
        self.weights = np.random.rand(bands, 1)
        self.error_history = []
        self.epoch_list = []

    #activation function ==> S(x) = 1/1+e^(-x)
    def sigmoid(self, x, deriv=False):
        if deriv == True:
            return x * (1 - x)
        return 1 / (1 + np.exp(-x))

    # data will flow through the neural network.
    def feed_forward(self):
        self.hidden = self.sigmoid(np.dot(self.inputs, self.weights))

    # going backwards through the network to update weights
    def backpropagation(self):
        self.error  = self.outputs - self.hidden
        delta = self.error * self.sigmoid(self.hidden, deriv=True)
        self.weights += np.dot(self.inputs.T, delta)

    # train the neural net for 25,000 iterations
    def train(self, epochs=100000):
        for epoch in range(epochs):
            # flow forward and produce an output
            self.feed_forward()
            # go back though the network to make corrections based on the output
            self.backpropagation()
            # keep track of the error history over each epoch
            self.error_history.append(np.average(np.abs(self.error)))
            self.epoch_list.append(epoch)

    # function to predict output on new and unseen input data
    def predict(self, new_input):
        prediction = self.sigmoid(np.dot(new_input, self.weights))
        return prediction


fs = ""
fc = []
for root, dirs, files in os.walk(os.getcwd()):
    files.sort()
    for f in files:
        if f.endswith(".nc"):
            fs = f

openf = netCDF4.Dataset(fs, "r")
arr = np.zeros([openf.dimensions["Bands"].size, openf.dimensions["y"].size, openf.dimensions["x"].size])
arr[:] = openf.variables["Data"][:]

for c in range(0, openf.dimensions["Bands"].size - 1):
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
    arr[:, 2994, 253]
    ]
)
#Land Pred
arrpred2 = np.array(
    [
    arr[:, 1688, 613]
    ]
)

NN = NeuralNetwork(arrtrain, arrOutput, openf.dimensions["Bands"].size)
NN.train()

print(NN.predict(arrpred), ' - Correct: ', arrpred[0][0])
print(NN.predict(arrpred2), ' - Correct: ', arrpred2[0][0])

plt.figure(figsize=(15,5))
plt.plot(NN.epoch_list, NN.error_history)
plt.xlabel('Epoch')
plt.ylabel('Error')
plt.show()
