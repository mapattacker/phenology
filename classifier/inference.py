import os

# os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

from config import MODEL_DIR, IMG_SIZE


model = load_model(MODEL_DIR)



def predict(file):
    """prediction, 0=Flower, 1=Not Flower"""

    # get probability of each class, & convert to class name
    predicted = model.predict(file)
    predicted_label = np.argmax(predicted, axis=1)

    return predicted_label


if __name__ == "__main__":
    dir_ = "eval_data/Cratoxylum maingayi/Flowering/"
#     dir_ = "img/flowernot"
    
    for path in os.listdir(dir_):
        if path.endswith(".jpeg"):
            image_path = os.path.join(dir_, str(path))
            image = tf.keras.preprocessing.image.load_img(image_path, target_size=(IMG_SIZE, IMG_SIZE))
            input_arr = tf.keras.preprocessing.image.img_to_array(image)
            input_arr = np.array([input_arr])

            x = predict(input_arr)
            print(x[0])