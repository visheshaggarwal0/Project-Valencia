# Viora: Autonomous AI Desktop Agent
**Technical Project Report & Architectural Overview**

---

## 1. Introduction
Viora is an advanced, autonomous AI-powered assistant designed to operate native Windows applications, manage local hardware, execute complex browser automation, and process semantic memory. Unlike traditional scripted chatbots, Viora leverages a **ReAct (Reasoning + Acting)** cognitive loop, enabling it to break down complex human requests into logical steps, autonomously call deterministic code functions (Tools), and process environmental feedback dynamically.

---

## 2. Core Architecture

Viora’s intelligence relies on a dual-provider **Hybrid LLM Architecture** using LangChain. This prevents API rate limitations and guarantees extreme efficiency.

### 2.1 The Router LLM (Intent Classification)
- **Engine**: Local Ollama Server (`gemma3:1b` or comparable lightweight model).
- **Purpose**: When a user inputs a command, the prompt first hits the Router LLM. This model statically analyzes the text to determine the "Intent" (`CHAT` vs `TOOL`). 
- **Efficiency**: Because this model runs locally on the user's hardware, casual conversations, greetings, and basic intent parsing cost **0 API tokens** and execute instantly.

### 2.2 The Reasoning LLM (ReAct Engine)
- **Engine**: Groq Inference API (`llama-3.3-70b-versatile` / `llama3.1`).
- **Purpose**: If the Router determines an action is needed, the request is passed to the Reasoning LLM. 
- **Execution Loop**:
  1. **Planning**: The LLM reviews active tools, assesses the end goal, and dynamically generates a sequential blueprint (e.g., *1. Open Browser 2. Navigate to URL 3. Extract DOM 4. Click specific ID*).
  2. **Action**: The LLM outputs structured `ToolCalls` mapping directly to Pydantic schemas in the Python backend.
  3. **Observation**: Python executes the code (e.g., clicking a button) and feeds the result back to the LLM. The LLM loops until the task succeeds.

---

## 3. Cognitive Systems

### 3.1 Long-Term Semantic Memory (ChromaDB RAG)
Traditional bots pass endless chat logs to the LLM, leading to token exhaustion and latency. Viora bypasses this using **Retrieval-Augmented Generation (RAG)** via `chromadb`.
- **Vector Embedding**: Every interaction is mathematical converted to vectors using the `all-MiniLM-L6-v2` dense embedding model and stored in a persistent local database.
- **Dynamic Context Injection**: When the user asks a personal question, Viora computes the Cosine Similarity of the prompt against the database. It retrieves the top 4 most semantically matching memories and implicitly injects them into the systemic prompt. Viora functionally "remembers" thousands of data points while maintaining a minimal operational context window.

### 3.2 Ephemeral UI (Rich CLI)
Viora leverages the `rich` UI library on a secondary Python thread to render complex internal thoughts directly to the terminal.
- **Garbage Collection Optimization**: Viora overwrites execution logs directly onto the spinner object `status.update()`. The second the action completes, the logs evaporate, maintaining a pristine user interface and preventing terminal buffer overflow, followed up by a hard `os._exit(0)` to prevent native `atexit` exceptions common with threaded UI loops.

---

## 4. Hardware and Automation Capabilities

### 4.1 "Vision" DOM Mapping Engine (Selenium)
Automating obfuscated web frameworks (like React apps or WhatsApp Web) is incredibly difficult because element class names are fully randomized (e.g., `<div class="_ak8j">`). Viora bypasses this limitation with a custom JavaScript injection engine.
- When Viora invokes `browser_map_elements`, Python halts the browser and executes an injection script that parses all visible interactable elements (buttons, inputs, roles) via viewport geometry (`getBoundingClientRect`). 
- A unique custom attribute (`viora-id`) is stamped onto every interactable entity. 
- Viora receives a pure map `[18] <input> "Type a message"`. The AI then simply triggers `browser_type(selector="[viora-id='18']")`.

### 4.2 Operating System Manipulation
Viora executes Python OS libraries to fundamentally alter host system states:
- **PyAutoGUI & pywinauto**: Synthesizes algorithmic mouse tracking, raw keystroke events, window enumeration, and window positioning.
- **Hardware Abstraction**: Has programmatic parity with deep system hardware, permitting dynamic OS volume tuning, clipboard exploitation, file hierarchy destruction/creation, and application instancing.

---

## 5. Conclusion
Viora is not just an API wrapper; it is an intelligent, reactive agentic layer living atop a sophisticated Python toolkit. By bridging localized fast-parsing LLMs with heavy-compute cloud models, and tying Vector RAG Memory to a custom OS interaction core, it provides an unrestrictive blueprint for future AI-integrated desktop environments.
