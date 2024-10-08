import streamlit as st
import pickle
import pandas as pd
from PIL import Image
import os

def recommend(drama_list, drama_images_df, drama, image_path='images'):
    try:
        drama_index = drama_list[drama_list['title'] == drama].index[0]
        distances = similarity[drama_index]
        sorted_distances = sorted(enumerate(distances), reverse=True, key=lambda x: x[1])[1:7]  # Change from [1:6] to [1:7]
        
        recommended_dramas = []
        recommended_images = []
        for i in sorted_distances:
            recommended_dramas.append(drama_list.iloc[i[0]]['title'])
            drama_id = drama_list.iloc[i[0]]['drama_id']
            local_image_path = os.path.join(image_path, f"{drama_id}.jpg")
            if os.path.exists(local_image_path):
                recommended_images.append(local_image_path)
            else:
                st.error(f"Image for drama ID {drama_id} not found locally.")
        return recommended_dramas, recommended_images
    except (IndexError, KeyError) as e:
        st.error(f"Error occurred: {e}")
        return ["Drama not found or error occurred."], []

# Load data
try:
    drama_list = pickle.load(open('asian_dramas.pkl','rb'))
    similarity = pickle.load(open('similarity.pkl','rb'))
    with open('images_data.pkl', 'rb') as f:
        drama_images_df = pickle.load(f)
        if not isinstance(drama_images_df, pd.DataFrame):
            raise ValueError("drama_images_df is not a DataFrame.")
except FileNotFoundError as e:
    st.error(f"Error: Data files not found. {e}")
except Exception as e:
    st.error(f"Error loading data: {e}")

# Prepare Streamlit app
st.title('Asian Drama Recommendation System')

selected_drama_name = st.selectbox(
    'Type in the drama title',
    drama_list['title'].values)

if st.button('Recommend'):
    recommendations, images = recommend(drama_list, drama_images_df, selected_drama_name)
    num_recommendations = len(recommendations)
    num_columns = 3  # Number of columns for recommendations

    # Calculate number of rows required
    num_rows = (num_recommendations + num_columns - 1) // num_columns

    for row in range(num_rows):
        cols = st.columns(num_columns)
        for col in range(num_columns):
            index = row * num_columns + col
            if index < num_recommendations:
                with cols[col]:
                    st.write(recommendations[index])
                    img = Image.open(images[index])
                    st.image(img)
