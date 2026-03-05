import os
import yaml
from dotenv import load_dotenv

load_dotenv()

class ConfigLoader:
    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._load_all_configs()
        return cls._instance

    def _load_all_configs(self):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_dir = os.path.join(root_dir, "config")
        
        # 1. Load settings.yaml
        settings_path = os.path.join(config_dir, "settings.yaml")
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                self._config['settings'] = yaml.safe_load(f)
        
        # 2. Load system prompts
        prompts_dir = os.path.join(config_dir, "system_prompts")
        self._config['prompts'] = {}
        if os.path.exists(prompts_dir):
            for filename in os.listdir(prompts_dir):
                if filename.endswith(".yaml"):
                    name = filename.replace(".yaml", "")
                    with open(os.path.join(prompts_dir, filename), 'r', encoding='utf-8') as f:
                        self._config['prompts'][name] = yaml.safe_load(f)

    def get_setting(self, path, default=None):
        """
        Get setting by dot-separated path (e.g., 'llm.model_name').
        Priority: ENV > YAML
        """
        # Try ENV first for specific keys
        env_key = path.upper().replace(".", "_")
        env_val = os.getenv(env_key)
        if env_val:
            return env_val

        # Then try YAML
        keys = path.split(".")
        val = self._config.get('settings', {})
        for key in keys:
            if isinstance(val, dict):
                val = val.get(key)
            else:
                return default
        
        return val if val is not None else default

    def get_prompt(self, agent_name, path=None):
        """
        Get prompt content for a specific agent.
        """
        agent_prompts = self._config.get('prompts', {}).get(agent_name, {})
        if not path:
            return agent_prompts
        
        keys = path.split(".")
        val = agent_prompts
        for key in keys:
            if isinstance(val, dict):
                val = val.get(key)
            else:
                return None
        return val

config_loader = ConfigLoader()
