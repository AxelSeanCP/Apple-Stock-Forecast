# -*- coding: utf-8 -*-
"""Timeseries_Model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_vYvXH0FCI1hM_-2IPKEJHZJgRVl3J4r
"""

import numpy as np
import pandas as pd
from keras.layers import Dense, LSTM, Dropout
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

df = pd.read_csv('AAPL.csv')
df.head(10)

target_columns = ['Date', 'Close']
df = df[target_columns]
df.head()

df.info()

threshold_mae = (df['Close'].max() - df['Close'].min()) * 10/100
print(threshold_mae) #mae model harus lebih kecil dari ini

data_train, data_test = train_test_split(df, test_size=0.2, random_state=69, shuffle=False)

dates = data_train['Date'].values
stock = data_train['Close'].values
stock_test = data_test['Close'].values

plt.figure(figsize=(15,5))
plt.plot(dates,stock)
plt.title('Apple Stock Price', fontsize=20)
plt.show()

min_max_scaler = MinMaxScaler()
stock = stock.reshape(-1,1)
stock_test = stock_test.reshape(-1,1)
min_max_scaler.fit(stock)

stock = min_max_scaler.transform(stock)
stock_test = min_max_scaler.transform(stock_test)

print(stock)
print(stock_test)

class BerhentiBos(tf.keras.callbacks.Callback):
  def __init__(self, sabar_mae=100, sabar_loss=100):
    super(BerhentiBos, self).__init__()
    self.sabar_mae = sabar_mae
    self.sabar_loss = sabar_loss
    self.limit_mae = sabar_mae
    self.limit_loss = sabar_loss

  def on_epoch_end(self, epoch, logs={}):
    if logs.get('mae')<threshold_mae and logs.get('val_mae')<threshold_mae:
      self.sabar_mae -= 1
    else:
      self.sabar_mae += 1

    if logs.get('loss')>threshold_mae or logs.get('val_loss')>threshold_mae:
      self.sabar_loss -= 1
    else:
      self.sabar_loss += 1

    if self.sabar_mae == 0:
      print(f"The model MAE has been below threshold for {self.limit_mae} epochs, Stopping training immediatly!!!")
      self.model.stop_training = True
    elif self.sabar_loss == 0:
      print(f"The model loss has been above threshold for {self.limit_loss} epochs, Stopping training immediatly!!!")
      self.model.stop_training = True

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
  ds = tf.data.Dataset.from_tensor_slices(series)
  ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
  ds = ds.flat_map(lambda w: w.batch(window_size+1))
  ds = ds.shuffle(shuffle_buffer)
  ds = ds.map(lambda w: (w[:-1], w[-1:]))
  return ds.batch(batch_size).prefetch(1)

train_set = windowed_dataset(stock, window_size=50, batch_size=100,shuffle_buffer=1000)
test_set = windowed_dataset(stock_test, window_size=50, batch_size=100, shuffle_buffer=1000)
model = tf.keras.Sequential([
    LSTM(64, return_sequences=True),
    LSTM(64),
    Dense(32, activation="relu"),
    Dense(12, activation="relu"),
    Dropout(0.5),
    Dense(1)
])

model.compile(
    optimizer=tf.keras.optimizers.SGD(learning_rate=0.001, momentum=0.9),
    loss=tf.keras.losses.Huber(),
    metrics=['mae']
)

berhenti_bos = BerhentiBos(sabar_mae=25)
mymodel = model.fit(
    train_set,
    epochs=100,
    validation_data=test_set,
    callbacks=[berhenti_bos],
    verbose=2
)

plt.plot(mymodel.history['loss'])
plt.plot(mymodel.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='center right')
plt.show()

plt.plot(mymodel.history['mae'])
plt.plot(mymodel.history['val_mae'])
plt.title('Model MAE')
plt.ylabel('MAE')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='center right')
plt.show()