import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
# from tensorflow.keras.models import model_from_json
# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
model = tensorflow.keras.models.load_model('model.hdf5')
# load part 

# json_file = open("model.json", 'r')
# loaded_model_json = json_file.read()
# json_file.close()
# model = model_from_json(loaded_model_json)
# model.load_weights("model.h5")


# Create the array of the right shape to feed into the keras model
# The 'length' or number of images you can put into the array is
# determined by the first position in the shape tuple, in this case 1.
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
for i in range(1,7):
    # Replace this with the path to your image
    # image = Image.open('./testimg/ETY_{}.jpg'.format(i))
    # image = Image.open('./testimg/DSR_{}.jpg'.format(i))
    # image = Image.open('./testimg/APL_{}.jpg'.format(i))
    image = Image.open('./testimg/WAL_{}.jpg'.format(i))
    # image = Image.open('./testimg/CAR_{}.jpg'.format(i))
    


    #resize the image to a 224x224 with the same strategy as in TM2:
    #resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)

    #turn the image into a numpy array
    image_array = np.asarray(image)

    # display the resized image
    image.show()

    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

    # Load the image into the array
    data[0] = normalized_image_array

    # run the inference
    prediction = model.predict(data)
    print(prediction)
    # model.summary()