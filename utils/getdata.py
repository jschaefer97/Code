#%%

import pandas as pd
import os
import importlib 
import pickle
import re
from loguru import logger

#%%

def list_filepaths_in_dir(directory):
    """
    Return a list of full filepaths for all files in the given directory.
    """
    if not os.path.exists(directory):
        return logger.warning(f"Directory does not exist: {directory}")
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]

def extract_period(filename):
    """
    Extracts the period string (e.g., 'p1', 'p2', ...) from a filename.
    """
    match = re.search(r'(p\d+)', filename)
    return match.group(1) if match else None

def _save_xlsx(df, file_path, dataset, replace=False):
    """
    Save a pandas DataFrame to a specified folder as an Excel file, 
    only if no file with the same name exists.

    Parameters:
    df (pandas.DataFrame): The DataFrame to save.
    file_path (str): The folder path where the file should be saved.
    dataset (str): The dataset (including extension, e.g., "data.xlsx").

    Returns:
    str: Full path of the saved file or a message if the file already exists.
    """

    # Ensure the folder exists
    os.makedirs(file_path, exist_ok=True)

    # Construct the full file path with extension
    full_file_path = os.path.join(file_path, f"{dataset}.xlsx")

    # Save the DataFrame as an Excel file
    if replace:
        df.to_excel(full_file_path, index=True)
        logger.info(f"DataFrame saved successfully at: {full_file_path}")
    elif not os.path.exists(full_file_path):  # Avoid overwriting
        df.to_excel(full_file_path, index=True)
        logger.info(f"DataFrame saved successfully at: {full_file_path}")
    else:
        logger.info(f"File already exists at: {full_file_path}")

    return full_file_path

def save_csv(df, file_path, dataset, replace=False):
    """
    Save a pandas DataFrame to a specified folder as a CSV file,
    only if no file with the same name exists.

    Parameters:
    df (pandas.DataFrame): The DataFrame to save.
    file_path (str): The folder path where the file should be saved.
    dataset (str): The dataset (file name without extension, e.g., "data").

    Returns:
    str: Full path of the saved file or a message if the file already exists.
    """

    # Ensure the folder exists
    os.makedirs(file_path, exist_ok=True)

    # Construct the full file path with extension
    full_file_path = os.path.join(file_path, f"{dataset}.csv")

    # Save the DataFrame as a CSV file
    if replace:
        df.to_csv(full_file_path, index=True)
        logger.info(f"DataFrame saved successfully at: {full_file_path}")
    elif not os.path.exists(full_file_path):  # Avoid overwriting
        df.to_csv(full_file_path, index=True)
        logger.info(f"DataFrame saved successfully at: {full_file_path}")
    else:
        logger.info(f"File already exists at: {full_file_path}")

    return full_file_path

def _load_xlsx(file_path, dataset):
    """
    Load a pandas DataFrame from an Excel file.

    Parameters:
    file_path (str): The folder path where the file is located.
    dataset (str): The dataset name (without extension).

    Returns:
    pandas.DataFrame: The loaded DataFrame.
    """
    # Construct the full file path with extension
    full_file_path = os.path.join(file_path, f"{dataset}.xlsx")
    
    # Check if the file exists
    if not os.path.exists(full_file_path):
        raise FileNotFoundError(f"File not found at: {full_file_path}")
    
    # Load the Excel file into a DataFrame
    df = pd.read_excel(full_file_path)
    logger.info(f"DataFrame loaded successfully from: {full_file_path}")

    return df

def _save_object(obj, file_path, file_name):
    """
    Save a Python object to a file using pickle.

    Parameters:
    obj (object): The Python object to save.
    file_path (str): The folder path where the file should be saved.
    dataset (str): The name of the file without extension.

    Returns:
    str: Full path of the saved file.
    """
    # Ensure the folder exists
    os.makedirs(file_path, exist_ok=True)

    # Construct the full file path with extension
    full_file_path = os.path.join(file_path, file_name)

    # Save the object using pickle
    with open(full_file_path, 'wb') as file:
        pickle.dump(obj, file)

    logger.info(f"Object saved successfully at: {full_file_path}")

    return full_file_path

def _load_object(file_path, file_name):
    """
    Load a Python object from a file using pickle.

    Parameters:
    file_path (str): The folder path where the file is located.
    dataset (str): The name of the file without extension.

    Returns:
    object: The loaded Python object.
    """
    # Construct the full file path with extension
    full_file_path = os.path.join(file_path, file_name)
    
    # Check if the file exists
    if not os.path.exists(full_file_path):
        raise FileNotFoundError(f"File not found at: {full_file_path}")

    # Load the object using pickle
    with open(full_file_path, 'rb') as file:
        obj = pickle.load(file)

    logger.info(f"Object loaded successfully from: {full_file_path}")

    return obj

# Consolidated repetitive file existence checks into a helper function
def _file_exists(file_path, file_name):
    return os.path.exists(os.path.join(file_path, file_name))

# Helper function to dynamically load dataset objects
def _load_dataset_mapping_object(dataset):
    dataset_mapping = f"mappings.{dataset}"
    try:
        dataset_module = importlib.import_module(dataset_mapping)
    except ImportError as e:
        raise ImportError(f"Failed to import dataset mapping '{dataset_mapping}': {e}. Check if the dataset exists in the 'mappings' directory.")
    return getattr(dataset_module, dataset)

class Getdata:
    """
    A utility class for saving and loading datasets in various formats (Excel, Pickle).
    """

    @staticmethod
    def mapping(file_path, dataset):
        """
        Load or save a dataset in Pickle format.

        Parameters:
        file_path (str): The folder path where the file is located or will be saved.
        dataset (str): The dataset name (without extension).

        Returns:
        object: The loaded dataset object.
        """
        file_name = f"{dataset}.pkl"

        # Check if the file already exists
        if _file_exists(file_path, file_name):
            dataset_object = _load_object(file_path, file_name)
            logger.info("File exists and is loaded in.")
        else:
            # Dynamically load the dataset object and save it as a Pickle file
            dataset_object = _load_dataset_mapping_object(dataset)
            _save_object(dataset_object, file_path, file_name)

        return dataset_object



