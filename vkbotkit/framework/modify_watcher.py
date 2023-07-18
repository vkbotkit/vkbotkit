from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from importlib.util import spec_from_file_location, module_from_spec

class Handler(FileSystemEventHandler):
    def dispatch(self, event):
        print(f"""
Тип события: {event.event_type},
Позиция: {event.src_path}
""")

        
class ModifyWatcher():
    def __init__(self, paths, watcher_action):
        self.paths = paths
        self.observer = Observer()
        self.handler = Handler()
        self.handler.dispatch = self.get_dispatch()
        self.mod_map = {}
        self.watcher_action = watcher_action

        self.observer.schedule(self.handler, os.getcwd(), recursive=True)
        self.observer.start()

    def get_dispatch(self):
        def dispatch(event):
            if event.src_path not in self.mod_map:
                return
            
            for path in self.paths:
                if path is None:
                    continue

                module_data = self.mod_map[event.src_path]
                self.watcher_action(event.event_type, module_data)

                return

        return dispatch
    
    def add_watch(self, module, module_path_name):
        self.mod_map[module.__loader__.path] = {
            "module": module,
            "module_path": module.__loader__.path,
            "module_path_name": module_path_name
        }


if __name__ == "__main__":
    paths = [
        "C:\\Users\\kenso\\OneDrive\\Документы\\GitHub\\vkbotkit\\vkbotkit\\objects",
    ]
    watcher = ModifyWatcher(paths)
