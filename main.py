from flask import Flask, request, render_template, redirect, url_for, session
import pandas as pd
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session to work

# Load the dataset
data = pd.read_csv('netflix_titles.csv')

OMDB_API_KEY = '3846e50e'
YOUTUBE_API_KEY = 'AIzaSyDiAWn_hopmBxY6eGz2R4VR3wc2klh2JIY'

# Get YouTube trailer
def get_youtube_embed_link(title):
    query = f"{title} official trailer"
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "key": YOUTUBE_API_KEY,
        "type": "video",
        "maxResults": 1
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        if items:
            video_id = items[0]["id"]["videoId"]
            return f"https://www.youtube.com/embed/{video_id}"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching trailer: {e}")
    return ""

# Get poster
def get_movie_poster(title):
    try:
        url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return data.get("Poster", "https://via.placeholder.com/150x220?text=No+Poster")
    except Exception as e:
        print(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/150x220?text=No+Poster"

@app.route('/')
def home():
    return render_template("index.html", recommendations=[], wishlist=session.get('wishlist', []))

@app.route('/recommend', methods=['POST'])
def recommend():
    genre = request.form.get('genre')
    num_recommendations = int(request.form.get('num_recommendations'))

    filtered_data = data[data['listed_in'].str.contains(genre, na=False, case=False)]

    if filtered_data.empty:
        filtered_data = data.sample(num_recommendations)
    else:
        filtered_data = filtered_data.head(num_recommendations)

    recommendations = []
    for _, row in filtered_data.iterrows():
        title = row.get('title', 'Unknown Title')
        poster = get_movie_poster(title)
        description = row.get('description', 'No description available.')
        recommendations.append({
            'title': title,
            'description': description,
            'type': row.get('type', 'N/A'),
            'cast': row.get('cast', 'N/A'),
            'director': row.get('director', 'N/A'),
            'release_year': row.get('release_year', 'N/A'),
            'rating': row.get('rating', 'N/A'),
            'duration': row.get('duration', 'N/A'),
            'poster': poster,
            'trailer': get_youtube_embed_link(title)
        })

    return render_template("index.html", recommendations=recommendations, genre=genre, wishlist=session.get('wishlist', []))

@app.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist():
    title = request.form.get('title')
    poster = request.form.get('poster')
    description = request.form.get('description')

    if 'wishlist' not in session:
        session['wishlist'] = []

    if not any(item['title'] == title for item in session['wishlist']):
        session['wishlist'].append({
            'title': title,
            'poster': poster,
            'description': description
        })
        session.modified = True

    return redirect(url_for('home'))

@app.route('/wishlist')
def wishlist_page():
    wishlist_titles = session.get('wishlist', [])
    wishlist_movies = []
    for title in wishlist_titles:
        row = data[data['title'] == title].head(1)
        if not row.empty:
            row = row.iloc[0]
            wishlist_movies.append({
                'title': row.get('title', 'Unknown Title'),
                'description': row.get('description', 'No description available.'),
                'poster': get_movie_poster(title),
            })
    return render_template("wishlist.html", wishlist=wishlist_movies)

if __name__ == '__main__':
    app.run(debug=True)
