# Viora 🤖✨

**Viora** is a next-generation, autonomous AI agent for your Windows Desktop. Engineered entirely on a **LangGraph Asynchronous State Machine**, Viora doesn't just respond to chats—she mathematically calculates execution loops, delegates tasks across an independent Multi-Agent Hybrid LLM swarm, automates Chrome dynamically via DOM-Mapping, and caches complex automations to run at zero-token latency.

![Viora Banner](https://img.shields.io/badge/Status-Active-brightgreen) ![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue) ![License](https://img.shields.io/badge/License-MIT-purple)

---

## 🌟 Key Architectural Upgrades (Phase 4.0)

### 🧠 LangGraph State Machine & Multi-Agent Swarm
- **Deterministic Node Execution**: Viora stripped out legacy linear arrays and migrated to independent, asynchronous nodes (`router`, `planner`, `reasoner`, `tools`). This completely isolates logical failure loops and prevents infinite AI hallucination chains.
- **Dual-Model Hybrid Swarm**: Massive Token cost mitigation! Viora runs a local background `gemma3:1b` (via Ollama) worker that handles all Chat, Intent Routing, and Fact Extraction natively for exactly $0. Heavyweight reasoning delegates strictly to `llama-3.3-70b` (via Groq) ONLY when complex execution pathways are required.

### ⚡ Zero-Token Semantic Routine Cache
- **Instant Tethers**: Anytime Viora natively executes a complex physical OS workflow, she calculates a vector mapping of the prompt into a `viora_routines` ChromaDB. 
- **Topological Bypassing**: When you ask her to do the same task again, LangGraph intercepts the routing natively and **completely bypasses the Groq LLM logic**, streaming the Python execution callbacks synchronously. 100% execution, 0% token waste.

### 🗄️ Background Fact Extraction (Memory Engine)
- **Latent Intelligence**: While Viora talks to you, a background `Ollama` thread silently analyzes her context to extract distinct permanent variables about your life, burning them into a long-term vector database. 

### 🌐 Obscured DOM Vision (Selenium Override)
- **Intelligent Web Extraction**: Legacy automated AI fails on modern React applications. Viora dynamically injects a custom JS script (`browser_map_elements`) onto live web pages to strip the DOM naked, mapping completely arbitrary tags with custom `viora-id` tags for pinpoint precision clicking and typing across security layers (e.g. WhatsApp, Amazon).

---

## 🚀 Quick Start (Global Installation)

### Prerequisites
- Python 3.9+ (Windows OS exclusively)
- Groq API Key (Extremely vital for Llama-3.3 Reasoning engine)
- Ollama installed natively with `gemma3:1b`

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
VIORA_ROUTER_PROVIDER=ollama
VIORA_REASONING_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
```

4. **Install Global Windows Execution (The Magic)**
Execute the native system-path registry linker:
```bash
python install_cli.py
```
> [!NOTE]
> Close all your terminal windows! You can now open a terminal anywhere on your entire Windows computer and simply type `viora chat` to instantly boot the agent. No more manual `.venv` navigation ever again.

## 💡 Usage Examples

Drop directly into your terminal and start giving commands naturally:

- **Desktop Action**: *"Open notepad, type out a quick goodbye message to Mom, save it, and then take a screenshot of my screen."*
- **Web Auto**: *"Open browser, map the elements, search the current Indian President, and give me a brief summary."*
- **System Hook**: *"Mute my system volume, then read me my clipboard contents."*
- **Semantic Memory**: *"Do you remember what my favorite coffee shop is from last week?"*

## 📁 Core System Architecture

```
viora/
├── agent/
│   ├── brain.py          # Native LangGraph State Machine Blueprint
│   └── memory.py         # Semantic Caching & Vector Fact Extraction
├── skills/
│   ├── selenium_skills.py# DOM Vision Map API
│   ├── windows_skills.py # OS Operations & Local Vision
│   ├── todo_skills.py    # Organic Task Vector tracking
│   └── tools_factory.py  # Pydantic Schema mapping
├── install_cli.py        # Windows Path Connector
├── viora.bat             # Global Execution Override
├── data/                 # [DB] Long-Term Storage
├── viora.py              # CLI Output Interface
├── requirements.txt      
└── .env                  
```

---

**Made with ❤️ for the pursuit of true artificial desktop automation.**
