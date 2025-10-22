# 📖 Bible Verse Agent

A powerful AI agent built with the [Sentient Agent Framework](https://github.com/sentient-agi/Sentient-Agent-Framework) that fetches Bible verses and provides detailed explanations using FireworksAI's Llama model.

## ✨ Features

- 📖 **Fetch Bible Verses** - Get verses from bible-api.com (KJV and other translations)
- 🤖 **AI Explanations** - Powered by FireworksAI's Llama models
- 💾 **Smart Caching** - Cache explanations for 7 days to reduce API costs
- 🔍 **Smart Parsing** - Automatically extracts verse references from natural language
- ⚡ **Real-time Streaming** - Stream AI explanations as they're generated
- 🎯 **Multiple Formats** - Supports full names, abbreviations, and verse ranges

## 📋 Requirements

- Python 3.9 or higher
- FireworksAI API key (get from [fireworks.ai](https://fireworks.ai/))
- Internet connection (for Bible API and FireworksAI)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo>
cd bible-verse-agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your FireworksAI API key
# Get your API key from: https://fireworks.ai/
```

Your `.env` should look like:
```bash
FIREWORKS_API_KEY=your_actual_api_key_here
FIREWORKS_MODEL=accounts/fireworks/models/llama-v3p1-8b-instruct
BIBLE_TRANSLATION=KJV
BIBLE_ENABLE_CACHE=True
```

### 3. Run the Agent

```bash
python main.py
```

You should see:
```
============================================================
📖 Bible Verse Agent Started
============================================================
📚 Bible API: https://bible-api.com
📖 Translation: KJV
🤖 LLM Model: accounts/fireworks/models/llama-v3p1-8b-instruct
💾 Cache: Enabled
   - TTL: 168 hours
🎯 Status: Ready to explain Bible verses
============================================================
```

## 💬 Usage

### Using cURL

```bash
curl -N --location 'http://localhost:8000/assist' \
--header 'Content-Type: application/json' \
--data '{
  "query": {
    "id": "01K6YDCXXV62EJV0KAP7JEGCGP",
    "prompt": "According to Matthew 7:7, what did Jesus tell his disciples?"
  },
  "session": {
    "processor_id": "Bible Verse Agent",
    "activity_id": "01JR8SXE9B92YDKKNMYHYFZY1T",
    "request_id": "01JR8SY5PHB9X2FET1QRXGZW76",
    "interactions": []
  }
}'
```

### Example Queries

1. **Direct verse request:**
   ```
   "Explain John 3:16"
   ```

2. **Question format:**
   ```
   "According to Matthew 7:7, what did Jesus tell his disciples?"
   ```

3. **Multiple verses:**
   ```
   "What does Romans 8:28 mean?"
   ```

4. **Verse ranges:**
   ```
   "Explain John 3:16-17"
   ```

### Using the Sentient Agent Client

```bash
# Clone the client
git clone https://github.com/sentient-agi/Sentient-Agent-Client.git
cd Sentient-Agent-Client

# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run
python3 -m src.sentient_agent_client --url http://localhost:8000/assist
```

## 📁 Project Structure

```
bible-verse-agent/
├── src/
│   └── bible_agent/
│       ├── __init__.py
│       ├── agent.py              # Main agent orchestration
│       ├── bible_service.py      # Bible API integration
│       └── llm_service.py        # FireworksAI LLM service
├── config/
│   ├── __init__.py
│   ├── bible_config.py           # Bible API configuration
│   └── llm_config.py             # FireworksAI configuration
├── utils/
│   ├── __init__.py
│   ├── cache.py                  # Caching system
│   └── verse_parser.py           # Verse reference parser
├── .cache/                       # Cache directory (auto-created)
├── main.py                       # Entry point
├── .env                          # Your environment variables (not committed)
├── .env.example                  # Environment template
├── requirements.txt
└── README.md
```

## 🔧 Configuration

### Bible Translation

Change the translation in `.env`:
```bash
# Options: KJV, ASV, WEB, etc.
BIBLE_TRANSLATION=KJV
```

### LLM Model

Switch to a different Llama model in `.env`:
```bash
# Options:
# - accounts/fireworks/models/llama-v3p1-8b-instruct (fast, free)
# - accounts/fireworks/models/llama-v3p1-70b-instruct (better quality)
# - accounts/fireworks/models/llama-v3p1-405b-instruct (best quality)
FIREWORKS_MODEL=accounts/fireworks/models/llama-v3p1-8b-instruct
```

### Cache Settings

Adjust cache duration in `.env`:
```bash
BIBLE_ENABLE_CACHE=True
BIBLE_CACHE_TTL_HOURS=168  # 7 days
```

### Temperature & Tokens

Fine-tune AI responses in `.env`:
```bash
LLM_TEMPERATURE=0.7      # 0.0-1.0 (lower = more focused)
LLM_MAX_TOKENS=1024      # Maximum response length
LLM_TOP_P=0.9           # Nucleus sampling
```

## 📖 Supported Verse Formats

The agent understands various formats:

| Input | Parsed As |
|-------|-----------|
| `Matthew 7:7` | Matthew 7:7 |
| `Matt 7:7` | Matthew 7:7 |
| `Mt 7:7` | Matthew 7:7 |
| `John 3:16-17` | John 3:16-17 |
| `1 Corinthians 13:4` | 1 Corinthians 13:4 |
| `Psalm 23:1` | Psalms 23:1 |

## 🎯 Response Format

The agent returns structured responses:

1. **STATUS** - Current processing status
2. **VERSE_DATA** - JSON with verse metadata
3. **VERSE_TEXT** - Formatted verse text
4. **EXPLANATION** - Streamed AI explanation

Example:
```
event: STATUS
data: {"content": "📖 Looking up Matthew 7:7..."}

event: VERSE_TEXT
data: {"content": "**Matthew 7:7** (King James Version)\n\nAsk, and it shall be given you..."}

event: EXPLANATION
data: {"content": "## 📚 Explanation\n\nIn this verse, Jesus teaches..."}
```

## 🐛 Troubleshooting

### "FIREWORKS_API_KEY is not set"
- Make sure you created a `.env` file
- Add your API key: `FIREWORKS_API_KEY=your_key_here`

### "Verse not found"
- Check the verse reference spelling
- Ensure the verse exists in the Bible
- Try the full book name: "Matthew" instead of "Mt"

### Connection errors
- Check your internet connection
- Verify FireworksAI API is accessible
- Check if bible-api.com is available

### Cache issues
- Delete the `.cache` folder to clear cache
- Disable cache: `BIBLE_ENABLE_CACHE=False` in `.env`

## 🌟 Examples

### Example 1: Simple Query
```
User: "Explain John 3:16"

Agent Response:
📖 Looking up John 3:16...

**John 3:16** (King James Version)
For God so loved the world, that he gave his only begotten Son...

## 📚 Explanation
This is perhaps the most famous verse in the Bible...
```

### Example 2: Question Format
```
User: "According to Matthew 7:7, what did Jesus tell his disciples?"

Agent Response:
📖 Looking up Matthew 7:7...

**Matthew 7:7** (King James Version)
Ask, and it shall be given you; seek, and ye shall find...

## 📚 Explanation
In this teaching from the Sermon on the Mount, Jesus encourages...
```

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [Sentient Agent Framework](https://github.com/sentient-agi/Sentient-Agent-Framework)
- Bible verses from [bible-api.com](https://bible-api.com)
- AI explanations powered by [FireworksAI](https://fireworks.ai/)

## 📧 Support

For issues and questions:
- GitHub Issues: [Create an issue]()
- Email: chikwetech@gmail.com

---

Built with ❤️ using the Sentient Agent Framework
