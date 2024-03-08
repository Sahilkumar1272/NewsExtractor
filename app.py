from flask import Flask, render_template, request, redirect, url_for, session, flash # Import necessary Flask modules
import psycopg2  # Import PostgreSQL adapter
from bs4 import BeautifulSoup  # Import BeautifulSoup for web scraping
import requests  # Import requests library for HTTP requests
import re  # Import re for regular expressions
import nltk  # Import nltk for natural language processing
from nltk.tokenize import word_tokenize, sent_tokenize  # Import tokenizers from NLTK
from nltk import pos_tag  # Import part-of-speech tagger from NLTK
import json  # Import json module for handling JSON data
from textblob import TextBlob
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)  # Create a Flask app instance
app.secret_key = 'sahil1272'

# to github
oauth = OAuth(app)

app.config['SECRET_KEY'] = "THIS SHOULD BE SECRET"
app.config['GITHUB_CLIENT_ID'] = "ab73f89ee9ac7d457cfe"
app.config['GITHUB_CLIENT_SECRET'] = "1ee6a2f4db68c0de5d1d7d1e6969f83f8d87eb4d"

github = oauth.register(
    name='github',
    client_id=app.config["GITHUB_CLIENT_ID"],
    client_secret=app.config["GITHUB_CLIENT_SECRET"],
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# Connect to the PostgreSQL database
def connect_db():
    conn = psycopg2.connect(
        dbname="dhp2024",
        user="postgres",
        password="Sahil9211@#",
        host="localhost"
    )
    return conn

def get_sentiment(text):
    analysis = TextBlob(text)
    sentiment_score = analysis.sentiment.polarity
    # Check if sentiment polarity is positive, negative, or neutral
    if sentiment_score > 0:
        sentiment_label = 'Positive'
    elif sentiment_score < 0:
        sentiment_label = 'Negative'
    else:
        sentiment_label = 'Neutral'
    return sentiment_label, sentiment_score
    

# Function to clean text from a given URL
def cleaned_text_from_url(url):
    response = requests.get(url)  # Send HTTP GET request to the provided URL
    if response.status_code == 200:  # If the request is successful
        soup = BeautifulSoup(response.content, 'html.parser')  # Parse the HTML content using BeautifulSoup

        # Extracting headlines and synopsis from the HTML content
        headline = soup.find('h1').text
        synopsis = soup.find('h2', class_="synopsis").text

        # Extracting main content
        main_content = soup.find('div', id='pcl-full-content')
        unwanted=main_content.find_all('blockquote')
        for unw in unwanted:
            unw.decompose()
        p_tags = main_content.find_all('p')

        # Extracting text content from <p> tags and concatenating into a single string
        content_string = ''
        for p_tag in p_tags:
            content_string += p_tag.get_text().strip()

        # Clean the main content: remove extra newlines and whitespace
        main_content = re.sub(r'\n+', '\n', content_string)
        main_content = re.sub(r'\s+', ' ', content_string)
        
        return headline,  synopsis,  content_string  # Return the cleaned headline, synopsis, and main content

    else:  # If the request fails
        print("Failed to retrieve the webpage. Status code:", response.status_code)


@app.route('/')  # Route for the homepage
def index():
    return render_template('index.html')  # Render the index.html template


@app.route('/submit', methods=['POST', 'GET'])  # Route for form submission
def submit():
    url = request.form['name']  # Get the URL from the submitted form
    heading, sub_heading, text = cleaned_text_from_url(url)  # Call the function to get cleaned text from the URL

    sentiment_label, sentiment_score=get_sentiment(text)

    # Further processing of the text
    words_list = word_tokenize(text)
    sent_list = sent_tokenize(text)

    count_stop_words = 0
    for i in words_list:
        if i.lower() in nltk.corpus.stopwords.words('english'):
            count_stop_words += 1

    def words(string):
        punc_list = ['.', ',', '!', '?']
        word_lst = word_tokenize(text)
        for i in word_lst:
            if i in punc_list:
                word_lst.remove(i)
        return len(word_lst)

    dict_upos = {}
    list_new = [x for x in nltk.pos_tag(words_list, tagset='universal')]
    for i in list_new:
        if i[1] not in dict_upos.keys():
            dict_upos[i[1]] = 1
        else:
            dict_upos[i[1]] += 1
    dict_upos = dict_upos
    sent_count = len(sent_list)
    words_count = words(text)
    pos_tag_count = sum(dict_upos.values())

    # Store summary data in a dictionary
    summary = {'words_count': words_count, 'sentences_count': sent_count, 'UPOS_tag_count': sum(dict_upos.values())}

    # Connect to the database
    conn = connect_db()
    cur = conn.cursor()

    # Create a table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS news_articles (
            id SERIAL PRIMARY KEY,
            url VARCHAR(1000),
            text TEXT,
            word_count INTEGER,
            sentence_count INTEGER,
            pos_tag_count INTEGER
        )
    """)

    # Insert data into the database
    cur.execute("""
        INSERT INTO news_articles (url, text, word_count, sentence_count, pos_tag_count)
        VALUES (%s, %s, %s, %s, %s)
    """, (url, text, words_count, sent_count, pos_tag_count))

    conn.commit()  # Commit changes
    conn.close()  # Close database connection

    # Render the content.html template with the extracted data
    return render_template('content.html', heading=heading, sub_heading=sub_heading, text=text,
                           words_count=words_count, sent_count=sent_count, dict_upos=dict_upos,
                           pos_tag_count=pos_tag_count,sentiment_label=sentiment_label, sentiment_score=sentiment_score)


@app.route('/admin')  # Route for admin login
def admin():
    return render_template('admin.html')  # Render the admin.html template


@app.route('/login', methods=['POST'])  # Route for handling login form submission
def login():
    email = request.form.get('email')  # Get email from the submitted form
    password = request.form.get('password')  # Get password from the submitted form
    conn = connect_db()
    cur = conn.cursor()

    # Execute SQL query to check credentials
    cur.execute("SELECT * FROM admin WHERE email=%s AND password=%s", (email.lower(), password))
    user = cur.fetchone()  # Fetch the result

    if user:  # If user exists (credentials are correct)
        return redirect('/admin/welcome')  # Redirect to the admin welcome page
    else:  # If user doesn't exist (credentials are incorrect)
        return "Invalid email or password"  # Return an error message
    
@app.route('/admin/logout')  # Route for admin logout
def admin_logout():
    session.clear()  # Clear the session
    flash('You have been logged out successfully!', 'success')  # Flash message for logout
    return redirect(url_for('admin'))  # Redirect to the admin login page



@app.route('/admin/welcome')
def admin_welcome():
    conn = connect_db() 
    cur = conn.cursor()
    cur.execute("SELECT * FROM news_articles")
    articles = cur.fetchall()
    conn.close()
    return render_template('admin_welcome.html', articles=articles)

github_admin_usernames=["Sahilkumar1272"]
# 
# Github login route
@app.route('/login/github')
def github_login():
    github = oauth.create_client('github')
    redirect_uri = url_for('github_authorize', _external=True)
    return github.authorize_redirect(redirect_uri)

# Github authorize route
@app.route('/login/github/authorize')
def github_authorize():
    github = oauth.create_client('github')
    token = github.authorize_access_token()
    session['github_token'] = token
    resp = github.get('user').json()
    print(f"\n{resp}\n")
    con=connect_db()
    
    
        
    logged_in_username = resp.get('login')
    if logged_in_username in github_admin_usernames:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM news_articles")
        data = cursor.fetchall()
        return render_template("admin_welcome.html",articles=data)
    else:
        return redirect(url_for('index'))


# Logout route for GitHub
@app.route('/logout/github')
def github_logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask application in debug mode
