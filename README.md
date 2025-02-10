# Celebrity AI Agent - Bringing Crypto Banter to Life

## 🌟 Overview
This project is all about creating an AI-powered **virtual crypto influencer** that mimics the social media style of a well-known figure in the cryptocurrency world. The AI dynamically grabs **real-time crypto trends**, looks at **past content**, and generates posts that sound just like the celebrity.

## 🤖 Who’s the Celebrity? **Changpeng Zhao (CZ Binance)**
### Why CZ?
- He’s the **founder of Binance**, the biggest crypto exchange.
- He tweets **market insights & motivation** all the time.
- Uses signature catchphrases like *BUIDL, Ignore FUD, SAFU*.
- Super active online with a huge influence in crypto.

## 🎯 How We Built the AI Celebrity

### 📥 **Step 1: Collecting Data**
We gathered content straight from:
✅ **Twitter (X)** – Pulled tweets using **Tweepy**.
✅ **Binance Blog** – Insights into crypto trends.
✅ **YouTube Interviews** – Transcribed CZ’s speeches with **OpenAI Whisper**.
✅ **Telegram Announcements** – Monitored Binance’s updates.

### 🧹 **Step 2: Preprocessing the Content**
- Filtered out **off-topic posts** (like personal stories or tech news).
- Organized posts into:
  - 📊 **Market Updates** (Bitcoin, Ethereum, Altcoins)
  - 💡 **Motivational Posts** ("Ignore FUD, Keep BUIDLing")
  - ⚠️ **Warnings** (Rug pulls, Scams, Centralized risks)
- Stored everything in **ChromaDB** so AI can reference past posts.

### 🏗️ **Step 3: Training the AI**
- Used **Mistral-7B or LLaMA-2 fine-tuned** on CZ’s tweets.
- Integrated **Retrieval-Augmented Generation (RAG)** to keep posts relevant.
- Set **custom prompts** so the AI sounds like CZ.

### 🚨 **Step 4: Making Sure AI Posts Are Safe**
To prevent misinformation or spam:
- 🚫 **Blocked risky words** like "scam", "rug pull", "Ponzi".
- ✅ **Fact-checked against Binance announcements** before posting.
- ✂️ **Kept tweets under 280 characters** so they fit on Twitter.

### 🚀 **Step 5: Auto-Posting to Social Media**
- Pulled **real-time crypto trends** from **CoinGecko API**.
- AI-generated content via **Hugging Face API**.
- **Automatically posted** to:
  - 🐦 **Twitter (X)** using **Tweepy**.
  - 📸 **Instagram** via **Instagram Private API**.

---

## 🛠️ **Technical MVP**
### 🏗️ **Tech Stack**
| Feature | Technology Used |
|-----------|------------|
| API Framework | **FastAPI** |
| AI Model | **Mistral-7B (Hugging Face API)** |
| Storage | **ChromaDB** (for past posts) |
| Social Media API | **Tweepy (Twitter), Instagram Private API** |
| Crypto Trends | **CoinGecko API** |
| Hosting | **Google Cloud / AWS Lambda** |

### 🔄 **How It Works**
1️⃣ **Fetch crypto trends**.
2️⃣ **Retrieve relevant past tweets & insights**.
3️⃣ **Generate AI-powered content**.
4️⃣ **Vetting for safety & compliance**.
5️⃣ **Auto-post to social media**.

---

## ⚙️ **Installation & Setup**
### 🏁 **1. Clone the Repo**
```bash
git clone https://github.com/saadkhalid-git/crypto_ai_agent
cd celebrity-ai-agent
```

### 🏗️ **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### 🔑 **3. Set Up Environment Variables**
Create a `.env` file and add:
```ini
HUGGINGFACE_API_KEY=your_api_key
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
```

### 🚀 **4. Run the FastAPI Server**
```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

### 🌍 **5. Test the API**
Visit:
```
http://127.0.0.1:8000/generate_post
```

---

## 🔗 **API Endpoints**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/generate_post` | Fetches crypto trends, generates a post, and auto-publishes it. |

---

## 🔮 **What’s Next?**
- Train the AI on **even more CZ tweets**.
- Add **multi-language support** for global engagement.
- Implement **real-time monitoring & sentiment analysis** before posting.
- Build a **Telegram bot** for direct engagement.

