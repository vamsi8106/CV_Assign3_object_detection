# -*- coding: utf-8 -*-
"""M22RM002_Q4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SZ9mp6Q0xtVQPEXcSqWi1BiplPxgqOoa
"""

from google.colab import drive
drive.mount('/content/drive')

import numpy as np
import cv2
from skimage.feature import hog
from sklearn.svm import LinearSVC
from google.colab.patches import cv2_imshow
import glob
import math
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn import preprocessing

"""## METHOD-1"""

import cv2
from skimage.feature import hog
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
import os
import joblib
# Load deer and non-deer image patches from folders
deer_dir= "/content/drive/MyDrive/Colab Notebooks/CV_ASSIGN_3/train_4_ques/deer"
non_deer_dir= "/content/drive/MyDrive/Colab Notebooks/CV_ASSIGN_3/train_4_ques/non_deer"

deer_images = []
non_deer_images = []

for file in os.listdir(deer_dir):
    if file.endswith('.jpg'):
        img = cv2.imread(os.path.join(deer_dir, file))
        if img.shape[-1] != 3:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        deer_images.append(img)

for file in os.listdir(non_deer_dir):
    if file.endswith('.jpg'):
        img = cv2.imread(os.path.join(non_deer_dir, file))
        if img.shape[-1] != 3:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        non_deer_images.append(img)

# Compute HOG features for image patches
hog_features = []

for img in deer_images + non_deer_images:
    # Preprocess image patch (e.g., resize, normalize, grayscale)
    img = cv2.resize(img, (64, 64))
    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Compute HOG features
    hog_feats = hog(img, orientations=9, pixels_per_cell=(8, 8),
                    cells_per_block=(2, 2), block_norm='L2-Hys')
    hog_features.append(hog_feats)

# Train SVM classifier
X_train, X_test, y_train, y_test = train_test_split(hog_features, [1]*len(deer_images) + [0]*len(non_deer_images),
                                                    test_size=0.2, random_state=42)

svm = LinearSVC(random_state=42)
svm.fit(X_train, y_train)
joblib.dump(svm, 'model1.joblib')
# Evaluate classifier
accuracy = svm.score(X_test, y_test)
print('Accuracy: {:.2f}%'.format(accuracy * 100))

"""## METHOD-2"""

import cv2
import numpy as np
import os
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score
from skimage.feature import hog

# Define paths to the folders containing deer and non-deer images
deer_path= "/content/drive/MyDrive/Colab Notebooks/CV_ASSIGN_3/train_4_ques/deer"
non_deer_path= "/content/drive/MyDrive/Colab Notebooks/CV_ASSIGN_3/train_4_ques/non_deer"

# Define HOG parameters
hog_params = {'orientations': 9,
              'pixels_per_cell': (8, 8),
              'cells_per_block': (2, 2),
              'block_norm': 'L2-Hys'}

# Compute HOG features for all the deer images
deer_features = []
for filename in os.listdir(deer_path):
    img = cv2.imread(os.path.join(deer_path, filename))
    img = cv2.resize(img, (64, 64))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hog_features = hog(img, **hog_params)
    deer_features.append(hog_features)

# Compute HOG features for all the non-deer images
non_deer_features = []
for filename in os.listdir(non_deer_path):
    img = cv2.imread(os.path.join(non_deer_path, filename))
    img = cv2.resize(img, (64, 64))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hog_features = hog(img, **hog_params)
    non_deer_features.append(hog_features)

# Combine the features and labels for SVM training
X_train = np.vstack((deer_features, non_deer_features))
y_train = np.hstack((np.ones(len(deer_features)), np.zeros(len(non_deer_features))))

# Train the SVM classifier
clf = LinearSVC()
clf.fit(X_train, y_train)

# Test the classifier on a few samples
y_pred = clf.predict(X_train)
import joblib

# Save the trained model
joblib.dump(clf, 'svm_model.joblib')

print('Training accuracy:', accuracy_score(y_train, y_pred))

"""## TEST WITH METHOD-1"""

def get_filepaths(directory):
   
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(filename)
            file_paths.append(filepath)
            print(file_paths)

    return file_paths

def bounding_box_1(test_img):
    window_size = (64, 64)
    step_size = (16, 16)
    # Initialize an empty list to store the detected deer bounding boxes
    detected_deer_boxes = []
    clf = joblib.load('/content/model1.joblib')
    # Slide the window over the test image and classify each window
    for y in range(0, test_img.shape[0] - window_size[1], step_size[1]):
        for x in range(0, test_img.shape[1] - window_size[0], step_size[0]):
            window = test_img[y:y+window_size[1], x:x+window_size[0], :]
            window_gray = cv2.cvtColor(window, cv2.COLOR_BGR2GRAY)
            hog_features = hog(window_gray, **hog_params)
            pred = clf.predict([hog_features])
            if pred == 1:
                detected_deer_boxes.append((x, y, x+window_size[0], y+window_size[1]))

    # Apply non-maximum suppression to remove overlapping bounding boxes
    detected_deer_boxes = cv2.groupRectangles(detected_deer_boxes, 1, 1)

    # Draw the detected bounding boxes on the test image
    for box in detected_deer_boxes[0]:
        cv2.rectangle(test_img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)

    # Show the test image with the detected bounding boxes
    return test_img

testing_path="/content/drive/MyDrive/Colab Notebooks/CV_ASSIGN_3/deer-test"
images_paths = get_filepaths(testing_path)
height = 250
width = 250
training_images = np.ndarray(shape=(len(images_paths), height*width), dtype=np.float64)
test_list=[]
for i in range(len(images_paths)):
    path= testing_path+'/'+ images_paths[i]
    read_image = cv2.imread(path)
    resized_image = cv2.resize(read_image, (width, height))
    image=bounding_box_1(resized_image)
    test_list.append(image)

for i in range(len(test_list)):
    img = test_list[i]
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.subplot(3,3,1+i)
    plt.imshow(img, cmap='gray')
    plt.tick_params(labelleft='off', labelbottom='off', bottom='off',top='off',right='off',left='off', which='both')
plt.show()

"""## TEST WITH METHOD-2"""

def bounding_box_2(test_img):
    window_size = (64, 64)
    step_size = (16, 16)
    # Initialize an empty list to store the detected deer bounding boxes
    detected_deer_boxes = []
    clf = joblib.load('/content/svm_model.joblib')
    # Slide the window over the test image and classify each window
    for y in range(0, test_img.shape[0] - window_size[1], step_size[1]):
        for x in range(0, test_img.shape[1] - window_size[0], step_size[0]):
            window = test_img[y:y+window_size[1], x:x+window_size[0], :]
            window_gray = cv2.cvtColor(window, cv2.COLOR_BGR2GRAY)
            hog_features = hog(window_gray, **hog_params)
            pred = clf.predict([hog_features])
            if pred == 1:
                detected_deer_boxes.append((x, y, x+window_size[0], y+window_size[1]))

    # Apply non-maximum suppression to remove overlapping bounding boxes
    detected_deer_boxes = cv2.groupRectangles(detected_deer_boxes, 1, 1)

    # Draw the detected bounding boxes on the test image
    for box in detected_deer_boxes[0]:
        cv2.rectangle(test_img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)

    # Show the test image with the detected bounding boxes
    return test_img

testing_path="/content/drive/MyDrive/Colab Notebooks/CV_ASSIGN_3/deer-test"
images_paths = get_filepaths(testing_path)
height = 250
width = 250
training_images = np.ndarray(shape=(len(images_paths), height*width), dtype=np.float64)
test_list=[]
for i in range(len(images_paths)):
    path= testing_path+'/'+ images_paths[i]
    read_image = cv2.imread(path)
    resized_image = cv2.resize(read_image, (width, height))
    image=bounding_box_2(resized_image)
    test_list.append(image)

for i in range(len(test_list)):
    img = test_list[i]
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.subplot(3,3,1+i)
    plt.imshow(img, cmap='gray')
    plt.tick_params(labelleft='off', labelbottom='off', bottom='off',top='off',right='off',left='off', which='both')
plt.show()

