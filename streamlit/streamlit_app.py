import streamlit as st
#import sys
import time
import pandas as pd
# import numpy as np
# from PIL import Image
#from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions

# Import functions with relative path
#sys.path.append("../functions")
from st_app_functions import get_started, user_name, create_map_df, plot_graph, animal_counts_plotted, get_base64_image

# Define a random seed
random_seed = 42

# Store the initial value of widgets in session state
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False

# Logo in page URL
st.set_page_config(
    page_title="TNP WildVision",
    page_icon="image_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
    )

# Sidebar Navigation/Tabs
st.sidebar.markdown("## Navigation")
tabs = st.sidebar.radio("", ["Get Started", "Trip Planner", "My Sightings", "Info"])
st.sidebar.markdown("---")

if tabs == "Get Started":
    # Create three equally sized columns to get logo in the center. col1/2 are just placeholder
    col1, col2, col3 = st.columns([1, 1., 1])

    with col1:
        st.write("")  # Empty column for spacing
    with col2:
        st.image("image_logo.png", use_column_width=True)
    with col3:
        st.write("")  # Empty column for spacing
    
    if 'button_clicked' not in st.session_state:
        st.session_state.button_clicked = False
    if st.button("Get Started"):
        st.session_state.button_clicked = True

    # Text input widget function is called
    if st.session_state.button_clicked:
        text_input = user_name()

        if text_input:
            text_to_write = f"Hello {text_input}! If you want a little assistance with planning your trip today, please click the 'Trip Planner' icon.\n If you want to get animals on your pictures identified please go to 'My Sightings'."
            st.write_stream(get_started(text_to_write))
            st.session_state.disabled = True

# Tab about the map
elif tabs == "Trip Planner":
    st.header("Interactive TNP Map")

    # Create the necessary data structures for the default map, the colors and the cluster centers
    map_df, animal_colors, central_points = create_map_df(seed=random_seed)

    # Custom labels just for display
    button_options = {
        "Antelope/duiker": "Duiker Devotee",
        "Bird": "Bird Buff",
        "Civet/genet": "Civet Connoisseur",
        "Hog": "Hog Handler",
        "Leopard": "Leopard Lover",
        "Monkey/prosimian": "Monkey Maniac",
        "Rodent": "Rodent Ruler"
    }

    # Split page in 2 columns. Col2 double the size.
    col1, col2 = st.columns([1, 2])

    # All about the checkbox widget with the custom created labels, to serve as legend for map
    # Original checkbox looks way different
    with col1:
        st.write("Choose your favorite animals")
        with st.container():
            st.write('I am a:')
            selected_animals = []
            for animal, label in button_options.items():

                # Only use the RGB part of RBGA encoded color dictionary
                color = animal_colors[animal][:3]
                color_str = f"rgb({color[0]}, {color[1]}, {color[2]})"
                
                # Split into three columns for checkbox and and custom label alignment
                # Otherwise the custom labels are sorted below the checkboxes
                check_col, label_col, _ = st.columns([0.1, 0.9, 0.1])
                with check_col:

                    # If not empty input the letters will be spelled one-by-one below each other
                    if st.checkbox("", key=animal):

                        # Creates the selected animals list, which can later serve as a filter
                        # For the map_df to only query the selected animals
                        selected_animals.append(animal)
                
                # CSS/HTML custom label
                with label_col:
                    html_label = f'''
                    <label class="custom-checkbox-label" style="color: {color_str};">
                        {label}
                    </label>
                    '''
                    st.markdown(html_label, unsafe_allow_html=True)

            # Placeholder for bar plot on animal counts
            graph_container = st.empty()

    # Create placeholders for the "Show animal sightings of 2023" button, the map, and the loading bar
    plot_button_placeholder = col2.empty()
    loading_bar_placeholder = col2.empty()
    map_placeholder = col2.empty()

    with col2:
        # Ensures that map is only updated if both conditions are met
        if selected_animals and plot_button_placeholder.button("Show animal sightings of 2023"):
            # Loading bar for fake computation time
            loading_text = loading_bar_placeholder.text("Loading... 0%")
            for percent_complete in range(100):
                loading_text.text(f"Loading... {percent_complete + 1}%")
                time.sleep(0.02)
            # Call function that creates the entire map with animal locations at map placeholder
            pydeck_map = plot_graph(selected_animals, map_df, central_points)
            map_placeholder.pydeck_chart(pydeck_map)
            # Bar plot generated at placeholder space
            fig = animal_counts_plotted(selected_animals, map_df)
            graph_container.pyplot(fig)
        else:
            # Create the default map only if the "Plot" button is not clicked
            pydeck_map = plot_graph([], map_df, central_points)
            map_placeholder.pydeck_chart(pydeck_map)

        # Plot Clusters button below the map the generation follows same logic as above
        if st.button("Where should I go?"):
            # Loading bar
            progress_bar = loading_bar_placeholder.progress(0)
            loading_text = loading_bar_placeholder.text("Loading... 0%")
            for percent_complete in range(100):
                loading_text.text(f"Loading... {percent_complete + 1}%")
                time.sleep(0.02)
            pydeck_map = plot_graph(selected_animals, map_df, central_points, show_clusters=True)
            map_placeholder.pydeck_chart(pydeck_map)
            
            graph_container.empty()
            animal_coordinates = []
            # To create table at position where the bar plot was
            for _, row in central_points.iterrows():
                if row['animal_list'] in selected_animals:
                    animal_coordinates.append([row['animal_list'], row['latitude'], row['longitude']])
            if animal_coordinates:
                animal_df = pd.DataFrame(animal_coordinates, columns=['Animal', 'Lat', 'Long'])
                graph_container.write(animal_df)
            else:
                graph_container.write("No animals selected.")

# Tab where user can upload image and gets the animal identified
elif tabs == "My Sightings":
    st.header("Let your animal be identified and score points")
    col3, col4= st.columns([1, 2])

    # # Load the MobileNetV2 model
    # model = MobileNetV2(weights='imagenet')

    # def preprocess_image(image):
    #     img = Image.open(image).convert('RGB')
    #     img = img.resize((224, 224))
    #     img_array = np.array(img)
    #     img_array = np.expand_dims(img_array, axis=0)
    #     img_array = preprocess_input(img_array)
    #     return img_array

    with col3:
        st.write("Leaderboard")

        # List of names and corresponding image paths. Placeholder images
        leaderboard_data = [
            ("TNP.jpeg", "J. Goodall"),
            ("TNP.jpeg", "T. Stark"),
            ("TNP.jpeg", "Cpt. J. Sparrow"),
            ("TNP.jpeg", "Hulk"),
            ("TNP.jpeg", "R2D2"),
        ]

        # Custom CSS to align images and text
        st.markdown("""
            <style>
                .leaderboard-item {
                    display: flex;
                    align-items: center;
                    margin-bottom: 10px;
                }
                .leaderboard-item img {
                    margin-right: 20px;
                    margin-left: 20px;
                }
                .leaderboard-item span {
                    font-size: 16px;
                }
                .leaderboard-rank {
                font-weight: bold;
                margin-right: 10px;
                }
            </style>
        """, unsafe_allow_html=True)

        # Display leaderboard with a rank, the image in html compliant format and name of user
        for rank, (img_path, name) in enumerate(leaderboard_data, start=1):

            img_base64 = get_base64_image(img_path)
            img_html = f'<img src="data:image/jpeg;base64,{img_base64}" width="100">'
            st.markdown(f"<div class='leaderboard-item'><span class='leaderboard-rank'>{rank}.</span>{img_html}<span>{name}</span></div>", unsafe_allow_html=True)

    # Apply image classification model if image is uploaded and button clicked
    with col4:
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded Image", width=400)
            identify_button_clicked = st.button("Identify Animal")
            if identify_button_clicked:
                progress_bar = st.progress(0)
                loading_text = st.text("Loading... 0%")
                for percent_complete in range(100):
                    time.sleep(0.02)
                    loading_text.text(f"Loading... {percent_complete + 1}%")
                    progress_bar.progress(percent_complete + 1)
                # Where classification takes place
                # try:
                #     img_array = preprocess_image(uploaded_file)
                #     predictions = model.predict(img_array)
                #     label = decode_predictions(predictions)[0][0]
                #     text_to_write = f"Congrats! We are {label[2]*100:.2f}% confident that you photographed a {label[1]}."
                #     st.write(get_started(text_to_write))
                # except Exception as e:
                #     st.error(f"An error occurred: {e}")
                    
elif tabs == "Info":
    st.header("Info")