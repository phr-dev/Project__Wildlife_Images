import sys
import pandas as pd
import cv2 as cv
import os
import glob

# project-specific custom functions
## import functions
from preprocessing import import_image_files, import_images_from_file_list



def load_data():
    """Function for loading train, validation and test datasets.

    Returns:
        tuple: 3-tuple containing (a list of) features and (one-hot-encoded) labels for train, validation and test data
    """

    dir_data_info_relative = "../data/dataset_infos/"  # the relative directory path to all data files

    # load info DataFrames
    df_train = pd.read_csv(dir_data_info_relative+f"train_dataset_info__100000_runs.csv")
    df_val = pd.read_csv(dir_data_info_relative+f"val_dataset_info__100000_runs.csv")
    df_test = pd.read_csv(dir_data_info_relative+f"test_dataset_info__100000_runs.csv")

    ## load all info data (one numpy array per image). use the list from the DataFrame to get a matching order
    dir_data_relative = "../data/"  # the relative directory path to all data files
    filepaths_train = (dir_data_relative + df_train.filepath).to_list()  # list with all image file paths
    filepaths_val = (dir_data_relative + df_val.filepath).to_list()  # list with all image file paths
    filepaths_test = (dir_data_relative + df_test.filepath).to_list()  # list with all image file paths

    X_train_list = import_images_from_file_list(file_list=filepaths_train)  # load all images
    X_val_list = import_images_from_file_list(file_list=filepaths_val)  # load all images
    X_test_list = import_images_from_file_list(file_list=filepaths_test)  # load all images

    Y_train = df_train.iloc[:, 9:]
    Y_val = df_val.iloc[:, 9:]
    Y_test = df_test.iloc[:, 9:]

    return (X_train_list, Y_train), (X_val_list, Y_val), (X_test_list, Y_test)

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