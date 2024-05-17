import shutil
from pathlib import Path

import numpy as np
import pandas as pd


def copy_files_to_directories(input_filepaths: list, output_directories: str) -> None:

    # create the unique output directories if not existing
    for directory in np.unique(output_directories):
        Path(directory).mkdir(parents=True, exist_ok=True)

    # copy the files
    for filepath, output_directory in zip(input_filepaths, output_directories):
        shutil.copy2(src=filepath,
                    dst=output_directory
                    )
        
    return None

def build_dataset_directories_with_categories(fraction_train:float|int = 1.0,
                                              fraction_val:float|int = 1.0,
                                              fraction_test:float|int = 1.0,
                                              seed:int = 42,
                                              ask_for_choice_confirmation:bool = True,
                                              test_run:bool = True,
                                              print_status:bool = True,) -> None:
    """Function for generating and populating the (train, validation and test) data target directories containing one subdirectory per class.

    Args:
        fraction_train (float | int, optional): Fraction of training data that is sampled. Defaults to 1.0.
        fraction_val (float | int, optional): Fraction of training validation that is sampled. Defaults to 1.0.
        fraction_test (float | int, optional): Fraction of training test that is sampled. Defaults to 1.0.
        seed (int, optional): _description_. Defaults to 42.
        ask_for_choice_confirmation (bool, optional): Boolean switch for asking the user to continue in case of a chosen fraction <1. Defaults to True.
        test_run (bool, optional): Boolean switch for the execution of a test run -- data selection is performed but no files are actually copied. Defaults to True.
        print_status (bool, optional): Boolean switch for printing status info messages. Defaults to True.

    Returns:
        _type_: returns None
    """

    dir_data_parent_relative = "../data/"  # the relative directory path to all data files
    dir_data_info_relative = "../data/dataset_infos/"  # the relative directory path to all data files

    # load info DataFrames
    df_train = pd.read_csv(dir_data_info_relative+f"train_dataset_info__100000_runs.csv")
    df_val = pd.read_csv(dir_data_info_relative+f"val_dataset_info__100000_runs.csv")
    df_test = pd.read_csv(dir_data_info_relative+f"test_dataset_info__100000_runs.csv")

    # sample the data
    if not (0<=fraction_train<=1) or not (0<=fraction_val<=1) or not (0<=fraction_test<=1):
        print("Chosen fractions are outside of valid range [0, 1].")
        print("Function execution has been aborted.\n")
        return None
    if (0<fraction_train<1) or (0<fraction_val<1) or (0<fraction_test<1):
        df_train = df_train.sample(frac=fraction_train, random_state=seed)
        df_val = df_val.sample(frac=fraction_val, random_state=seed)
        df_test = df_test.sample(frac=fraction_test, random_state=seed)

        print(f"Number of train data instances sampled      (corresponding to {fraction_train*100:6.2f}%): {df_train.shape[0]:7d}")
        print(f"Number of validation data instances sampled (corresponding to {fraction_val*100:6.2f}%): {df_val.shape[0]:7d}")
        print(f"Number of test data instances sampled       (corresponding to {fraction_test*100:6.2f}%): {df_test.shape[0]:7d}\n")

        if ask_for_choice_confirmation:
            user_input = input("Do you want to continue? (yes / no): ")
            while user_input not in {"yes", "no"}:
                user_input = input("Please enter 'yes' or 'no': ")

            if user_input == "no":
                print("No files are copied, function execution has been aborted.\n")
                return None
        if test_run:
            print("'test_run' is set to True.")
            print("No files are copied, function execution has been aborted.\n")
            return None
    else:
        print("All data instances are selected.\n")
        if test_run:
            print("'test_run' is set to True.")
            print("No files are copied, function execution has been aborted.\n")
            return None

    ## load all info data (one numpy array per image). use the list from the DataFrame to get a matching order
    filepaths_train = (dir_data_parent_relative + df_train.filepath).to_list()  # list with all train image file paths
    filepaths_val = (dir_data_parent_relative + df_val.filepath).to_list()  # list with all validation image file paths
    filepaths_test = (dir_data_parent_relative + df_test.filepath).to_list()  # list with all test image file paths
    filepaths_all = np.concatenate([filepaths_train, filepaths_val, filepaths_test])  # list with all image file paths

    # get the labels
    labels_train = df_train.animal_label.to_list()
    labels_val = df_val.animal_label.to_list()
    labels_test = df_test.animal_label.to_list()

    # copy all files into corresponding directories
    dir_data_relative = dir_data_parent_relative+"dataset_split_categories/"
    ## define the dataset output directories
    dir_data_train = dir_data_relative+"train"
    dir_data_val = dir_data_relative+"validation"
    dir_data_test = dir_data_relative+"test"

    ## construct the output/target subdirectory lists
    target_directories_train = [dir_data_train+"/"+label for label in labels_train]
    target_directories_val = [dir_data_val+"/"+label for label in labels_val]
    target_directories_test = [dir_data_test+"/"+label for label in labels_test]
    target_directories_all = np.concatenate([target_directories_train, target_directories_val, target_directories_test])

    ## remove the target parent directory for all data (if existing)
    if print_status:
        print("Potentially existing target directories are being deleted ...")
    try:
        shutil.rmtree(dir_data_relative)
        if print_status:
            print("DONE\n")
    except FileNotFoundError as e:
        print("Target directory did not exist.")
        if print_status:
            print("Done\n")
        # print(e)

    if print_status:
        print("Files are being copied into directories ...")
    copy_files_to_directories(filepaths_all, target_directories_all)  # train data
    if print_status:
        print("DONE\n")

    return None