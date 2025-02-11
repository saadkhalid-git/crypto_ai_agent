import os
import requests
import tweepy
import time
import psycopg2
import random
import agentops
from dotenv import load_dotenv
from langchain.chains import SequentialChain
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from agentops.partners.langchain_callback_handler import (
    LangchainCallbackHandler as AgentOpsLangchainCallbackHandler,
)
from agentops.decorators import track_agent 

# Load environment variables
load_dotenv()

# API Keys & Credentials
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
AGENT_OPS_API_KEY = os.getenv("AGENT_OPS_API_KEY")

agentops.init(AGENT_OPS_API_KEY, default_tags=["AI_Agent", "Monitoring"])

API_URL = (
    "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
)
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
    """Establish a connection to PostgreSQL."""
    return psycopg2.connect(DB_CONNECTION)


def create_tables():
    """Create necessary tables if they don't exist."""
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
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
            """
            )
            conn.commit()


# Initialize Vector Store
db_path = "chroma_db"
vector_db = Chroma(
    persist_directory=db_path, embedding_function=HuggingFaceEmbeddings()
)
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


@agentops.record_action("Fetching Trends")
def get_vetted_trends():
    """Fetch and filter trending crypto topics from CoinGecko."""
    response = requests.get("https://api.coingecko.com/api/v3/search/trending")
    if response.status_code != 200:
        return []
    raw_trends = response.json()
    return [
        coin["item"]["name"]
        for coin in raw_trends["coins"]
        if is_relevant(coin["item"])
    ]


def is_relevant(coin):
    """Check if a coin is relevant based on specific keywords."""
    keywords = ["bitcoin", "ethereum", "defi", "nft", "web3", "altcoin"]
    return any(keyword in coin["name"].lower() for keyword in keywords)


@agentops.record_action("Generating AI Content")
def generate_text(prompt):
    """Generate social media content using the AI model."""
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "return_full_text": False,
        },
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        return "Error: Unexpected API response format."

    return f"Error: {response.json()}"


@agentops.record_action("Vetting Content")
def vet_content(content):
    """Check if generated content meets platform guidelines."""
    inappropriate_words = ["scam", "rug pull", "ponzi"]
    if any(word in content.lower() for word in inappropriate_words):
        return False, "Content contains inappropriate language."
    if len(content) > 280:
        return False, "Content exceeds 280 characters."
    return True, "Content approved."


@agentops.record_action("Posting to Social Media")
def post_to_twitter(content):
    """Simulate posting to Twitter."""
    likes = random.randint(100, 10000)
    comments = random.randint(10, 500)
    retweet_count = random.randint(10, 10000)
    print(
        "Twitter:",
        content,
        f"Likes: {likes}, Comments: {comments}, Retweets: {retweet_count}",
    )
    return "Tweet posted successfully"


@agentops.record_action("Posting to Instagram")
def post_to_instagram(content):
    """Simulate posting to Instagram."""
    likes = random.randint(100, 10000)
    comments = random.randint(10, 500)
    print(f"Instagram: {content} | Likes: {likes} | Comments: {comments}")
    return "Instagram post saved successfully"


@agentops.record_action("Running AI Agent")
def run_agent():
    """Main function to run the AI agent for content generation and posting."""

    create_tables()
    try:
        print("Running AI agent...")
        trends = get_vetted_trends()
        if not trends:
            print("No relevant trends found. Skipping this cycle.")
            time.sleep(300)
            return

        rag_context_list = retriever.get_relevant_documents(", ".join(trends))
        rag_context = " ".join(
            [doc.page_content for doc in rag_context_list]
        )  # Ensure correct formatting

        formatted_prompt = prompt_template.format(
            trends=", ".join(trends), rag_context=rag_context
        )
        generated_content = generate_text(formatted_prompt)

        is_valid, vetting_message = vet_content(generated_content)
        if is_valid:
            post_to_twitter(generated_content)
            post_to_instagram(generated_content)

        print("AI Agent Cycle Complete")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    run_agent()
    agentops.end_session('Success')
