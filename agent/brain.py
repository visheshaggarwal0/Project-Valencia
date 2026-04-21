import os
import re
import json
from typing import List, Dict, Any, Optional, TypedDict, Annotated, Sequence
import operator
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
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from langgraph.graph import StateGraph, END

from skills.tools_factory import get_viora_tools

load_dotenv()
viora_console = Console()

class VioraState(TypedDict):
    messages: Annotated[list, operator.add]
    user_input: str
    context: str
    intent: str
    plan: str
    status: Any
    memory: Any
    final_response: str
    steps_taken: int

class Brain:
    def __init__(self):
        self.router_provider = os.getenv("VIORA_ROUTER_PROVIDER", "ollama").lower()
        self.reasoning_provider = os.getenv("VIORA_REASONING_PROVIDER", "groq").lower()
        
        self.all_tools = get_viora_tools("ALL")
        self.tool_map = {tool.name: tool for tool in self.all_tools}
        self.should_exit = False
        
        self.router_llm = self._create_llm(model="gemma3:1b", tools=[], provider=self.router_provider)
        self.reasoning_llm = self._create_llm(model="llama3.1", tools=self.all_tools, provider=self.reasoning_provider)

        self.history = [
            SystemMessage(
                content="""
You are Viora, a helpful and friendly AI assistant.

CORE BEHAVIOR:
1. CHAT FIRST: Prioritize chatting and being helpful.
2. TOOL CONFIRMATION: You may use read-only or harmless tools immediately WITHOUT asking for permission. ONLY ask for confirmation before executing destructive, intrusive, or sensitive actions.
3. GREETINGS: Respond warmly to greetings naturally.
4. TERMINATION: Complete the session when the user says "bye", "exit", or wants to quit.
5. CURRENT FACTS: Whenever a query involves current events, specific people, dates, or information you are uncertain about, ALWAYS run a web search for the most up-to-date information before responding.
6. SUMMARIZATION: After searching, provide a concise summary.
7. SCREENSHOTS: Use your screen capture capability when asked.

Be concise. Think step by step.
"""
            )
        ]

        self.session_tokens = {"prompt": 0, "completion": 0, "total": 0}
        self.last_response_tokens = None
        
        self.graph = self._build_graph()

    # --- LLM Utils ---
    def _create_llm(self, model: str = "llama3.1", tools: List[Any] = None, provider: str = None):
        used_provider = provider if provider else self.reasoning_provider
        if used_provider == "ollama":
            if "llama" in model:
                model_tag = "llama3.1:8b-instruct-q4_K_M"
            elif "gemma" in model:
                model_tag = "gemma3:1b"
            else:
                model_tag = "phi3:mini"
            llm = ChatOllama(model=model_tag, temperature=0)
        elif used_provider == "groq":
            model_map = {
                "gemma3:1b": "gemma2-9b-it",
                "llama3.1": "llama-3.3-70b-versatile",
            }
            llm = ChatGroq(model_name=model_map.get(model, model), temperature=0)
        else:
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        return llm.bind_tools(tools) if tools else llm

    def _track_tokens(self, response):
        if hasattr(response, "response_metadata"):
            usage = response.response_metadata.get("token_usage", {})
            if usage:
                self.session_tokens["prompt"] += usage.get("prompt_tokens", 0)
                self.session_tokens["completion"] += usage.get("completion_tokens", 0)
                self.session_tokens["total"] += usage.get("total_tokens", 0)
                self.last_response_tokens = usage

    def get_token_usage(self):
        return {
            "session": self.session_tokens,
            "last": self.last_response_tokens,
            "provider": f"Router:{self.router_provider} | Reasoner:{self.reasoning_provider}",
        }

    # --- Tools Routing Utils ---
    def _get_relevant_tools(self, user_input: str) -> List[Any]:
        user_input = user_input.lower()
        categories = ["GENERAL", "GREETING"]
        if any(kw in user_input for kw in ["todo", "task", "list"]): categories.append("TODO")
        if any(kw in user_input for kw in ["notepad", "calc", "file", "time", "screen", "click", "type", "keyboard", "window", "vol", "mute"]): categories.append("WINDOWS")
        if any(kw in user_input for kw in ["search", "google", "browser", "open http", "url", "click link", "who is", "what is"]): categories.append("BROWSER")
        if len(categories) <= 2: return self.all_tools
        tools = []
        for cat in categories: tools.extend(get_viora_tools(cat))
        seen = set()
        unique = []
        for t in tools:
            if t.name not in seen:
                unique.append(t)
                seen.add(t.name)
        return unique

    # --- LANGGRAPH NODES ---
    
    def node_rules(self, state: VioraState):
        if state["status"]: state["status"].update("Viora is evaluating rules...")
        text = state["user_input"].lower().strip()
        
        if text in ["hi", "hello", "hey", "greetings", "good morning", "good evening", "good afternoon", "yo", "what's up", "sup", "sup?"]:
            resp = "Hello! How can I help you today?"
            return {"messages": [AIMessage(content=resp)], "final_response": resp, "intent": "RULES"}

        if re.fullmatch(r"(?:what is the\s+)?(?:time|clock)", text):
            resp = f"The current time is {self.tool_map['get_time'].invoke({})}"
            return {"messages": [AIMessage(content=resp)], "final_response": resp, "intent": "RULES"}
            
        match = re.fullmatch(r"open\s+([a-zA-Z0-9]+)", text)
        if match:
            resp = self.tool_map["open_app"].invoke({"app_name": match.group(1).strip()})
            return {"messages": [AIMessage(content=resp)], "final_response": resp, "intent": "RULES"}
            
        if re.fullmatch(r"set\s+volume\s+to\s+(\d+)", text):
            vol = re.search(r"(\d+)", text).group(1)
            resp = self.tool_map["set_volume"].invoke({"volume": int(vol)})
            return {"messages": [AIMessage(content=resp)], "final_response": resp, "intent": "RULES"}
            
        if text in ["mute", "mute system", "mute volume"]: 
            resp = self.tool_map["mute_volume"].invoke({})
            return {"messages": [AIMessage(content=resp)], "final_response": resp, "intent": "RULES"}
        if text in ["unmute", "unmute system", "unmute volume"]: 
            resp = self.tool_map["unmute_volume"].invoke({})
            return {"messages": [AIMessage(content=resp)], "final_response": resp, "intent": "RULES"}
        
        if text in ["list todos", "show tasks", "what are my todos", "list tasks", "todos"]:
            resp = f"Your tasks:\n{self.tool_map['list_todos'].invoke({})}"
            return {"messages": [AIMessage(content=resp)], "final_response": resp, "intent": "RULES"}
            
        search_match = re.fullmatch(r"(?:search for|google|duckduckgo)\s+(.+)", text)
        if search_match:
            resp = self.tool_map["web_search"].invoke({"query": search_match.group(1)})
            return {"messages": [AIMessage(content=resp)], "final_response": resp, "intent": "RULES"}
            
        return {"intent": "UNKNOWN"}

    def node_router(self, state: VioraState):
        if state["status"]: state["status"].update("Viora is classifying intent...")
        prompt = f"""Task: Intent Classification\nInput: "{state['user_input']}"\nRules:\n- Respond with 'TOOL' if the user wants an ACTION (open, click, screenshot, search, files, etc.) or if the input involves CURRENT EVENTS, PEOPLE, DATES, or FACTUAL QUESTIONS.\n- Respond with 'CHAT' if it's general conversation or subjective opinion.\nResponse:"""
        try:
            route = self.router_llm.invoke([SystemMessage(content=prompt)])
            intent = route.content.strip().upper()
        except:
            intent = "TOOL"
        return {"intent": intent}

    def node_cache(self, state: VioraState):
        """Checks Routine DB for exact semantic matches >0.95"""
        if state["status"]: state["status"].update("Checking semantic routine cache...")
        if state.get("memory"):
            cached_tools = state["memory"].check_routine_cache(state["user_input"])
            if cached_tools:
                viora_console.print("⚡ [dim green]Semantic Cache Hit! Bypassing reasoning LLM...[/dim green]")
                return {"messages": [AIMessage(content="", tool_calls=cached_tools)], "intent": "CACHED"}
        return {"intent": "TOOL"}

    def node_chat(self, state: VioraState):
        if state["status"]: state["status"].update("Viora is responding...")
        
        current_context = list(state["messages"])
        if state["context"]:
            current_context.insert(-1, SystemMessage(content=state["context"]))
            
        response = self.router_llm.invoke(current_context)
        self._track_tokens(response)
        
        if "terminate" in response.content.lower() and len(response.content) < 15:
            return {"messages": [AIMessage(content="I'm here! How can I help you?")], "final_response": "I'm here! How can I help you?"}
            
        return {"messages": [response], "final_response": response.content}

    def node_planner(self, state: VioraState):
        if state["status"]: state["status"].update("Viora is planning strategy...")
        planner_llm = self._create_llm(model="llama3.1", tools=None, provider=self.reasoning_provider)
        prompt = SystemMessage(content="You are the Planner.\nGiven the conversation history and user request, create a step-by-step plan of action.\nFocus on tools and order. Respond ONLY with the Plan, starting with 'Plan:'. Do NOT call tools yourself.")
        
        current_context = list(state["messages"])
        if state["context"]:
            current_context.insert(-1, SystemMessage(content=state["context"]))
            
        try:
            plan_resp = planner_llm.invoke(current_context + [prompt])
            self._track_tokens(plan_resp)
            plan_msg = SystemMessage(content=f"Initial Plan generated by Reasoning Engine:\n{plan_resp.content}\n\nExecute this plan to fulfill the request.")
            
            panel = Panel(Markdown(plan_resp.content), title="🧠 [bold magenta]Viora Strategy[/bold magenta]", border_style="magenta", padding=(1, 2))
            if state["status"]: state["status"].update(panel)
            else: viora_console.print(panel)
            
            return {"messages": [plan_msg], "plan": plan_resp.content}
        except Exception as e:
            return {"plan": f"Error planning: {e}"}

    def node_reasoner(self, state: VioraState):
        current_tools = self._get_relevant_tools(state["user_input"])
        reasoner = self._create_llm(model="llama3.1", tools=current_tools, provider=self.reasoning_provider)
        
        current_context = list(state["messages"])
        if state["context"]:
            current_context.insert(-1, SystemMessage(content=state["context"]))
            
        try:
            response = reasoner.invoke(current_context)
            self._track_tokens(response)
        except Exception as e:
            err_str = str(e)
            match = re.search(r"<function=([a-zA-Z0-9_]+)>?(\{.*?\})?</function>", err_str)
            if match:
                tool_name = match.group(1)
                try: tool_args = json.loads(match.group(2) or "{}")
                except: tool_args = {}
                tool_id = f"call_manual_{tool_name}"
                response = AIMessage(content="", tool_calls=[{"name": tool_name, "args": tool_args, "id": tool_id}])
            else:
                return {"final_response": f"Reasoning error: {err_str}"}

        if response.tool_calls:
            return {"messages": [response]}
        else:
            return {"messages": [response], "final_response": response.content}

    def node_tools(self, state: VioraState):
        last_message = state["messages"][-1]
        
        # Determine if we should save this payload to the routine cache (if it's not already from the cache)
        # Note: If it came from cache, the intent in State is CACHED. If it generated fresh, intent is TOOL.
        tool_calls = getattr(last_message, "tool_calls", [])
        if state.get("memory") and tool_calls and state.get("intent") != "CACHED":
            state["memory"].save_routine_cache(state["user_input"], tool_calls)
        
        tool_results = []
        for call in tool_calls:
            tool_name = call["name"]
            tool_args = call["args"]
            tool_id = call["id"]
            
            msg = f"🔧 [italic yellow]Using tool:[/italic yellow] [bold cyan]{tool_name}[/bold cyan]"
            if state["status"]: state["status"].update(msg)
            else: viora_console.print(msg)
                
            if tool_name not in self.tool_map:
                result = f"Tool {tool_name} not found."
            else:
                try: 
                    result = self.tool_map[tool_name].invoke(tool_args)
                    if result == "TERMINATE_SESSION":
                        self.should_exit = True
                        result = "DONE"
                except Exception as e: 
                    result = f"Tool error: {str(e)}"
            
            tool_results.append(ToolMessage(content=str(result), tool_call_id=tool_id))
            
        steps = state.get("steps_taken", 0) + 1
        
        if state.get("intent") == "CACHED":
            return {"messages": tool_results, "steps_taken": steps, "final_response": "⚡ Executed perfectly from your Semantic Cache!"}
            
        return {"messages": tool_results, "steps_taken": steps}

    # --- GRAPH ARCHITECTURE ---
    def _route_after_rules(self, state: VioraState) -> str:
        if state["intent"] == "RULES": return "end"
        return "node_router"

    def _route_after_intent(self, state: VioraState) -> str:
        if "CHAT" in state["intent"]: return "node_chat"
        return "node_cache" # Insert cache check before planning

    def _route_after_cache(self, state: VioraState) -> str:
        if state["intent"] == "CACHED": return "node_tools" # Direct pass to python callbacks
        return "node_planner"

    def _route_after_reasoner(self, state: VioraState) -> str:
        if state.get("final_response"): return "end"
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            if state.get("steps_taken", 0) > 10:
                return "end" # Hard limit
            return "node_tools"
        return "end"

    def _route_after_tools(self, state: VioraState) -> str:
        if state.get("intent") == "CACHED": return "end"
        return "node_reasoner"

    def _build_graph(self):
        builder = StateGraph(VioraState)
        
        # Nodes
        builder.add_node("node_rules", self.node_rules)
        builder.add_node("node_router", self.node_router)
        builder.add_node("node_cache", self.node_cache)
        builder.add_node("node_chat", self.node_chat)
        builder.add_node("node_planner", self.node_planner)
        builder.add_node("node_reasoner", self.node_reasoner)
        builder.add_node("node_tools", self.node_tools)
        
        # Edges
        builder.set_entry_point("node_rules")
        builder.add_conditional_edges("node_rules", self._route_after_rules, {"end": END, "node_router": "node_router"})
        builder.add_conditional_edges("node_router", self._route_after_intent, {"node_chat": "node_chat", "node_cache": "node_cache"})
        
        builder.add_conditional_edges("node_cache", self._route_after_cache, {"node_tools": "node_tools", "node_planner": "node_planner"})
        
        builder.add_edge("node_chat", END)
        builder.add_edge("node_planner", "node_reasoner")
        
        builder.add_conditional_edges("node_reasoner", self._route_after_reasoner, {"node_tools": "node_tools", "end": END})
        builder.add_conditional_edges("node_tools", self._route_after_tools, {"node_reasoner": "node_reasoner", "end": END})
        
        return builder.compile()

    def run(self, user_input: str, max_steps: int = 15, status=None, context: str = "", memory=None) -> str:
        self.last_response_tokens = None # Reset stale tokens from prior execution
        
        if len(self.history) > 15:
            self.history = [self.history[0]] + self.history[-14:]
            
        initial_state = {
            "messages": self.history + [HumanMessage(content=user_input)],
            "user_input": user_input,
            "context": context,
            "intent": "",
            "plan": "",
            "status": status,
            "memory": memory,
            "final_response": "",
            "steps_taken": 0
        }
        
        try:
            final_state = self.graph.invoke(initial_state)
            self.history = final_state["messages"]
            
            if final_state.get("final_response"):
                return final_state["final_response"]
            elif self.should_exit:
                return "Goodbye!"
            else:
                return "DONE"
        except Exception as e:
            return f"LangGraph Execution Error: {e}"
