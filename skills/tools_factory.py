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

class BrowserOpenInput(BaseModel):
    url: str = Field(description="The URL to navigate to")

class BrowserClickInput(BaseModel):
    selector: str = Field(description="The CSS element selector to click")

class BrowserGetTextInput(BaseModel):
    selector: str = Field(description="The CSS element selector to get text from")

class GoogleNavInput(BaseModel):
    query: str = Field(description="The search query text")

class SingleStringInput(BaseModel):
    text: str = Field(description="The text input")

class OpenAppInput(BaseModel):
    app_name: str = Field(description="The app name")

class ReadFileInput(BaseModel):
    path: str = Field(description="The file path")

class WriteFileInput(BaseModel):
    path: str = Field(description="The file path")
    content: str = Field(description="The content to write")

class VolumeInput(BaseModel):
    level: int = Field(description="Volume level 0-100")

class ScreenshotInput(BaseModel):
    path: str = Field(default="", description="Optional path to save screenshot")

class WindowFocusInput(BaseModel):
    title: str = Field(description="The window title to focus")

def get_viora_tools(category: str = "ALL"):
    org = TodoSkills()
    win = WindowsSkills()
    browser = SeleniumSkills()
    gen = GeneralSkills()

    # Define tool groups
    todo_tools = [
        StructuredTool.from_function(name="add_todo", func=org.add_todo, description="Add a new task to your todo list.", args_schema=SingleStringInput),
        StructuredTool.from_function(name="list_todos", func=org.list_todos, description="List all pending tasks.")
    ]

    windows_tools = [
        StructuredTool.from_function(name="open_app", func=win.open_application, description="Open a Windows app (notepad, calc, etc).", args_schema=OpenAppInput),
        StructuredTool.from_function(name="get_time", func=win.get_time, description="Get the current system time."),
        StructuredTool.from_function(name="set_volume", func=win.set_volume, description="Set system volume level (0-100).", args_schema=VolumeInput),
        StructuredTool.from_function(name="mute_volume", func=win.mute_volume, description="Mute the system volume."),
        StructuredTool.from_function(name="unmute_volume", func=win.unmute_volume, description="Unmute the system volume."),
        StructuredTool.from_function(name="read_file", func=win.read_file, description="Read content from a local file path.", args_schema=ReadFileInput),
        StructuredTool.from_function(name="write_file", func=win.write_file, description="Write content to a local file path.", args_schema=WriteFileInput),
        StructuredTool.from_function(name="list_files", func=win.list_files, description="List files in a directory.", args_schema=ReadFileInput),
        StructuredTool.from_function(name="take_screenshot", func=win.take_screenshot, description="Capture a screenshot.", args_schema=ScreenshotInput),
        StructuredTool.from_function(name="clipboard_set", func=win.clipboard_set, description="Set text to the clipboard.", args_schema=SingleStringInput),
        StructuredTool.from_function(name="clipboard_get", func=win.clipboard_get, description="Get text from the clipboard."),
        StructuredTool.from_function(name="window_list", func=win.window_list, description="List all open window titles."),
        StructuredTool.from_function(name="window_focus", func=win.window_focus, description="Focus a window by its title.", args_schema=WindowFocusInput),
        StructuredTool.from_function(name="mouse_click", func=win.mouse_click, description="Click the mouse at specific x,y coordinates."),
        StructuredTool.from_function(name="keyboard_type", func=win.keyboard_type, description="Type a string of text via keyboard simulation.", args_schema=SingleStringInput),
        StructuredTool.from_function(name="keyboard_press", func=win.keyboard_press, description="Press a single keyboard key.", args_schema=SingleStringInput)
    ]

    browser_tools = [
        StructuredTool.from_function(name="web_search", func=browser.web_search, description="Search the web for up-to-date facts and info.", args_schema=WebSearchInput),
        StructuredTool.from_function(name="google_nav", func=browser.google_search_nav, description="Search Google and open the results in a browser tab.", args_schema=GoogleNavInput),
        StructuredTool.from_function(name="browser_open", func=browser.browser_open, description="Navigate to a URL.", args_schema=BrowserOpenInput),
        StructuredTool.from_function(name="browser_click", func=browser.browser_click, description="Click an element on the webpage. Use browser_map_elements first to find the selector.", args_schema=BrowserClickInput),
        StructuredTool.from_function(name="browser_type", func=browser.browser_type, description="Type text into a webpage element. Use browser_map_elements first to find the selector.", args_schema=BrowserTypeInput),
        StructuredTool.from_function(name="browser_get_text", func=browser.browser_get_text, description="Get text content of a specific element.", args_schema=BrowserGetTextInput),
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
