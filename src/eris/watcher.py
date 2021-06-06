import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys 

class PyFlowWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        print("Got it!")


def watch_file(filename):
    event_handler = PyFlowWatcher()
    observer = Observer()
    observer.schedule(event_handler, path=filename, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

watch_file(sys.argv[1])