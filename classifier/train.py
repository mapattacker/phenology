"""refactored from https://colab.research.google.com/github/keras-team/keras-io/blob/master/examples/vision/ipynb/image_classification_efficientnet_fine_tuning.ipynb#scrollTo=r0HWGRFjPwCS
"""

from config import *

import matplotlib.pyplot as plt
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.preprocessing import image_dataset_from_directory
from tensorflow.keras.models import Sequential
from tensorflow.keras import layers
import tensorflow as tf


def train_val_split(DATA_DIR, IMG_SIZE):
    val_data = image_dataset_from_directory(
                    DATA_DIR,
                    labels="inferred",
                    label_mode="int",
                    color_mode="rgb",
                    batch_size=32,
                    image_size=(IMG_SIZE, IMG_SIZE),
                    validation_split=0.2,
                    subset="training",
                    seed=1
                )

    train_data = image_dataset_from_directory(
                    DATA_DIR,
                    labels="inferred",
                    label_mode="int",
                    color_mode="rgb",
                    batch_size=32,
                    image_size=(IMG_SIZE, IMG_SIZE),
                    validation_split=0.2,
                    subset="validation",
                    seed=1
                )

    train_data = train_data.map(lambda x, y: (x, tf.one_hot(y, depth=NUM_CLASSES)))
    val_data = val_data.map(lambda x, y: (x, tf.one_hot(y, depth=NUM_CLASSES)))

    train_data = train_data.cache().prefetch(buffer_size=tf.data.AUTOTUNE)
    val_data = val_data.cache().prefetch(buffer_size=tf.data.AUTOTUNE)

    return train_data, val_data


def plot_hist(hist, metric="accuracy"):
    """plot results, metric can be 'accuracy' or 'loss' """
    plt.plot(hist.history[metric])
    plt.plot(hist.history[f"val_{metric}"])
    plt.title("model accuracy")
    plt.ylabel(metric)
    plt.xlabel("epoch")
    plt.legend(["train", "validation"], loc="upper left")
    plt.show()


def model_arch(NUM_CLASSES, IMG_SIZE, LR):
    """efficientnet transfer learning"""
    inputs = layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    img_augmentation = Sequential(
        [
            layers.RandomRotation(factor=0.15),
            layers.RandomTranslation(height_factor=0.1, width_factor=0.1),
            layers.RandomFlip(),
            layers.RandomContrast(factor=0.1),
        ],
        name="img_augmentation",
    )

    x = img_augmentation(inputs)
    # model = EfficientNetB0(include_top=False, input_tensor=x, weights="imagenet")
    model = EfficientNetB0(include_top=False, input_tensor=x, weights='model/efficientnetb0_notop.h5')

    # Freeze the pretrained weights
    model.trainable = False

    # Rebuild top
    x = layers.GlobalAveragePooling2D(name="avg_pool")(model.output)
    x = layers.BatchNormalization()(x)

    top_dropout_rate = 0.2
    x = layers.Dropout(top_dropout_rate, name="top_dropout")(x)
    outputs = layers.Dense(NUM_CLASSES, activation="softmax", name="pred")(x)

    # Compile
    model = tf.keras.Model(inputs, outputs, name="EfficientNet")
    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-2)
    model.compile(
        optimizer=optimizer, 
        loss="binary_crossentropy", 
        metrics=["accuracy"]
    )
    return model


if __name__ == "__main__":
    train_data, val_data = train_val_split(DATA_DIR, IMG_SIZE, LR)
    model = model_arch(NUM_CLASSES, IMG_SIZE)
    
    checkpointer = ModelCheckpoint(filepath='./model', 
                            verbose=1, 
                            save_best_only=True)
    
    hist = model.fit(train_data, 
                     epochs=EPOCH, 
                     validation_data=val_data,
                     callbacks=[checkpointer],
                     verbose=1)
