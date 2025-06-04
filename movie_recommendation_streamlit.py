import streamlit as st
import pandas as pd
import pickle

# Load the model
with open('model4.pkl', 'rb') as file:
    model = pickle.load(file)

# Load the dataset for reference (optional, based on requirements)
@st.cache_data
def load_data():
    data = pd.read_csv('netflix_titles.csv')
    return data

data = load_data()

# Streamlit App Design
st.markdown(
    """
    <style>
        .center-title {
            text-align: center;
            padding: 20px;
            font-size: 40px;
            font-weight: bold;
            color: #333333;
        }
        .wide-image {
            width: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and Image
st.markdown('<div class="center-title">Netflix Recommendation System</div>', unsafe_allow_html=True)
st.image("https://i.pinimg.com/736x/0a/a3/3c/0aa33c4c483f63a5a1ec383457aa0f98.jpg", use_column_width=True)

st.write("Provide your preferences to get personalized recommendations!")

# Input Fields for User Preferences
genre = st.selectbox(
    "Choose a Genre:",
    options=list(set(data['listed_in'].dropna().str.split(', ').sum()))
)

# Slider for number of recommendations
num_recommendations = st.slider(
    "How many recommendations do you want?",
    min_value=1,
    max_value=20,
    value=5,  # Default value
)

# Optional Title Search (Optional)
title_search = st.text_input("Search for a Title (Optional): Leave blank to skip.")

# Button to Trigger Recommendation
if st.button("Recommend"):
    # Filter dataset based on inputs
    filtered_data = data[data['listed_in'].str.contains(genre, na=False)]
    
    if title_search:
        filtered_data = filtered_data[filtered_data['title'].str.contains(title_search, case=False, na=False)]

    # Limit the number of recommendations
    filtered_data = filtered_data.head(num_recommendations)

    # Check if filtered data exists
    if not filtered_data.empty:
        st.subheader("Recommended Titles:")
        for _, row in filtered_data.iterrows():
            st.write(f"**{row['title']}**")
            st.write(f"Director: {row['director'] if pd.notna(row['director']) else 'N/A'}")
            st.write(f"Cast: {row['cast'] if pd.notna(row['cast']) else 'N/A'}")
            st.write(f"Genre: {row['listed_in']}")
            st.write(f"Rating: {row['rating']}")
            st.write(f"Year Released: {row['release_year']}")
            st.write(f"Duration: {row['duration'] if pd.notna(row['duration']) else 'N/A'}")
            st.write(f"Description: {row['description']}")
            st.write("---")
    else:
        st.write("No recommendations found for the given criteria.")

st.write("---")
st.write("Built with ❤️")
