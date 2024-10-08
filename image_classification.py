# -*- coding: utf-8 -*-
"""Image Classification.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1EUwT5ipvpnAHN1qfPc6DPgYygIU39lf2
"""

# Install necessary libraries
!pip install tensorflow
!pip install matplotlib

import os
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import load_img, img_to_array, ImageDataGenerator
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

# Define paths
base_path = '/content/drive/MyDrive/Dataset/'
train_path = os.path.join(base_path, 'seg_train')
test_path = os.path.join(base_path, 'seg_test')
pred_path = os.path.join(base_path, 'seg_pred')

# Function to load images from a directory
def load_images_from_directory(directory, target_size=(32, 32)):
    images = []
    labels = []
    label_map = {label: i for i, label in enumerate(sorted(os.listdir(directory)))}
    for label_dir in os.listdir(directory):
        label_path = os.path.join(directory, label_dir)
        if os.path.isdir(label_path):
            for img_file in os.listdir(label_path):
                img_path = os.path.join(label_path, img_file)
                img = load_img(img_path, target_size=target_size)
                img_array = img_to_array(img)
                images.append(img_array)
                labels.append(label_map[label_dir])
    return np.array(images), np.array(labels), label_map

# Load datasets
try:
    x_train, y_train, label_map_train = load_images_from_directory(train_path)
    x_test, y_test, label_map_test = load_images_from_directory(test_path)
except Exception as e:
    print(f"Error loading data: {e}")
    raise

# Ensure that data is not empty
if x_train.size == 0 or x_test.size == 0:
    raise ValueError("Loaded data is empty. Check the dataset directories.")

# Normalize images
x_train = x_train.astype('float32') / 255.0
x_test = x_test.astype('float32') / 255.0

# Encode labels
y_train = to_categorical(y_train, num_classes=len(label_map_train))
y_test = to_categorical(y_test, num_classes=len(label_map_test))

# Data Augmentation
datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)
datagen.fit(x_train)

# Build the CNN model
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dense(512, activation='relu'),
    Dropout(0.5),
    Dense(len(label_map_train), activation='softmax')  # Number of classes
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

model.summary()

# Train the model
history = model.fit(
    datagen.flow(x_train, y_train, batch_size=64),
    epochs=50,
    validation_data=(x_test, y_test)
)

# Evaluate the model
loss, accuracy = model.evaluate(x_test, y_test)
print(f'Test accuracy: {accuracy * 100:.2f}%')

# Plot training history
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='accuracy')
plt.plot(history.history['val_accuracy'], label='val_accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.ylim([0, 1])
plt.legend(loc='lower right')

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='loss')
plt.plot(history.history['val_loss'], label='val_loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(loc='upper right')
plt.show()

# Make predictions on new images
def load_and_preprocess_images(directory, target_size=(32, 32)):
    images = []
    for img_file in os.listdir(directory):
        img_path = os.path.join(directory, img_file)
        img = load_img(img_path, target_size=target_size)
        img_array = img_to_array(img)
        images.append(img_array)
    return np.array(images)

x_pred = load_and_preprocess_images(pred_path)
x_pred = x_pred.astype('float32') / 255.0

predictions = model.predict(x_pred)
predicted_classes = np.argmax(predictions, axis=1)

# Map indices to class names
inverse_label_map = {v: k for k, v in label_map_train.items()}
predicted_labels = [inverse_label_map[class_idx] for class_idx in predicted_classes]

# Output predictions
for i, label in enumerate(predicted_labels):
    print(f"Image {i}: Predicted label - {label}")