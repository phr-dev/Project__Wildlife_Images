import pydeck as pdk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import random
import base64
import streamlit as st
import time

# Streams the inputted text with a small time delay
def get_started(timed_text):
        for word in timed_text.split(" "):
            yield word + " "
            time.sleep(0.1)

# Creates the user name input widget
def user_name():
        text_input = st.text_input(
            "Provide Username 👇",
            key="text_input",
            disabled=st.session_state.disabled,
            placeholder="Ex. J. Goodall"
        )
        return text_input

# Creates the dictionary that contains information about most frequent animal count per site
def create_dictionary():
    train_features = pd.read_csv("../data/train_features.csv")
    train_labels = pd.read_csv("../data/train_labels.csv")

    df = pd.merge(train_features, train_labels, on="id").drop(columns=["filepath", 'id', 'blank'])
    df.columns = [column.replace('_','/').capitalize() for column in df.columns]

    # Create array of unique sites
    array_of_sites = sorted(df.Site.unique())

    # Create dictionary to store sites and most frequent animal + counts
    dictionary = {}

    # For every site location get the needed information
    for site in array_of_sites:
        sites = pd.DataFrame(df.groupby('Site').value_counts()[site].reset_index())
        for column_name, value in sites.iloc[0].items():
            if value == 1.0:
                dictionary[site] = (column_name, sites['count'].max())
                break
    
    return dictionary

# Turns images into an html compatible format
def get_base64_image(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Function to generate random coordinates within specified boundaries    
def generate_random_coordinates(min_lat, max_lat, min_lon, max_lon):
    new_lat = round(random.uniform(min_lat, max_lat),2)
    new_lon = round(random.uniform(min_lon, max_lon),2)
    return new_lat, new_lon

# Function to create map dataframe, animal colors dictionary and provides animal location clusters
def create_map_df(seed=None):
    if seed is not None:
        random.seed(seed)

    # Define boundaries for specific animals
    animal_locations_min_max = {
            'Antelope/duiker': (5.7, 6.1, -7.22, -6.93),
            'Bird': (5.2, 6, -7.2, -6.9),
            'Civet/genet': (5.25, 5.55, -7.22, -6.91),
            'Hog': (5.4, 5.7, -7.2, -7.0),
            'Leopard': (5.7, 6.1, -7.34, -7.2),
            'Monkey/prosimian': (5.4, 6.08, -7.26, -7.01),
            'Rodent': (5.3, 6.1, -7.25, -6.9)
            }

    animal_colors = {
            'Antelope/duiker': [255, 0, 0, 150],
            'Bird': [0, 0, 255, 150],
            'Civet/genet': [139, 0, 0, 150],
            'Leopard': [255, 192, 203, 150],
            'Monkey/prosimian': [0, 128, 0, 150],
            'Rodent': [255, 255, 0, 150],
            'Hog': [128, 0, 128, 150]
            }

    # Initialize an empty list to store dictionaries for each entry
    data = []

    # Iterate over the dictionary items and construct a dictionary for each entry
    dictionary = create_dictionary()

    for site, (animal, count) in dictionary.items():
        min_lat, max_lat, min_lon, max_lon = animal_locations_min_max[animal]
        new_lat, new_lon = generate_random_coordinates(min_lat, max_lat, min_lon, max_lon)
        data.append({
            'site_list': site,
            'animal_list': animal,
            'latitude': new_lat,
            'longitude': new_lon,
            'animal_colors_list': animal_colors[animal],
            'max_count_list': count
            })

    # Create DataFrame from the list of dictionaries
    map_df = pd.DataFrame(data)

   # Calculate weighted mean latitude and longitude for each animal
    central_points = map_df.groupby('animal_list').apply(lambda x: pd.Series({
        'latitude': round(np.average(x['latitude'], weights=x['max_count_list']),2),
        'longitude': round(np.average(x['longitude'], weights=x['max_count_list']),2),
        'max_count_list': x['max_count_list'].sum()
    })).reset_index()

    return map_df, animal_colors, central_points

# Plots the map using pydeck. Works by creating layers and assembling them into a "Deck"
# Functionality allows for animals to be selected with the checkbox. Applies the filter to the map_df 
def plot_graph(selected_animals, map_df, central_points, show_clusters=False):

    # Filter map_df based on the selected animals
    filtered_df = map_df[map_df['animal_list'].isin(selected_animals)]
    filtered_central_points = central_points[central_points['animal_list'].isin(selected_animals)]

    # Load upper and lower boundaries of the park from GeoJSON files
    with open("../data/GeoJson/export_upper.geojson") as f:
        upper_boundary_geojson = json.load(f)

    with open("../data/GeoJson/export_lower.geojson") as f:
        lower_boundary_geojson = json.load(f)

    # Create a text layer
    text_layer1 = pdk.Layer(
        "TextLayer",
        data=[{"position": [-7.29, 5.65], "text": "You are here"}],
        get_size=10,
        get_color=[255, 0, 0, 255],
        get_position="position",
        get_text="text",
    )

    # Create a text layer
    text_layer2 = pdk.Layer(
        "TextLayer",
        data=[{"position": [-7.283, 5.62], "text": "X"}],
        get_size=12,
        get_color=[255, 0, 0, 255],
        get_position="position",
        get_text="text",
    )

    # Define a layer to display the animal locations on the map
    animal_layer = pdk.Layer(
        'ScatterplotLayer',
        data=filtered_df,
        get_position='[longitude, latitude]',
        get_fill_color='animal_colors_list',
        get_radius='max_count_list * 12',
        pickable=True,
        opacity=0.8
    )

    # Define a layer to display the animal locations on the map as a heatmap
    heatmap_layer = pdk.Layer(
        'HeatmapLayer',
        data=filtered_central_points,
        get_position='[longitude, latitude]',
        opacity=0.8,
        color_range=[[178, 255, 255]],
        threshold=0.01,
    )

    animal_text_layer = pdk.Layer(
        "TextLayer",
        data=filtered_central_points,
        get_position='[longitude, latitude]',
        get_text='animal_list',
        get_size=12,
        get_color=[0, 0, 0],
        get_angle=0,
        get_text_anchor='"middle"',
        get_alignment_baseline='"center"',
    )

    # Define a layer to display the upper boundary of the park
    upper_boundary_layer = pdk.Layer(
        'GeoJsonLayer',
        data=upper_boundary_geojson,
        stroked=True,
        filled=False,
        line_width_min_pixels=2,
        get_line_color=[0, 0, 0, 255]
    )

    # Define a layer to display the lower boundary of the park
    lower_boundary_layer = pdk.Layer(
        'GeoJsonLayer',
        data=lower_boundary_geojson,
        stroked=True,
        filled=False,
        line_width_min_pixels=2,
        get_line_color=[0, 0, 0, 255]
    )

    # Define the view state
    view_state = pdk.ViewState(
        latitude=5.63,
        longitude=-7.15,
        zoom=8.4,
        pitch=0
    )

    # Render the deck.gl map
    layers = [upper_boundary_layer, lower_boundary_layer, text_layer2, text_layer1]
    
    if show_clusters:
        if not filtered_central_points.empty:
            layers.append(heatmap_layer)
            layers.append(animal_text_layer)
    else:
        if not filtered_df.empty:
            layers.append(animal_layer)

    r = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/satellite-streets-v11",
        tooltip={"text": "{animal_list}\nCount: {max_count_list}\nLat: {latitude}\nLong: {longitude}"}
    )

    return r

# Creates bar plot with checkboxed animals
def animal_counts_plotted(selected_animals, map_df, bar_width=0.8, figsize=(5,5)):
    dict2 = {}
    # Filter map_df based on the selected animals
    filtered_df_2 = map_df[map_df['animal_list'].isin(selected_animals)]

     # Define colors
    background_color = 'black'
    element_color = 'lightgrey'

    for animal in selected_animals:
        dict2[animal] = filtered_df_2.query("animal_list == @animal")["max_count_list"].sum()
    
    # Create the matplotlib figure
    fig, ax = plt.subplots(figsize=figsize)

    # Set the background to be transparent
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    # Set the background color of the figure and axes
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)

    ax.bar(range(len(dict2)), 
        list(dict2.values()), 
        width=bar_width, 
        color=element_color, 
        tick_label=selected_animals
        )
    ax.set_title(
        label='Animal sightings',
        fontdict={
            'fontsize': 20,
            'color': element_color,
            'verticalalignment': 'baseline',
            'horizontalalignment': 'center'
        }
    )
    ax.set_xticks(range(len(dict2)))
    #ax.set_ylabel('Counts', color=element_color, size=20)
    ax.set_xticklabels(list(dict2.keys()), rotation=90, color=element_color, fontsize=18)
    ax.tick_params(axis='x', colors=element_color, labelsize=18)
    ax.tick_params(axis='y', colors=element_color, labelsize=18)
    # Set the spines (borders) of the plot to green
    for spine in ax.spines.values():
        spine.set_edgecolor(element_color)

    # Adjust the color of the tick labels and other elements
    ax.yaxis.label.set_color(element_color)
    ax.xaxis.label.set_color(element_color)
    ax.title.set_color(element_color)

    # Ensure grid lines are not visible (optional)
    ax.grid(False)

    # Return the figure
    return fig

    
