import pandas as pd
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import re

# Read the CSV file
df = pd.read_csv('20241113_192753_comments.csv')

# Combine all comments into one text
text = ' '.join(df['text'].astype(str))

# Basic cleaning
# Remove URLs
text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
# Remove special characters but keep letters from all languages and emojis
text = re.sub(
    r'[^\w\s\u4e00-\u9fff\u0400-\u04FF\u0E00-\u0E7F\U0001F300-\U0001F9FF]', ' ', text)
# Remove extra whitespace
text = re.sub(r'\s+', ' ', text).strip()

# Define a color palette inspired by traditional Chinese aesthetics
color_func = lambda *args, **kwargs: np.random.choice([
    "#8C4356",  # Chinese rouge red
    "#A88462",  # Ancient pottery brown
    "#4A4E4D",  # Ink black
    "#839B97",  # Celadon green
    "#977C00",  # Ancient gold
    "#794C74",  # Purple lotus
    "#5B7F98",  # Porcelain blue
])

# Create and generate a word cloud image
wordcloud = WordCloud(
    width=3200,
    height=1600,
    background_color='#F7F3E8',  # Warm rice paper color
    font_path='/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
    max_words=500,
    min_font_size=8,
    max_font_size=200,
    random_state=42,
    color_func=color_func,
    prefer_horizontal=0.7,  # Allow more vertical words
    margin=20,  # Add some margin
).generate(text)

# Match background color
plt.figure(figsize=(32, 16), dpi=300, facecolor='#F7F3E8')
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')

# Save with matching background
plt.savefig('word-cloud.png',
            dpi=300,
            bbox_inches='tight',
            facecolor='#F7F3E8')
