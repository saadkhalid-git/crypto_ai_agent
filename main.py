import os
import requests
import tweepy
import time
import psycopg2
import random
from dotenv import load_dotenv
from langchain.chains import SequentialChain
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# API Keys & Credentials
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
TWITTER_CREDS = {
    "api_key": os.getenv("TWITTER_API_KEY"),
    "api_secret": os.getenv("TWITTER_API_SECRET"),
    "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
    "access_secret": os.getenv("TWITTER_ACCESS_SECRET"),
}
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# PostgreSQL Connection
DB_CONNECTION = os.getenv("POSTGRES_CONNECTION_STRING")

def connect_db():
    return psycopg2.connect(DB_CONNECTION)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tweets (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            retweet_count INT DEFAULT 0,
            comments_count INT DEFAULT 0,
            likes_count INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS instagram_posts (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            likes_count INT DEFAULT 0,
            comments_count INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Initialize Vector Store
db_path = "chroma_db"
vector_db = Chroma(persist_directory=db_path, embedding_function=HuggingFaceEmbeddings())
retriever = vector_db.as_retriever()

# Prompt Template
prompt_template = PromptTemplate(
    input_variables=["trends", "rag_context"],
    template=(
        "You are a virtual AI agent for Crypto Banter. Generate social media content using their style.\n\n"
        "Recent crypto trends: {trends}\n"
        "Relevant context from past content: {rag_context}\n\n"
        "Generate a post that:\n"
        "1. Matches Crypto Banter's communication style\n"
        "2. Incorporates at least 2 trends\n"
        "3. Includes characteristic phrases (e.g., 'DYOR', 'To the moon!')\n"
        "4. Is under 280 characters"
    ),
)


def get_vetted_trends():
    response = requests.get("https://api.coingecko.com/api/v3/search/trending")
    if response.status_code != 200:
        return []
    raw_trends = response.json()
    return [coin["item"]["name"] for coin in raw_trends["coins"] if is_relevant(coin["item"])]

def is_relevant(coin):
    keywords = ["bitcoin", "ethereum", "defi", "nft", "web3", "altcoin"]
    return any(keyword in coin["name"].lower() for keyword in keywords)


def generate_text(prompt):
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 200, "temperature": 0.7, "return_full_text": False}}
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    return f"Error: {response.json()}"


def vet_content(content):
    inappropriate_words = ["scam", "rug pull", "ponzi"]
    if any(word in content.lower() for word in inappropriate_words):
        return False, "Content contains inappropriate language."
    if len(content) > 280:
        return False, "Content exceeds 280 characters."
    return True, "Content approved."


def store_generated_content(content):
    vector_db.add_texts([content])

def store_post_in_db(table, content, likes=None, comments=None, retweet_count=None):
    conn = connect_db()
    cursor = conn.cursor()
    if table == "tweets":
        cursor.execute("INSERT INTO tweets (content, likes_count, comments_count, retweet_count) VALUES (%s, %s, %s, %s)", (content, likes, comments, retweet_count))
    elif table == "instagram_posts":
        cursor.execute("INSERT INTO instagram_posts (content, likes_count, comments_count) VALUES (%s, %s, %s)", (content, likes, comments))
    conn.commit()
    cursor.close()
    conn.close()


def post_to_twitter(content):
    auth = tweepy.OAuthHandler(TWITTER_CREDS["api_key"], TWITTER_CREDS["api_secret"])
    auth.set_access_token(TWITTER_CREDS["access_token"], TWITTER_CREDS["access_secret"])
    likes = random.randint(100, 10000)
    comments = random.randint(10, 500)
    retweet_count = random.randint(10, 10000)
    print("Twitter:", content, likes, comments, retweet_count)
    store_post_in_db("tweets", content)
    return "Tweet posted successfully"


def post_to_instagram(content):
    likes = random.randint(100, 10000)
    comments = random.randint(10, 500)
    print(f"Instagram: {content} | Likes: {likes} | Comments: {comments}")
    store_post_in_db("instagram_posts", content, likes, comments)
    return "Instagram post saved successfully"


def run_agent():
    create_tables()
    while True:
        try:
            print("Running AI agent...")
            trends = get_vetted_trends()
            print("Trends:", trends)
            rag_context = retriever.get_relevant_documents(", ".join(trends))
            formatted_prompt = prompt_template.format(trends=trends, rag_context=rag_context)
            generated_content = generate_text(formatted_prompt)
            is_valid, vetting_message = vet_content(generated_content)
            if is_valid:
                store_generated_content(generated_content)
                post_to_twitter(generated_content)
                post_to_instagram(generated_content)
            print("AI Agent Cycle Complete")
        except Exception as e:
            print(f"Error: {str(e)}")
        time.sleep(300)  # Run every 5 minutes

if __name__ == "__main__":
    run_agent()
