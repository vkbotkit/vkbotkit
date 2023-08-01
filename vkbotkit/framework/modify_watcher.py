"""
Copright 2023 kensoi
"""

import os
from enum import Enum
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class PluginType(Enum):
    "PluginType"

    ONE_FILE="one-file"
    PACKAGE="package"

class Handler(FileSystemEventHandler):
    "Handler"

    def dispatch(self, event):
        print(f"""
Тип события: {event.event_type},
Позиция: {event.src_path}
""")

class ModifyWatcher():
    """
    watcher for changes
    """

    def __init__(self, watcher_action):
        self.bot_path = os.getcwd()
        self.observer = Observer()
        self.handler = Handler()
        self.handler.dispatch = self.get_dispatch()
        self.plugins = {}
        self.plugin_folders_list = []
        self.watcher_action = watcher_action

        self.observer.schedule(self.handler, os.getcwd(), recursive=True)
        self.observer.start()

    def get_dispatch(self):
        """
        wrapper
        """

        def dispatch(event):
            if "__pycache__" in event.src_path:
                return

            plugin_path, _ = os.path.split(event.src_path)

            for name in self.plugin_folders_list:
                plugin_folder_path = os.path.join(self.bot_path, name)

                if not plugin_path.startswith(plugin_folder_path):
                    continue

                if plugin_path == plugin_folder_path: # One-file plugins
                    for plugin_data in self.plugins.values():
                        if plugin_data["type"] == PluginType.PACKAGE:
                            continue

                        if event.src_path == plugin_data["module_path"]:
                            return self.watcher_action(event.event_type, plugin_data)

                else: # Package plugins
                    for plugin_data in self.plugins.values():
                        if plugin_data["type"] == PluginType.ONE_FILE:
                            continue

                        if event.src_path.startswith(plugin_data["dir_path"]):
                            return self.watcher_action(event.event_type, plugin_data)

        return dispatch

    def add_watch(self, plugin, plugin_codename):
        """
        register plugin to watch it for changes
        """

        module_path = plugin.__loader__.path
        plugin_path, plugin_root_filename = os.path.split(module_path)

        for name in self.plugin_folders_list:
            plugin_folder_path = os.path.join(self.bot_path, name)

            if not plugin_path.startswith(plugin_folder_path):
                continue

            if plugin_path == plugin_folder_path: # One-file plugins
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
