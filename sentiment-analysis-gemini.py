import pandas as pd
import google.generativeai as genai
import os
from tqdm import tqdm  # For progress bar
from ratelimit import limits, sleep_and_retry
from backoff import on_exception, expo
import time
import json

# Configure Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Define rate limits
CALLS_PER_MINUTE = 15
SECONDS_PER_CALL = 60.0 / CALLS_PER_MINUTE

@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE, period=60)
@on_exception(expo, Exception, max_tries=3)
def analyze_sentiment(text):
    """
    Analyze sentiment of a given text using Gemini AI.
    Returns a dictionary with sentiment and confidence.
    """
    try:
        prompt = f"""
        Analyze the sentiment of this comment, considering these contexts:
        - In Chinese internet culture, "666" means "awesome" or "skilled" (very positive)
        - Heart emojis (❤️) and similar symbols are positive
        - Religious blessings like "God bless" are positive expressions of goodwill
        - The 🥹 emoji (face holding back tears) usually indicates emotional warmth or touched feelings
        - References to family members in blessings make the sentiment more positive
        - The ✝️ cross symbol in context of blessings reinforces positive sentiment
        
        Classify the sentiment as POSITIVE, NEGATIVE, or NEUTRAL.
        Also provide a confidence score between 0 and 1.
        Return only a JSON-like string in this format: {{"sentiment": "POSITIVE", "confidence": 0.95}}

        Comment: {text}
        """

        response = model.generate_content(prompt)
        try:
            result = json.loads(response.text.strip())
            return result
        except json.JSONDecodeError:
            return {"sentiment": "NEUTRAL", "confidence": 0.5}
    except Exception as e:
        print(f"Error analyzing comment: {e}")
        time.sleep(SECONDS_PER_CALL)
        raise


def main():
    # Read the CSV file
    df = pd.read_csv('20241113_192753_comments.csv')

    # Initialize lists to store results
    sentiments = []
    confidences = []

    # Process each comment with a progress bar
    for comment in tqdm(df['text'], desc="Analyzing comments"):
        result = analyze_sentiment(comment)
        sentiments.append(result['sentiment'])
        confidences.append(result['confidence'])

    # Add results to dataframe
    df['sentiment'] = sentiments
    df['confidence'] = confidences

    # Save results
    df.to_csv('comments_with_sentiment.csv', index=False)

    # Print summary
    sentiment_counts = df['sentiment'].value_counts()
    print("\nSentiment Analysis Summary:")
    print(sentiment_counts)

    avg_confidence = df['confidence'].mean()
    print(f"\nAverage confidence: {avg_confidence:.2f}")


if __name__ == "__main__":
    main()
