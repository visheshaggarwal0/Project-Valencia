# Viora 🤖✨

**Viora** is a next-generation, autonomous AI agent for your Windows Desktop. Engineered with a **ReAct (Plan-and-Execute)** orchestration loop, Viora doesn't just respond to chats—it independently creates execution strategies to drive your desktop, automate browsers, and solve complex workflows utilizing advanced LLM reasoning (via Groq, Ollama, or Gemini).

![Viora Banner](https://img.shields.io/badge/Status-Active-brightgreen) ![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue) ![License](https://img.shields.io/badge/License-MIT-purple)

---

## 🌟 Key Upgrades & Features

### 🧠 ReAct Engine & Ephemeral CLI
- **Autonomous Reasoning System**: Viora synthesizes instructions, creates a multi-step action plan, and dynamically invokes specific tools (over 60+ available) until the task is structurally complete.
- **"Ghost" Spinner UI**: Terminal logs and thought-processes are injected directly into a breathtaking, rich CLI loading spinner that evaporates the exact millisecond the task concludes, maintaining a pristine terminal layout without token pollution.

### 🗄️ ChromaDB RAG Architecture
- **Vector Memory Core**: Viora has true long-term memory! Using `all-MiniLM-L6-v2` embeddings via **ChromaDB**, every interaction is parsed into semantic vectors.
- **Dynamic Context Injection**: When you ask a question, Viora natively queries the Top 4 most relevant past conversational chunks and organically injects them into its awareness stream, enabling deep personalization while minimizing token cost.

### 🌐 Selenium Web Automation
- **Unrestricted Access**: Playwright was globally swapped for **Selenium** to enable robust Edge wrapper manipulation, persistent cookie profile injection, and native bypasses for automated browser restrictions. Log into WhatsApp Web once, and Viora remembers you in its persistent profile storage forever. 

### 🖥️ Native Desktop Operations
- **System Hacking**: Native integration with `PyAutoGUI`, `pywinauto`, and `pygetwindow`.
- Instruct Viora to open `notepad.exe`, type a specific greeting, adjust your volume, capture targeted screenshots, compute screen pixels, or read/write to your local clipboard.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Windows OS
- API keys for **Groq** (Recommended for Llama-3.3 70b inference speed)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/viora.git
cd viora
```

2. **Initialize Environment**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file in the project root:
```env
VIORA_MODEL_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here  # Optional fallback
```

4. **Launch the Agent**
Viora utilizes the elegant `typer` framework. Boot into the rich CLI interface:
```bash
python viora.py chat
```

## 💡 Usage Examples

Drop directly into your terminal and start giving commands naturally:

- **Desktop Action**: *"Open notepad, type out a quick goodbye message to Mom, save it, and then take a screenshot of my screen."*
- **Web Auto**: *"Open browser, research the current Indian President, and give me a brief summary."*
- **System Hook**: *"Mute my system volume, then read me my clipboard contents."*
- **Semantic Memory**: *"Do you remember what my favorite coffee shop is from last week?"*

## 📁 System Architecture

```
viora/
├── agent/
│   ├── brain.py          # Core ReAct & Router Agent Loop
│   └── memory.py         # ChromaDB Vector RAG Engine
├── skills/
│   ├── selenium_skills.py# Selenium Web Driver wrapper (Stealth)
│   ├── windows_skills.py # OS, Window handling, Sound, Apps
│   ├── todo_skills.py    # Organic Task tracking
│   └── tools_factory.py  # Pydantic Schema & Tool execution map
├── data/
│   ├── chroma_db/        # [Generated] Local Vector Embeddings
│   └── browser_profile_selenium/ # [Generated] Persistent Cookies
├── viora.py              # Typer CLI Entrypoint
├── requirements.txt      # Dependencies
└── .env                  # Core Configuration Keys
```

---

**Made with ❤️ for the pursuit of true artificial desktop automation.**
