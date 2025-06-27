import subprocess
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ReloadHandler(FileSystemEventHandler):
    def __init__(self, process):
        self.process = process

    def on_any_event(self, event):
        if event.src_path.endswith(".py"):
            self.process.terminate()
            self.process = subprocess.Popen(["uvicorn", "mq7_v1:app", "--host", "0.0.0.0", "--port", "8000"])


def main():
    process = subprocess.Popen(["uvicorn", "mq7_v1:app", "--host", "0.0.0.0", "--port", "8000"])
    event_handler = ReloadHandler(process)
    observer = Observer()
    observer.schedule(event_handler, path="events", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        process.terminate()
    observer.join()


if __name__ == "__main__":
    main()
