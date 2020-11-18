import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout, Flatten, Dense, Conv2D, MaxPooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import optimizers, initializers, regularizers, metrics
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

# seed = 0
# np.random.seed(seed)
# tf.random.set_seed(3)

train_datagen = ImageDataGenerator(rescale=1./255,
                                  horizontal_flip=True,
                                  width_shift_range=0.1,
                                  height_shift_range=0.1, 
                                  #rotation_range=5,      
                                  #shear_range=0.7,       
                                  zoom_range=[0.9, 2.2],  
                                  vertical_flip=True,      
                                  fill_mode='nearest') 


# ---------------------- training data set -------------------------- #
train_generator = train_datagen.flow_from_directory(
       './dataset/train', 
       target_size=(224, 224),
       batch_size=5,
       class_mode='binary')


# ---------------------- test data set -------------------------- #
test_datagen = ImageDataGenerator(rescale=1./255)  

test_generator = test_datagen.flow_from_directory(
       './dataset/tests',  
       target_size=(224, 224),
       batch_size=5,
       class_mode='binary')

path, dirs, files = next(os.walk("./dataset/tests"))
classification_num = len(dirs)

# Design Model layer
model = Sequential()
model.add(Conv2D(32, (3, 3), input_shape=(224,224,3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(32, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(64, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Flatten())
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(classification_num))
model.add(Activation('softmax'))


# compile model 
model.compile(loss='sparse_categorical_crossentropy',
              optimizer=optimizers.Adam(learning_rate=0.0002),
              metrics=['accuracy'])




# model optimization
now = datetime.datetime.now()
capdate = now.strftime( '%Y%m%d' )
captime = now.strftime( '%H%M%S' )
nowdate = capdate+'_'+captime
MODEL_DIR = './lego_model/'+nowdate
if not os.path.exists(MODEL_DIR):
    os.mkdir(MODEL_DIR)
    
modelpath = MODEL_DIR + '/{epoch:02d}-{val_loss:.4f}.hdf5'
checkpointer = ModelCheckpoint(filepath=modelpath, monitor='val_loss', verbose=1, save_best_only=True)
early_stopping_callback = EarlyStopping(monitor='val_loss', patience=10)

model.summary()


# run training
history = model.fit_generator(train_generator,
                    steps_per_epoch=50, 
                    epochs=25,
                    validation_data=test_generator,
                    validation_steps=4,
                    callbacks=[early_stopping_callback, checkpointer])

# model.save_weights('model.h5')
# model_json = model.to_json()
# with open('model.json', "w") as json_file:
#     json_file.write(model_json)
# json_file.close()

# load part 
# from keras.models import model_from_json
# json_file = open("model.json", 'r')
# loaded_model_json = json_file.read()
# json_file.close()
# model = model_from_json(loaded_model_json)
# model.load_weights("model.h5")

# show accuracy graph
acc= history.history['accuracy']
val_acc= history.history['val_accuracy']
y_vloss = history.history['val_loss']
y_loss = history.history['loss']

x_len = np.arange(len(y_loss))  
plt.plot(x_len, acc, marker='.', c="red", label='Trainset_acc')
plt.plot(x_len, val_acc, marker='.', c="lightcoral", label='Testset_acc')
plt.plot(x_len, y_vloss, marker='.', c="cornflowerblue", label='Testset_loss')
plt.plot(x_len, y_loss, marker='.', c="blue", label='Trainset_loss')

plt.legend(loc='upper right') 
plt.grid()
plt.xlabel('epoch')
plt.ylabel('loss/acc')
plt.show()
