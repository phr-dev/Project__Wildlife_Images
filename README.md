# TNP WildVision - Wildlife Image Classification in West Africa 🐒 🐆 🐗


**Welcome** to the code repository for the ***TNP WildVision*** project! 

Our team of 4 data scientists built a Streamlit app that allows for upload and fully automated classification of wildlife images into 8 distinct animal species derived from the animal population in the Taï national park in Côte d’Ivoire. The implemented classifier is based on a pretrained convolutional neural network (ConvNeXtXLarge) that was adopted to our dataset consisting of photos collected by camera traps distributed through the park. This dataset we explored and used in our modeling originated from the [Conser-vision Practice Area: Image Classification](https://www.drivendata.org/competitions/87/competition-image-classification-wildlife-conservation/) competition hosted on [drivendata.org](https://www.drivendata.org/).


## Repository Overview
- The [./functions](https://github.com/phr-dev/Project__Wildlife_Images/blob/main/functions/) directory containes the modules [data_loading.py](https://github.com/phr-dev/Project__Wildlife_Images/blob/main/functions/data_loading.py) and [preprocessing.py](https://github.com/phr-dev/Project__Wildlife_Images/blob/main/functions/preprocessing.py) which provide helper functions for data processing and loading into memory
- An mlflow-based experiment tracking functionality that can be used for model tuning is implemented [here](https://github.com/phr-dev/Project__Wildlife_Images/blob/main/functions/mlflow_utils.py)
- The slide deck used in the final project presentation can be found in the file [Project_Presentation.pdf](https://github.com/phr-dev/Project__Wildlife_Images/blob/main/Project_Presentation.pdf).


## Setup

If you would like to use (parts of) the code, you can run the following lines in your terminal for setting up a virtual environment containing the necessary packages.

```BASH
make setup

#or

pyenv local 3.11.3
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```