import cv2 as cv
import os
import glob

def import_image_files(n_images=16488):
    if os.name == "nt":
        img_files = glob.glob("..\\data\\train_features\\*.jpg")
    else:
        img_files = glob.glob("../data/train_features/*.jpg")
    image_list = []
    for file in img_files[0:n_images]:
        image_list.append(cv.imread(file))
    return image_list

def import_images_from_file_list(file_list):
    image_list = []
    for file in file_list:
        image_list.append(cv.imread(file))
    return image_list