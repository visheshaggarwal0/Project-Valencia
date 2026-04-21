# Viora Development Journal 📘

This document serves as a living chronological record of Viora's architectural evolution, tracking major engine overhauls, tool expansions, and fundamental capabilities added throughout her development lifecycle.

---

## 🐣 Phase 1: MVP Core
*The foundational building blocks of the Desktop Assistant. Focus was purely on basic capability mapping and zero-shot execution.*

**Architecture:**
- **Standard Langchain Wrapper:** Implemented basic Langchain abstraction layers.
- **Linear Execution:** Simple prompt-in, response-out workflow without self-correction or looping.
- **Flat Memory:** Utilized standard string buffers without database retention capabilities.

**Tool Implementations:**
- **OS Operations:** Hooked physical OS commands (file manipulation, opening apps, system volume control).
- **Automation Libraries:** Implemented basic Python libraries (`PyAutoGUI`, `Pywinauto`, `PSUtil`).
- **Basic Internet:** Hooked DuckDuckGo for generic web search query retrieval.

---

## 🧠 Phase 2: The ReAct Engine 
*Focused on teaching Viora how to systematically plan operations.*

**Architecture:**
- **The ReAct Orchestration Loop:** Migrated the linear script into a robust Agentic ReAct Engine. Viora learned how to "Plan before Executing", spinning up a dedicated Planner LLM to output rigid step-by-step documentation before delegating to the executing loop.

---

## 👁️ Phase 3: Semantic Architecture & Ghost UI
*Focused on remembering the user via local databases, establishing a permanent browser trace, and rendering thoughts natively in the terminal.*

**Architecture:**
- **Ephemeral Ghost CLI:** Hooked Viora into a custom Typer/Rich framework. Built a real-time status UI panel that projects her internal "Thoughts" over a spinner.

**Memory Upgrades:**
- **Vector RAG Engine:** Scrapped legacy flat-JSON persistent storage arrays. Migrated entirely to a local **ChromaDB** vector architecture utilizing `all-MiniLM-L6-v2`. 
- **Semantic Threading:** Viora began searching via cosine-similarity scores to organically weave semantic context blocks into her active pipeline without destroying context limits.

**Tool Enhancements:**
- **Selenium Stealth Migration:** Replaced the Playwright implementation entirely in favor of Edge-powered Selenium.
- **Persistent Web Authentication:** Transition to Selenium enabled permanent user-profile caching, allowing Viora to maintain authenticated states like WhatsApp Web logins across sessions.

---

## 🚀 Phase 4: LangGraph & Deep Vision (Current)
*Focused on extreme token efficiency, fault tolerance, and bridging the gap between obscured web architecture and AI vision capabilities.*

**Architecture:**
- **LangGraph Migration:** Completely stripped out the custom sequential `while` loop engine. Migrated Viora to a LangGraph compiled **State Machine**.
- **Asynchronous Nodes:** Viora engine split into deterministic Nodes (`node_rules`, `node_router`, `node_planner`, `node_reasoner`, `node_tools`). This allows precise fault isolation and natively fixes edge-case infinite loops.
- **Dual-Provider Hybrid Engine:** Introduced granular LLM mapping to solve massive token pollution.
- **Free Local Routing:** The lightweight local `gemma3:1b` (via Ollama) now automatically handles all Intent classification and casual chat (costing 0 API tokens).
- **Heavyweight Reasoning:** The heavyweight `llama-3.3-70b` (via Groq) is strictly reserved for the heavy Execution Reasoner node.

**Optimization & Token Trimming:**
- **Dynamic Skill Binding:** Implemented intelligent tool truncation. Viora now dynamically evaluates the user's intent to ONLY bind relevant tool payloads.
- **Massive Input Truncation:** By only loading exactly what is needed (e.g. 6 Selenium tools instead of 60+ Windows tools for web queries), Prompt tokens were structurally minimized mathematically.
- **Fixed History Drift:** Solved a critical hallucination where lightning-fast Regex bypass tools (like "open notepad") failed to register an `AIMessage` to the graph state, causing the LangChain array to disconnect and hallucinate on subsequent turns.

**Tool Enhancements:**
- **DOM Vision Mapping (`browser_map_elements`):** Deployed a custom JavaScript payload injector into the Selenium wrapper. Viora can now map obscured React infrastructures.
- **Element Targeting:** The JS extracts interactable elements and visually assigns them a clean `viora-id` tag for millimeter-precise UI clicking and typing.
- **Auto-Typer Evolution (`keyboard_type` / `keyboard_press`):** Resolved heavy JS copy/paste blockers on high-security websites. 
- **HID Simulation:** Engineered a 1.0s physical padding delay for UI focus shifting and calibrated keystroke internals to `0.05` to simulate physical human HID typing velocity perfectly.

---

## 🖥️ Phase 5: The Terminal Dashboard (Commencing)
*Focused on replacing the linear CLI script with a fully asynchronous Terminal User Interface (TUI) mapping.*

**Architecture:**
- **Textual UI:** Migrating Typer UI to a full textual dashboard.
- **Background Threading:** Implementing asynchronous LangGraph workers to prevent UI lockups during complex 15+ second web search loops.
