import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import plotly.express as px

# Set the title of the dashboard
st.set_page_config(page_title='Amazon Prime Dashboard', layout='wide')
st.markdown("""
    <style>
    body {
        background-color: #f0f2f6;
    }
    .css-1d391kg {
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)
st.title('📊 Amazon Prime Dashboard')

# Load the dataset
df = pd.read_csv("amazon_prime.csv")

# Sidebar filters
st.sidebar.header("🔧 Filters")
selected_type = st.sidebar.multiselect("Select Content Type", df['type'].unique(), default=df['type'].unique())
selected_genre = st.sidebar.multiselect("Select Genre", df['listed_in'].str.split(', ').explode().unique())
selected_rating = st.sidebar.multiselect("Select Rating", df['rating'].dropna().unique())
selected_year_range = st.sidebar.slider("Select Release Year Range", int(df['release_year'].min()), int(df['release_year'].max()), (2000, 2020))

# Reset button
def reset_filters():
    st.session_state["selected_type"] = df['type'].unique()
    st.session_state["selected_genre"] = []
    st.session_state["selected_rating"] = []
    st.session_state["selected_year_range"] = (2000, 2020)

if st.sidebar.button("🔄 Reset Filters"):
    reset_filters()

# Apply filters
filtered_df = df[df['type'].isin(selected_type)]
filtered_df = filtered_df[filtered_df['release_year'].between(*selected_year_range)]
if selected_genre:
    filtered_df = filtered_df[filtered_df['listed_in'].str.contains('|'.join(selected_genre), na=False)]
if selected_rating:
    filtered_df = filtered_df[filtered_df['rating'].isin(selected_rating)]

# Display a preview of the dataset
st.subheader("🔍 Dataset Preview")
st.dataframe(filtered_df.head())

# Run EDA
st.subheader("📈 Dataset Information")
st.write("**🔹 Shape of the dataset:**", filtered_df.shape)
st.write("**🔹 Descriptive Statistics:**")
st.write(filtered_df.describe(include='all'))

# Display the missing values
st.write("**🔹 Missing Values:**")
missing_values = filtered_df.isnull().sum()
st.write(missing_values[missing_values > 0])

# Movie vs TV Show counts
st.subheader("📊 Distribution of Content Type")
fig = px.bar(filtered_df['type'].value_counts(), x=filtered_df['type'].value_counts().index, y=filtered_df['type'].value_counts().values, labels={'x': 'Content Type', 'y': 'Count'}, title="Movie vs TV Show Count")
st.plotly_chart(fig)

# Release Year Distribution
st.subheader("📆 Release Year Distribution")
fig = px.histogram(filtered_df, x='release_year', nbins=20, title="Release Year Distribution", labels={'release_year': 'Year'})
st.plotly_chart(fig)

# Popular Genres
st.subheader("🎭 Top Genres")
genre_counts = filtered_df['listed_in'].str.split(', ').explode().value_counts().head(10)
fig = px.bar(x=genre_counts.index, y=genre_counts.values, labels={'x': 'Genre', 'y': 'Count'}, title="Top Genres", color=genre_counts.values, color_continuous_scale='Viridis')
st.plotly_chart(fig)

# Word Cloud for Descriptions
st.subheader("🌟 Most Common Words in Descriptions")
text = ' '.join(filtered_df['description'].dropna())
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
fig, ax = plt.subplots()
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis('off')
st.pyplot(fig)

# Directors with the most titles (Updated Chart)
st.subheader("🎬 Top Directors with Most Titles")
director_counts = filtered_df['director'].dropna().value_counts().head(10).reset_index()
director_counts.columns = ['Director', 'Count']
fig = px.bar(director_counts, x='Director', y='Count', title="Top Directors by Number of Titles", color='Count', color_continuous_scale='Inferno')
st.plotly_chart(fig)

# Viewer Rating Distribution
st.subheader("⭐ Viewer Rating Distribution")
fig = px.pie(filtered_df, names='rating', title="Distribution of Content Ratings")
st.plotly_chart(fig)

# Box Plot for Duration vs Genre (Top 25-40 genres only)
st.subheader("🎬 Duration vs Genre")
filtered_df['duration_numeric'] = filtered_df['duration'].str.extract('(\d+)').astype(float)
top_genres = filtered_df['listed_in'].str.split(', ').explode().value_counts().head(40).index
filtered_df = filtered_df[filtered_df['listed_in'].isin(top_genres)]
fig = px.box(filtered_df, x='listed_in', y='duration_numeric', labels={'listed_in': 'Genre', 'duration_numeric': 'Duration (minutes)'}, title="Box Plot of Duration vs Genre (Top Genres)")
st.plotly_chart(fig)

# Treemap Visualization for Genres
st.subheader("📌 Genre Distribution Treemap")
genre_treemap = filtered_df['listed_in'].str.split(', ').explode().value_counts().reset_index()
genre_treemap.columns = ['Genre', 'Count']
fig = px.treemap(genre_treemap, path=['Genre'], values='Count', title="Treemap of Genres")
st.plotly_chart(fig)

# Show raw data
st.subheader("📜 Raw Data")
st.dataframe(filtered_df)