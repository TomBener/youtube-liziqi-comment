# Li Ziqi YouTube Video Comments Analysis

A data analysis project that scrapes and analyzes comments from Li Ziqi's comeback YouTube video [My grandma’s wardrobe was broken, so I gave it a makeover](https://www.youtube.com/watch?v=IrXjnw8BpM0) released on November 12, 2024.

## Word Cloud

![Word Cloud](word-cloud.png)

## Sentiment Analysis

The sentiment analysis is conducted using Google Gemini, and the result is overwhelmingly positive.

## Prerequisites

To collect video data, you’ll need a YouTube Data API key:

1. Visit the [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3
4. Create credentials (API key)
5. Rename `.env.example` to `.env`
6. Add your API key to the `.env` file

To conduct the sentiment analysis, you’ll need a Gemini API key:

1. Visit the [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a Gemini API key
3. Add your Gemini API key to the `.env` file
