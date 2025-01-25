# News Extraction Web App

This is a web-based application that allows users to extract and analyze content from news articles by providing a URL. The app scrapes the article, processes the text for sentiment analysis, tokenization, part-of-speech tagging, and stores the extracted data in a PostgreSQL database.

## Features

- **Extract News Content**: Input a news article URL to extract its headline, synopsis, and full content.
- **Sentiment Analysis**: The app performs sentiment analysis on the article's content and categorizes it as Positive, Negative, or Neutral.
- **Text Tokenization**: The text is tokenized into words and sentences for further processing.
- **POS Tagging**: The app performs Part-of-Speech (POS) tagging on the text and counts the occurrences of each tag.
- **Data Storage**: Extracted data is stored in a PostgreSQL database for easy retrieval and management.

## Technologies Used

- **Backend**: Flask (Python Web Framework)
- **Database**: PostgreSQL
- **Web Scraping**: BeautifulSoup, Requests
- **Text Analysis**: NLTK, TextBlob
- **OAuth Authentication**: Authlib (GitHub Login)
- **Natural Language Processing**: Tokenization, Sentiment Analysis, POS Tagging

## How it Works

1. **User submits a URL**: The user inputs a news article URL.
2. **Scrape Content**: The app fetches the page content and extracts the headline, synopsis, and body text.
3. **Text Processing**: Sentiment analysis, tokenization, and POS tagging are performed on the extracted content.
4. **Store in Database**: All the extracted data is stored in a PostgreSQL database for analysis.
5. **Admin Dashboard**: The admin can view all stored articles through a secure login.

## Setup & Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Sahilkumar1272/NewsExtractor.git

2.Install dependencies:
```bash
pip install -r requirements.txt

