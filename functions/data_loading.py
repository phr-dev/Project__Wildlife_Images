import sys
import numpy as np
import pandas as pd
import cv2 as cv
import os
import glob


def get_label_name_from_filename(filename: str) -> str:
    """returns the image category given its filename
    
    Args:
        filename (str): the filename

    Returns:
        str: the category label (name of the animal)
    """

    df_info__all = pd.read_csv("../data/data_info__all.csv")  # DataFrame containing all file info (including the labels)

    ID = filename.rstrip(".jpg")    
    label_str = df_info__all.query("id == @ID")["animal_label"].values[0]

    return label_str


def import_image_files(n_images: int = 16488) -> list[np.ndarray]:
    """Return a list of numpy.ndarrays containing a given number of images from the training dataset.

    Args:
        n_images (int, optional): Number of images to load from the training set and return. Defaults to 16488, which is the total number of images in the training set.

    Returns:
        list[np.ndarray]: a list containing image data in form of numpy.ndarray
    """

    if os.name == "nt":
        img_files = glob.glob("..\\data\\train_features\\*.jpg")
    else:
        img_files = glob.glob("../data/train_features/*.jpg")
    image_list = []
    for file in img_files[0:n_images]:
        image_list.append(cv.imread(file))
    
    return image_list


def import_images_from_file_list(file_list: list[str]) -> list[np.ndarray]:
    """Return a list of numpy.ndarrays containing images read from files passed as the argument.

    Args:
        file_list (list[str]): list of image files to load and return.

    Returns:
        list[np.ndarray]: a list containing image data in form of numpy.ndarray
    """

    image_list = []
    for file in file_list:
        image_list.append(cv.imread(file))
    
    return image_list


def load_data():
    """Function for loading train, validation and test datasets.

    Returns:
        tuple: 3-tuple containing (a list of) features and (one-hot-encoded) labels for train, validation and test data.
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

