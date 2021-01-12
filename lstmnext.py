''' This code creates an LSTM that predicts the next value in the following period. '''


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error


def train_test_split(X, y, prct=.2):
    '''Splits the time series data into a train and test set'''
    X_train, X_test = X[:int((1-prct)*len(X))], X[int((1-prct)*len(X)):]
    y_train, y_test = y[:int((1-prct)*len(y))], y[int((1-prct)*len(y)):]
    
    return X_train, X_test, y_train, y_test

def formatdata(past,pred, back=1):
    ''' Format the past data and prediction data in arrays that can be fed into LSTM '''
    pastX, predY = [], []
    for i in range(len(past)-back-1): 
        pastX.append(past[i:(i+back), None])
        predY.append(pred[i + back])
    return np.array(pastX), np.array(predY)

def chooseoptions(Xtrain, Xtest, ytrain, ytest, back):
    ''' Allows to choose options currently just the amount of past data to include '''
    trainpast, trainpred = formatdata(Xtrain, ytrain, back)
    testpast,testpred = formatdata(Xtest, ytest, back)
    return trainpast, trainpred, testpast, testpred
    
def predict(model, trainpastr, testpastr):
    ''' Creates the prediction arrays ''' 
    trainPredict = model.predict(trainpastr)
    testPredict = model.predict(testpastr)
    return trainPredict, testPredict

def buildmodel(back, pastr, pred, epoch = 10, bs = 256):
    ''' Builds model with inputs given '''
    model = Sequential()
    model.add(LSTM(100))
    model.add(Dense(100))
    model.add(Dense(50))
    model.add(Dense(25))
    model.add(Dense(5))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(pastr, pred, epochs=epoch, batch_size=bs)
    
    return model

def metrics(trainpred, trainPredict, testpred, testPredict):
    ''' Prints and returns the metric data which consists of RMSE '''
    trainScore = math.sqrt(mean_squared_error(trainpred, trainPredict))
    print('Train Score: %.5f RMSE' % (trainScore))
    testScore = math.sqrt(mean_squared_error(testpred, testPredict))
    print('Test Score: %.5f RMSE' % (testScore))
    return trainScore, testScore    

#Code to take in file, create the appropriate inputs for the model, create model and results

file = "eurousddailywithrates.csv"
back = 250
df = pd.read_csv(file)
df = df.set_index(pd.DatetimeIndex(df['dt']))
df = df.drop(columns='dt')
df = df.dropna()
X = df.values
y = df["<CLOSE>"].values
X_train, X_test, y_train, y_test = train_test_split(X,y)
trpt, trpd, tstpt, tstpd = chooseoptions(X_train, X_test, y_train, y_test, back)
tstr = tstpt.reshape((-1,back,7))
trptr = trpt.reshape((-1,back,7))
model = buildmodel(back, trptr,trpd)
r1, r2 = predict(model, trptr, tstr)
model.summary()
metrics(trpd,r1,tstpd,r2)