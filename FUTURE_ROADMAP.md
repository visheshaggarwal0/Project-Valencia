# Viora Architectural Roadmap 🌐
*The Next Generation of the Viora Multi-Agent Ecosystem*

This document serves as the theoretical and structural blueprint for Viora's upcoming expansion phases. The core objective is to transition Viora from a singular linear LLM Assistant into a highly concurrent, fully automated **Multi-Agent Network** capable of self-expansion and background processing.

---

## 1. The Plugin Engine (Self-Coding Modularity)
**Goal**: Decouple static tool functions from Viora's code base to allow "plug-and-play" capability extensions without requiring structural reboots.
- **Dynamic Mounting**: Develop a root `/plugins` directory. `tools_factory.py` will utilize native Python `importlib` to hot-swap and auto-bind any `.py` script dropped into the folder structurally into the active LLM vocabulary.
- **Auto-Coding Capability**: Equip Viora with a `write_plugin_to_disk()` tool. If assigned a new application to master, the Groq Llama-3 Reasoner will dynamically write the Python UI logic, compile it as a tool, and physically drop it into the Plugin folder, achieving **Self-Expansion capability**.

## 2. Multi-Agent Swarm (Supervisor Topology)
**Goal**: Re-forge `node_reasoner` into a LangGraph Supervisor to handle parallel, intensive delegations.
- **Fan-Out Parallel Processing**: The Supervisor node will have the ability to read a user's multi-step intent and parallelize the tasks. E.g., instructing the `agent_researcher` to browse Wikipedia while simultaneously instructing the `agent_analyst` to scan a local data CSV.
- **Model Triangulation**: Each Sub-Agent is assigned a specialized local/remote LLM tailored strictly to their function (e.g. Anthropic `Claude-3.5-Sonnet` for the Python Coder Agent, Google `Gemini` for the 2M context-window Web Surfer Agent).
- **Asynchronous Fan-In**: The Supervisor awaits the resolution of all sub-agents simultaneously via asynchronous API streams, cutting massive latency from compound workflows. 

## 3. Autonomous Chronological Agents (Background Threading)
**Goal**: Break the "Request-Response" conversational shackle. Give Viora autonomous temporal awareness.
- **APScheduler Integration**: Deploy background threads completely isolated from the Typer UI CLI pipeline. 
- **Time-Locked Triggers**: The user can instruct: *"At 5:00 PM every weekday, boot chromium, check my unread emails, close it, and send a summary message directly to my console."* Viora runs the sub-agent graph silently in the background while the user continues normal UI work.

## 4. Multimodal Desktop "Vision" (The Visual Oracle)
**Goal**: Grant Viora pixel-perfect awareness of the OS screen natively to augment brittle DOM-mapping.
- **Master Vision Toggle**: Implemented via `.env` (`VIORA_VISION_ENABLED`). This grants the user strict structural control over when Viora is allowed to physically take a snapshot, preventing unnecessary token usage when disabled.
- **Decoupled Architecture**: Viora limits Gemini strictly to image analysis. Gemini receives the base64 screenshot and returns physical coordinate geometry points as text strings.
- **Groq Handoff**: The text returned from Gemini is intercepted and routed directly back to the Groq Llama-3 Executor LLM. Groq dynamically maps those raw vectors into its native `mouse_click(x, y)` toolset without ever breaking its internal context.

## 5. Dedicated Terminal Dashboard (TUI)
**Goal**: Rebuild the Viora frontend CLI to mimic professional dev-tools like the Gemini SDK and Vercel CLI.
- **Textual / Prompt Toolkit Integration**: Strip out the basic top-to-bottom synchronous scrolling UI from Typer. Deploy a locked-screen Terminal User Interface (TUI).
- **Layout Architecture**: 
  - **Top Bar**: Viora versioning and active system network status.
  - **Main Console View**: Rich text rendering of previous chat logs, separated by magenta execution bounds.
  - **Dynamic Footer**: Real-time Groq API token tracking (Prompt vs Completion), execution cost estimates, and current `.venv` target.
  - **Command Deck**: A persistent floating text-input box anchored at the absolute bottom of the terminal window, supporting multi-line editing and history-scrolling.

---
*Roadmap curated based on deep architectural scaling discussions covering Agent synchronization, Task Allotment, LLM Specialization, and Memory efficiency.*
