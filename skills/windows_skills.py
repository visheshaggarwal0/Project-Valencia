import platform
import datetime
import os
import subprocess
import difflib
import psutil
import pyperclip
import pyautogui
import pywinauto
from pywinauto import Application, Desktop
import pygetwindow
from PIL import ImageGrab
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import ctypes
import math
import time
from typing import Optional, List, Dict, Tuple

class WindowsSkills:
    "Consolidated Windows skills: System operations and Desktop automation."
    
    # Common Windows App Aliases
    APP_ALIASES = {
        "edge": "msedge",
        "chrome": "chrome",
        "firefox": "firefox",
        "notepad": "notepad",
        "calculator": "calc",
        "calc": "calc",
        "cmd": "cmd",
        "terminal": "wt",
        "explorer": "explorer",
        "settings": "start ms-settings:",
        "solitaire": "solitaire & casual games",
        "store": "explorer.exe shell:AppsFolder\\Microsoft.WindowsStore_8wekyb3d8bbwe!App",
        "photos": "explorer.exe shell:AppsFolder\\Microsoft.Windows.Photos_8wekyb3d8bbwe!App",
        "spotify": "spotify",
        "code": "code",
        "vscode": "code",
        "no": "notepad",
        "note": "notepad",
        "outlook": "outlook",
        "mail": "outlook",
        "word": "winword",
        "excel": "excel",
        "powerpoint": "powerpnt",
        "ppt": "powerpnt"
    }

    def __init__(self):
        # Set PyAutoGUI safety features
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5

    # --- System Operations ---

    def open_application(self, app_name: str):
        """Opens a Windows application (outlook, chrome, notepad, etc)."""
        app_name_lower = app_name.lower().strip()
        command = self.APP_ALIASES.get(app_name_lower)
        
        if not command:
            matches = difflib.get_close_matches(app_name_lower, self.APP_ALIASES.keys(), n=1, cutoff=0.7)
            if matches:
                suggestion = matches[0]
                command = self.APP_ALIASES[suggestion]
        
        if not command:
            command = app_name

        try:
            if command.startswith("start "):
                 os.system(command)
            else:
                os.startfile(command)
            return f"Successfully attempted to open '{app_name}'."
        except Exception as e:
            return f"Failed to open '{app_name}': {str(e)}"

    def get_time(self):
        """Get the current system time."""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_system_info(self):
        """Get OS and platform info."""
        return f"{platform.system()} {platform.release()}"

    def get_system_status(self):
        """Get CPU, Memory and Battery status."""
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        bat = psutil.sensors_battery()
        res = f"CPU: {cpu}%, Mem: {mem}%"
        if bat: res += f", Bat: {bat.percent}% ({'Plugged' if bat.power_plugged else 'Discharging'})"
        return res

    def read_file(self, path: str):
        """Read content from a file."""
        with open(path, 'r', encoding='utf-8') as f: return f.read()

    def write_file(self, path: str, content: str):
        """Write content to a file."""
        with open(path, 'w', encoding='utf-8') as f: f.write(content); return f"Wrote to {path}"

    def list_files(self, path: str = "."):
        """List files in a directory."""
        return "\n".join(os.listdir(path))

    def take_screenshot(self, path: str = ""):
        """Capture a full-screen screenshot."""
        screenshots_dir = "screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)
        
        if not path:
            path = os.path.join(screenshots_dir, f"screenshot_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png")
        elif not os.path.dirname(path):
            # If only a filename was provided, put it in the screenshots folder
            path = os.path.join(screenshots_dir, path)
        else:
            # if a full path was provided, ensure the parent directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
        pyautogui.screenshot(path)
        return f"Screenshot saved to {path}"

    def system_ops(self, action: str, value = None):
        """Deprecated: Use specific system methods."""
        action = action.lower().strip()
        if action == 'time': return self.get_time()
        if action == 'info': return self.get_system_info()
        if action == 'status': return self.get_system_status()
        if action == 'vol': return self.set_volume(int(value))
        if action == 'mute': return self.mute_volume()
        if action == 'unmute': return self.unmute_volume()
        if action == 'media': return self.media_control(value)
        return "Invalid action."

    def file_ops(self, action: str, path: str = ".", content: str = None):
        """Deprecated: Use read_file, write_file, or list_files."""
        action = action.lower().strip()
        if action == 'read': return self.read_file(path)
        if action == 'write': return self.write_file(path, content)
        if action == 'list': return self.list_files(path)
        return "Invalid file action."

    def clipboard_get(self):
        """Get the current text from the clipboard."""
        return pyperclip.paste()

    def clipboard_set(self, text: str):
        """Set the clipboard to a specific string."""
        pyperclip.copy(text)
        return "Clipboard set."

    def clipboard_ops(self, action: str, text: str = None):
        """Deprecated: Use clipboard_get or clipboard_set."""
        action = action.lower().strip()
        if action == 'get': return self.clipboard_get()
        if action == 'set': return self.clipboard_set(text)
        return "Invalid action."

    # --- Volume & Media Helpers ---

    def _get_volume_interface(self):
        devices = AudioUtilities.GetSpeakers()
        return devices.EndpointVolume

    def set_volume(self, level: int):
        try:
            volume = self._get_volume_interface()
            scalar = max(0.0, min(1.0, level / 100.0))
            volume.SetMasterVolumeLevelScalar(scalar, None)
            return f"Volume set to {level}%."
        except Exception as e: return str(e)

    def mute_volume(self):
        try:
            volume = self._get_volume_interface()
            volume.SetMute(1, None)
            return "Muted."
        except Exception as e: return str(e)

    def unmute_volume(self):
        try:
            volume = self._get_volume_interface()
            volume.SetMute(0, None)
            return "Unmuted."
        except Exception as e: return str(e)

    def media_control(self, action: str):
        VK_MAP = {"play_pause": 0xB3, "next": 0xB0, "prev": 0xB1, "stop": 0xB2, "vol_up": 0xAF, "vol_down": 0xAE, "mute": 0xAD}
        vk_code = VK_MAP.get(action.lower())
        if not vk_code: return "Invalid media action."
        try:
            ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
            ctypes.windll.user32.keybd_event(vk_code, 0, 0x0002, 0)
            return f"Sent media {action}."
        except Exception as e: return str(e)

    # --- Desktop Automation ---

    def window_list(self):
        """List all visible window titles."""
        return "\n".join([w.title for w in pygetwindow.getAllWindows() if w.title])

    def window_focus(self, title: str):
        """Bring a specific window to the front."""
        try:
            wins = pygetwindow.getWindowsWithTitle(title)
            if wins:
                wins[0].activate()
                return f"Focused {title}"
            return f"Window not found: {title}"
        except Exception as e: return f"Focus error: {str(e)}"

    def mouse_click(self, x: int = None, y: int = None, button: str = 'left'):
        """Click the mouse."""
        pyautogui.click(x=x, y=y, button=button)
        return "Clicked."

    def keyboard_type(self, text: str):
        """Type text."""
        pyautogui.write(text, interval=0.01)
        return f"Typed text."

    def keyboard_press(self, key: str):
        """Press a key."""
        pyautogui.press(key)
        return f"Pressed {key}"

    def window_ops(self, action: str, title: str = None, **kwargs):
        """Deprecated: Use window_list or window_focus."""
        action = action.lower().strip()
        if action == 'list': return self.window_list()
        if action == 'focus' and title: return self.window_focus(title)
        return "Invalid action."

    def mouse_ops(self, action: str, **kwargs):
        """Deprecated: Use mouse_click."""
        if action == 'click': return self.mouse_click(kwargs.get('x'), kwargs.get('y'))
        return "Invalid action."

    def keyboard_ops(self, action: str, **kwargs):
        """Deprecated: Use keyboard_type or keyboard_press."""
        if action == 'type': return self.keyboard_type(kwargs.get('text', ''))
        if action == 'press': return self.keyboard_press(kwargs.get('key', ''))
        return "Invalid action."

    def screen_ops(self, action: str, **kwargs):
        """Deprecated: Use take_screenshot."""
        if action == 'cap': return self.take_screenshot()
        return "Invalid action."
