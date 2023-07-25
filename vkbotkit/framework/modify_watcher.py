from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from enum import Enum


class PluginType(Enum):
    ONE_FILE="one-file"
    PACKAGE="package"

class Handler(FileSystemEventHandler):
    def dispatch(self, event):
        print(f"""
Тип события: {event.event_type},
Позиция: {event.src_path}
""")
        
class ModifyWatcher():
    def __init__(self, watcher_action):
        self.library_directory = os.getcwd() + os.sep + "library"
        self.observer = Observer()
        self.handler = Handler()
        self.handler.dispatch = self.get_dispatch()
        self.plugins = {}
        self.watcher_action = watcher_action

        self.observer.schedule(self.handler, self.library_directory, recursive=True)
        self.observer.start()

    def get_dispatch(self):
        def dispatch(event):
            if event.src_path.startswith(os.path.join(self.library_directory, "__pycache__")):
                return
            
            plugin_path, _ = os.path.split(event.src_path)

            if plugin_path == self.library_directory: # One-file plugins
                for plugin_data in self.plugins.values():
                    if plugin_data["type"] == PluginType.PACKAGE:
                        continue
                    
                    if event.src_path == plugin_data["module_path"]:
                        self.watcher_action(event.event_type, plugin_data)
                        break
            
            else: # Package plugins
                for plugin_data in self.plugins.values():
                    if plugin_data["type"] == PluginType.ONE_FILE:
                        continue

                    if event.src_path.startswith(plugin_data["dir_path"]):
                        self.watcher_action(event.event_type, plugin_data)
                        break            
            pass

        return dispatch
    
    def add_watch(self, plugin, plugin_codename):
        module_path = plugin.__loader__.path
        plugin_path, plugin_root_filename = os.path.split(module_path)

        if plugin_path == self.library_directory:
            # one-file plugin
            
            self.plugins[plugin_codename] = {
                "plugin_codename": plugin_codename,
                "plugin": plugin,
                "type": PluginType.ONE_FILE,
                "filename": plugin_root_filename,
                "module_path": module_path
            }

        else:
            # package plugin

            self.plugins[plugin_codename] = {
                "plugin_codename": plugin_codename,
                "plugin": plugin,
                "type": PluginType.PACKAGE,
                "dir_path": plugin_path,
                "module_path": module_path
            }
