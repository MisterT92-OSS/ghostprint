"""
GhostPrint - Plugin System
Extensible plugin architecture for custom modules
"""
import importlib
import pkgutil
from typing import Dict, List, Callable, Any
from pathlib import Path


class PluginManager:
    """Manage GhostPrint plugins"""
    
    def __init__(self, plugin_dir: str = None):
        self.plugins: Dict[str, Any] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        self.plugin_dir = Path(plugin_dir) if plugin_dir else Path.home() / '.ghostprint' / 'plugins'
    
    def discover_plugins(self):
        """Discover plugins in plugin directory"""
        if not self.plugin_dir.exists():
            return
        
        for plugin_file in self.plugin_dir.glob('*.py'):
            if plugin_file.name.startswith('_'):
                continue
            
            try:
                spec = importlib.util.spec_from_file_location(
                    plugin_file.stem, plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'register'):
                    module.register(self)
                    self.plugins[plugin_file.stem] = module
            except Exception as e:
                print(f"Error loading plugin {plugin_file}: {e}")
    
    def register_hook(self, hook_name: str, callback: Callable):
        """Register a callback for a hook"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
    
    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Execute all callbacks for a hook"""
        results = []
        for callback in self.hooks.get(hook_name, []):
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"Hook error: {e}")
        return results
    
    def get_plugin(self, name: str) -> Any:
        """Get a loaded plugin"""
        return self.plugins.get(name)


class BasePlugin:
    """Base class for GhostPrint plugins"""
    
    name = "base"
    description = "Base plugin"
    version = "0.1.0"
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
    
    def run(self, target: str, **kwargs) -> Dict:
        """Main plugin execution"""
        raise NotImplementedError
    
    def register(self, plugin_manager: PluginManager):
        """Register plugin with manager"""
        plugin_manager.plugins[self.name] = self


# Example plugin template
EXAMPLE_PLUGIN = '''"""
Example GhostPrint Plugin
"""
from ghostprint.plugins import BasePlugin

class ExamplePlugin(BasePlugin):
    name = "example"
    description = "Example plugin demonstrating the API"
    version = "1.0.0"
    
    def run(self, target: str, **kwargs) -> dict:
        """Plugin execution"""
        return {
            'plugin': self.name,
            'target': target,
            'result': f"Processed {target}"
        }
    
    def register(self, plugin_manager):
        """Register with plugin manager"""
        super().register(plugin_manager)
        plugin_manager.register_hook('pre_investigation', self.pre_hook)
    
    def pre_hook(self, target: str, **kwargs):
        """Hook executed before investigation"""
        print(f"[Example Plugin] Starting investigation of {target}")


# Create instance
plugin = ExamplePlugin()
'''

def create_plugin_template(path: str, name: str):
    """Create a new plugin template"""
    plugin_dir = Path(path)
    plugin_dir.mkdir(parents=True, exist_ok=True)
    
    plugin_file = plugin_dir / f"{name}.py"
    plugin_file.write_text(EXAMPLE_PLUGIN.replace('example', name))
    
    return plugin_file