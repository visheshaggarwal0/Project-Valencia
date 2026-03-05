import json
import os
from datetime import datetime

class TodoSkills:
    """
    Consolidated Todo management skills.
    """
    def __init__(self, storage_file: str = "data/organizer.json"):
        self.storage_file = storage_file
        self.data = self._load_data()

    def _load_data(self):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        return {"todos": [], "journal": []}

    def save_data(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_todo(self, task: str):
        """Add a new task to the todo list."""
        self.data["todos"].append({"task": task, "completed": False, "created_at": datetime.now().isoformat()})
        self.save_data()
        return f"Added: {task}"

    def list_todos(self):
        """List all pending tasks."""
        incomplete = [t for t in self.data["todos"] if not t["completed"]]
        return "\n".join([f"- {t['task']}" for t in incomplete]) if incomplete else "No pending tasks."

    def todo_ops(self, action, task=None):
        """Deprecated: Use add_todo or list_todos directly."""
        action = action.lower().strip()
        if action == "add": return self.add_todo(task)
        if action == "list": return self.list_todos()
        return "Invalid action."
