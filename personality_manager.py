import json
import os
import glob

class PersonalityManager:
    def __init__(self, personalities_dir='personalities'):
        self.personalities_dir = personalities_dir
        self.current_personality = None
        self.current_personality_name = None

    def load_personality(self, name):
        """Loads a personality by name (filename without extension)."""
        path = os.path.join(self.personalities_dir, f"{name}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Personality '{name}' not found.")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.current_personality = data
        self.current_personality_name = name
        return data

    def get_current_config(self):
        return self.current_personality

    def list_personalities(self):
        """Returns a list of available personality names."""
        files = glob.glob(os.path.join(self.personalities_dir, "*.json"))
        return [os.path.splitext(os.path.basename(f))[0] for f in files]
