import importlib

class PluginManager:
    def __init__(self):
        self.plugin_names = []
        self.plugins = []
        
    def update_plugins(self, plugin_list):
        # add plugins
        for plugin_name in plugin_list:
            if plugin_name not in self.plugin_names:
                self.plugin_names.append(plugin_name)
                self.load_plugin(plugin_name)
        # remove plugins
        for plugin_name in self.plugin_names:
            if plugin_name not in plugin_list:
                self.plugin_names.remove(plugin_name)
                self.remove_plugin(plugin_name)
        
    def load_plugin(self, plugin_name):
        plugin_cls = self._resolve_class(plugin_name)
        if plugin_cls:
            print(f"Load plugin: {plugin_name}")
            plugin = plugin_cls()
            plugin.initialize()
            self.plugins.append(plugin)
        
    def remove_plugin(self, plugin_name):
        print(f"try to remove plugin {plugin_name}")
        module_name, class_name = plugin_name.rsplit(".", 1)
        print(f"classname: {class_name}")
        for plugin in self.plugins:
            print(f"plugin.classname: {plugin.classname}")
            if plugin.classname == class_name:
                print(f"Remove plugin: {plugin_name}")
                plugin.finalize()
                self.plugins.remove(plugin)
                
    def _resolve_class(self, cls_path):
        module_name, class_name = cls_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name, None)
    
    def execute(self, data):
        for plugin in self.plugins:
            print(f"Running plugin {type(plugin).__name__}")
            data = plugin.run(data)
        return data