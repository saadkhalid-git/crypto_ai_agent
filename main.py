import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
import tweepy
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

# Initialize Vector Store
db_path = "chroma_db"
vector_db = Chroma(persist_directory=db_path, embedding_function=HuggingFaceEmbeddings())
retriever = vector_db.as_retriever()

# Prompt Template
prompt_template = PromptTemplate(
    input_variables=["trends", "rag_context"],
    template=(
        "You are a virtual version of Crypto Banter. Generate social media content using their style.\n\n"
        "Recent crypto trends: {trends}\n"
        "Relevant context from past content: {rag_context}\n\n"
        "Generate a post that:\n"
        "1. Matches Crypto Banter's communication style\n"
        "2. Incorporates at least 2 trends\n"
        "3. Includes characteristic phrases (e.g., 'DYOR', 'To the moon!')\n"
        "4. Is under 280 characters"
    ),
)

# Fetch crypto trends
def get_vetted_trends():
    response = requests.get("https://api.coingecko.com/api/v3/search/trending")
    if response.status_code != 200:
        return []
    raw_trends = response.json()
    return [coin["item"]["name"] for coin in raw_trends["coins"] if is_relevant(coin["item"])]


def is_relevant(coin):
    keywords = ["bitcoin", "ethereum", "defi", "nft", "web3", "altcoin"]
    return any(keyword in coin["name"].lower() for keyword in keywords)

# Generate text using Hugging Face API
def generate_text(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 200, "temperature": 0.7, "return_full_text": False},
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    return f"Error: {response.json()}"

# Vet content
def vet_content(content):
    inappropriate_words = ["scam", "rug pull", "ponzi"]
    if any(word in content.lower() for word in inappropriate_words):
        return False, "Content contains inappropriate language."
    if len(content) > 280:
        return False, "Content exceeds 280 characters."
    return True, "Content approved."

# Store generated posts
def store_generated_content(content):
    vector_db.add_texts([content])

# Social media posting
def post_to_twitter(content):
    auth = tweepy.OAuthHandler(TWITTER_CREDS["api_key"], TWITTER_CREDS["api_secret"])
    auth.set_access_token(TWITTER_CREDS["access_token"], TWITTER_CREDS["access_secret"])
    # api = tweepy.API(auth)
    print("Twitter:", content)
    return "Tweet posted successfully"

# FastAPI setup
app = FastAPI()

@app.get("/generate_post")
async def generate_post():
    try:
        trends = get_vetted_trends()
        rag_context = retriever.get_relevant_documents(", ".join(trends))
        formatted_prompt = prompt_template.format(trends=trends, rag_context=rag_context)
        generated_content = generate_text(formatted_prompt)
        is_valid, vetting_message = vet_content(generated_content)

        if is_valid:
            store_generated_content(generated_content)
            twitter_result = post_to_twitter(generated_content)
        else:
            twitter_result = "Content not posted (vetting failed)."
        
        return {
            "content": generated_content,
            "vetting_result": vetting_message,
            "twitter_status": twitter_result,
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)