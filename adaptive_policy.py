"""
Adaptive Compression Policy – Task-aware compression levels.
Allows setting different compression aggressiveness per content type and task type.
"""
import json
import os

class AdaptivePolicy:
    POLICY_FILE = os.path.expanduser("~/.headroom_adaptive_policy.json")
    
    # Default policies: key -> compression_level (0.0 = none, 1.0 = maximum)
    DEFAULT_POLICIES = {
        "json": {"level": 0.8},
        "code": {"level": 0.3},
        "text": {"level": 0.5},
        "logs": {"level": 0.7},
        "json_debug": {"level": 0.1},
        "code_debug": {"level": 0.1},
        "json_search": {"level": 0.9},
        "code_search": {"level": 0.6},
        "default": {"level": 0.4}
    }
    
    def __init__(self):
        self.policies = self._load()
    
    def _load(self):
        if os.path.exists(self.POLICY_FILE):
            with open(self.POLICY_FILE, 'r') as f:
                return json.load(f)
        return self.DEFAULT_POLICIES.copy()
    
    def get_level(self, content_type, task_type="default"):
        """Return compression level for given content type and task"""
        # Try specific key first: content_type_task_type
        specific_key = f"{content_type}_{task_type}"
        if specific_key in self.policies:
            return self.policies[specific_key]["level"]
        # Fall back to content_type only
        if content_type in self.policies:
            return self.policies[content_type]["level"]
        # Ultimate fallback
        return self.policies["default"]["level"]
    
    def set_level(self, key, level):
        """Set compression level for a specific key"""
        if key not in self.policies:
            self.policies[key] = {}
        self.policies[key]["level"] = float(level)
        self._save()
        return True
    
    def _save(self):
        os.makedirs(os.path.dirname(self.POLICY_FILE) or ".", exist_ok=True)
        with open(self.POLICY_FILE, 'w') as f:
            json.dump(self.policies, f, indent=2)
    
    def show(self):
        """Display all current policies"""
        print("Current Adaptive Policies:")
        for key, config in self.policies.items():
            print(f"  {key}: level = {config.get('level', 0.4)}")
    
    @classmethod
    def get_global(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance
