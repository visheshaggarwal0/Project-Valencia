import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
    BaseMessage,
)
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from skills.tools_factory import get_viora_tools

load_dotenv()


class Brain:
    def __init__(self):
        self.provider = os.getenv("VIORA_MODEL_PROVIDER", "groq").lower()
        self.all_tools = get_viora_tools("ALL")
        self.tool_map = {tool.name: tool for tool in self.all_tools}
        self.should_exit = False

        # Initialize LLMs
        self.router_llm = self._create_llm(model="gemma3:1b", tools=[])
        self.reasoning_llm = self._create_llm(model="llama3.1", tools=self.all_tools)

        self.history: List[BaseMessage] = [
            SystemMessage(
                content="""
You are Viora, a helpful and friendly AI assistant.

CORE BEHAVIOR:
1. CHAT FIRST: Prioritize chatting and being helpful.
2. CONFIRM BEFORE TOOLS: Always ask for confirmation before using browser, search, or automation tools unless the user explicitly requested the action (e.g. "open notepad").
3. GREETINGS: Respond warmly to greetings naturally.
4. TERMINATION: Use the `terminate` tool when the user says "bye", "exit", or wants to quit.
5. CURRENT FACTS: Whenever a query involves current events, specific people, dates, or information you are uncertain about, ALWAYS use the `web_search` tool to search for the most up-to-date information before responding.
6. SUMMARIZATION: After searching, provide a concise and helpful summary of the findings.
7. SCREENSHOTS: Use `take_screenshot` for screen captures.

Be concise. Think step by step.
"""
            )
        ]

        # Token tracking
        self.session_tokens = {"prompt": 0, "completion": 0, "total": 0}
        self.last_response_tokens = None

        # Tools setup
        self.all_tools = get_viora_tools("ALL")
        self.tool_map = {tool.name: tool for tool in self.all_tools}

    def _get_relevant_tools(self, user_input: str) -> List[Any]:
        """Simple keyword-based tool routing for reliability."""
        user_input = user_input.lower()
        categories = ["GENERAL", "GREETING"]  # Always include basics

        if any(kw in user_input for kw in ["todo", "task", "list"]):
            categories.append("TODO")
        if any(
            kw in user_input
            for kw in [
                "notepad",
                "calc",
                "file",
                "time",
                "screen",
                "click",
                "type",
                "keyboard",
                "window",
                "vol",
                "mute",
            ]
        ):
            categories.append("WINDOWS")
        if any(
            kw in user_input
            for kw in [
                "search",
                "google",
                "browser",
                "open http",
                "url",
                "click link",
                "who is",
                "what is the",
            ]
        ):
            categories.append("BROWSER")

        # If no specific category matched, default to ALL for safety on first turn
        if len(categories) <= 2:
            return self.all_tools

        tools = []
        for cat in categories:
            tools.extend(get_viora_tools(cat))

        # Deduplicate tools
        seen = set()
        unique_tools = []
        for t in tools:
            if t.name not in seen:
                unique_tools.append(t)
                seen.add(t.name)
        return unique_tools

    def _create_llm(self, model: str = "llama3.1", tools: List[Any] = None):
        """Helper to create LLM instances based on provider and purpose."""
        if self.provider == "ollama":
            # Map logical model names to specific Ollama tags
            if "llama" in model:
                model_tag = "llama3.1:8b-instruct-q4_K_M"
            elif "gemma" in model:
                model_tag = "gemma3:1b"
            else:
                model_tag = "phi3:mini"
            llm = ChatOllama(model=model_tag, temperature=0)
        elif self.provider == "groq":
            model_map = {
                "gemma3:1b": "gemma2-9b-it",
                "llama3.1": "llama-3.3-70b-versatile",
            }
            llm = ChatGroq(model_name=model_map.get(model, model), temperature=0)
        else:
            # Fallback to Gemini if other providers fail or aren't set
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

        return llm.bind_tools(tools) if tools else llm

    def _apply_rules(self, user_input: str) -> Optional[str]:
        """Hardcoded rules layer for instant responses (Time, Apps, Vol, Todo, Search)."""
        import re

        text = user_input.lower().strip()

        # 1. Time (only for very simple queries)
        if re.fullmatch(r"(?:what is the\s+)?(?:time|clock)", text):
            return f"The current time is {self.tool_map['get_time'].invoke({})}"

        # 2. Open Apps (only if it's the ONLY thing in the command)
        match = re.fullmatch(r"open\s+([a-zA-Z0-9]+)", text)
        if match:
            app = match.group(1).strip()
            return self.tool_map["open_app"].invoke({"app_name": app})

        # 3. Volume
        if re.fullmatch(r"set\s+volume\s+to\s+(\d+)", text):
            vol = re.search(r"(\d+)", text).group(1)
            return self.tool_map["set_volume"].invoke({"volume": int(vol)})
        if text in ["mute", "mute system", "mute volume"]:
            return self.tool_map["mute_volume"].invoke({})
        if text in ["unmute", "unmute system", "unmute volume"]:
            return self.tool_map["unmute_volume"].invoke({})

        # 4. Todos
        if text in [
            "list todos",
            "show tasks",
            "what are my todos",
            "list tasks",
            "todos",
        ]:
            return f"Your tasks:\n{self.tool_map['list_todos'].invoke({})}"

        # 5. Search (only for direct "search [query]" or "google [query]" commands)
        search_match = re.fullmatch(r"(?:search for|google|duckduckgo)\s+(.+)", text)
        if search_match:
            return self.tool_map["web_search"].invoke({"query": search_match.group(1)})

        return None

    def run(self, user_input: str, max_steps: int = 10) -> str:
        # 1. Rules Layer (Instant)
        rule_result = self._apply_rules(user_input)
        if rule_result:
            return rule_result

        # 2. History Truncation (Keep last 15 messages)
        if len(self.history) > 15:
            # Keep the System Message (index 0) and the last 14 messages
            self.history = [self.history[0]] + self.history[-14:]

        self.history.append(HumanMessage(content=user_input))

        # 3. Router Step (Fast Model)
        # We use a more descriptive prompt to prevent hallucinations with small models
        router_prompt = f"""Task: Intent Classification
Input: "{user_input}"
Rules:
- Respond with 'TOOL' if the user wants an ACTION (open, click, screenshot, search, files, etc.).
- Respond with 'TOOL' if the input involves CURRENT EVENTS, PEOPLE, DATES, or FACTUAL QUESTIONS that might need verification.
- Respond with 'CHAT' if it's general conversation, greeting, or subjective opinion.
Response:"""
        try:
            route: AIMessage = self.router_llm.invoke(
                [SystemMessage(content=router_prompt)]
            )
            intent = route.content.strip().upper()
        except:
            intent = "TOOL"

        # 4. Reasoning Step
        if "CHAT" in intent:
            response: AIMessage = self.router_llm.invoke(self.history)
            # Prevent weird hallucinations from small model
            if "terminate" in response.content.lower() and len(response.content) < 15:
                # Fallback to a polite response if it just says "terminate"
                return "I'm here! How can I help you?"
            self.history.append(response)
            return response.content

        # TOOL Intent -> Use Reasoning LLM with selective tools
        current_tools = self._get_relevant_tools(user_input)
        # Re-bind tools dynamically to the reasoning model
        reasoning_with_tools = self._create_llm(model="llama3.1", tools=current_tools)

        for step in range(max_steps):
            response: AIMessage = reasoning_with_tools.invoke(self.history)
            self.history.append(response)
            self._track_tokens(response)

            # If no tool calls → done
            if not response.tool_calls:
                return response.content

            # Execute tool calls
            for call in response.tool_calls:
                tool_name = call["name"]
                tool_args = call["args"]
                tool_id = call["id"]

                print(f"Using {tool_name}...")

                result = self._execute_tool(tool_name, tool_args)

                self.history.append(
                    ToolMessage(content=str(result), tool_call_id=tool_id)
                )

                if result == "TERMINATE_SESSION":
                    self.should_exit = True
                    return "DONE"

        return "Stopped: too many steps."

    def _execute_tool(self, name: str, args: Dict[str, Any]):
        if name not in self.tool_map:
            return f"Tool {name} not found."
        try:
            # Check for console printing if we want to keep it here,
            # but usually it's better to let the caller handle UI.
            # However, brain.py currently prints to stdout.
            # We'll keep it simple for now.
            return self.tool_map[name].invoke(args)
        except Exception as e:
            return f"Tool error: {str(e)}"

    def _track_tokens(self, response):
        if hasattr(response, "response_metadata"):
            usage = response.response_metadata.get("token_usage", {})
            p = usage.get("prompt_tokens", 0)
            c = usage.get("completion_tokens", 0)
            t = usage.get("total_tokens", 0)

            self.session_tokens["prompt"] += p
            self.session_tokens["completion"] += c
            self.session_tokens["total"] += t
            self.last_response_tokens = usage

    def get_token_usage(self):
        return {
            "session": self.session_tokens,
            "last": self.last_response_tokens,
            "provider": self.provider,
        }
