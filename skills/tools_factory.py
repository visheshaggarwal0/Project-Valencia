from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from skills.todo_skills import TodoSkills
from skills.windows_skills import WindowsSkills
from skills.selenium_skills import SeleniumSkills
from skills.general_skills import GeneralSkills

class WebSearchInput(BaseModel):
    query: str = Field(description="The exact search query text")

class BrowserTypeInput(BaseModel):
    selector: str = Field(description="The CSS element selector")
    text: str = Field(description="The text to type")

def get_viora_tools(category: str = "ALL"):
    org = TodoSkills()
    win = WindowsSkills()
    browser = SeleniumSkills()
    gen = GeneralSkills()

    # Define tool groups
    todo_tools = [
        StructuredTool.from_function(name="add_todo", func=org.add_todo, description="Add a new task to your todo list."),
        StructuredTool.from_function(name="list_todos", func=org.list_todos, description="List all pending tasks.")
    ]

    windows_tools = [
        StructuredTool.from_function(name="open_app", func=win.open_application, description="Open a Windows app (notepad, calc, etc)."),
        StructuredTool.from_function(name="get_time", func=win.get_time, description="Get the current system time."),
        StructuredTool.from_function(name="set_volume", func=win.set_volume, description="Set system volume level (0-100)."),
        StructuredTool.from_function(name="mute_volume", func=win.mute_volume, description="Mute the system volume."),
        StructuredTool.from_function(name="unmute_volume", func=win.unmute_volume, description="Unmute the system volume."),
        StructuredTool.from_function(name="read_file", func=win.read_file, description="Read content from a local file path."),
        StructuredTool.from_function(name="write_file", func=win.write_file, description="Write content to a local file path."),
        StructuredTool.from_function(name="list_files", func=win.list_files, description="List files in a directory."),
        StructuredTool.from_function(name="take_screenshot", func=win.take_screenshot, description="Capture a screenshot."),
        StructuredTool.from_function(name="clipboard_set", func=win.clipboard_set, description="Set text to the clipboard."),
        StructuredTool.from_function(name="clipboard_get", func=win.clipboard_get, description="Get text from the clipboard."),
        StructuredTool.from_function(name="window_list", func=win.window_list, description="List all open window titles."),
        StructuredTool.from_function(name="window_focus", func=win.window_focus, description="Focus a window by its title."),
        StructuredTool.from_function(name="mouse_click", func=win.mouse_click, description="Click the mouse at specific x,y coordinates."),
        StructuredTool.from_function(name="keyboard_type", func=win.keyboard_type, description="Type a string of text via keyboard simulation."),
        StructuredTool.from_function(name="keyboard_press", func=win.keyboard_press, description="Press a single keyboard key.")
    ]

    browser_tools = [
        StructuredTool.from_function(name="web_search", func=browser.web_search, description="Search the web for up-to-date facts and info.", args_schema=WebSearchInput),
        StructuredTool.from_function(name="google_nav", func=browser.google_search_nav, description="Search Google and open the results in a browser tab."),
        StructuredTool.from_function(name="browser_open", func=browser.browser_open, description="Navigate to a URL."),
        StructuredTool.from_function(name="browser_click", func=browser.browser_click, description="Click an element on the webpage. Use browser_map_elements first to find the selector."),
        StructuredTool.from_function(name="browser_type", func=browser.browser_type, description="Type text into a webpage element. Use browser_map_elements first to find the selector.", args_schema=BrowserTypeInput),
        StructuredTool.from_function(name="browser_get_text", func=browser.browser_get_text, description="Get text content of a specific element."),
        StructuredTool.from_function(name="browser_get_all_text", func=browser.browser_get_all_text, description="Get the text of the entire webpage."),
        StructuredTool.from_function(name="browser_map_elements", func=browser.browser_map_elements, description="Maps page elements and visually assigns them a [viora-id=*] attribute allowing you to extract targetable CSS IDs for clicking/typing on heavily scrambled webpages. Always use this if normal selectors fail.")
    ]

    general_tools = [
        StructuredTool.from_function(name="terminate", func=gen.terminate, description="End the session when the user says goodbye.")
    ]

    # Map categories to tool groups
    mapping = {
        "GREETING": [],
        "TODO": todo_tools,
        "WINDOWS": windows_tools,
        "BROWSER": browser_tools,
        "GENERAL": general_tools,
        "ALL": general_tools + todo_tools + windows_tools + browser_tools
    }

    return mapping.get(category, mapping["ALL"])
