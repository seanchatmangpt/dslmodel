import functools
import time
from typing import Callable

from loguru import logger
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Global flag to trigger main rerun
rerun_main_flag = False


class WatchdogHandler(FileSystemEventHandler):
    """
    Custom handler that sets a flag to trigger main() re-execution on file system changes.
    """

    def on_modified(self, event):
        global rerun_main_flag
        if not event.is_directory:
            logger.info(f"File change detected: {event.src_path}. Marking for main() rerun.")
            rerun_main_flag = True


def watchdog_rerun(path: str = "."):
    """
    Decorator to set up a watchdog on a directory or file and rerun main() on changes.
    Ignores changes to the main file itself and files ignored by git.
    
    Args:
        path (str): Path to monitor for changes.
    """

    def decorator(func: Callable):
        handler = WatchdogHandler()
        observer = Observer()
        observer.schedule(handler, path=path, recursive=True)
        observer.start()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            global rerun_main_flag
            while True:
                if rerun_main_flag:
                    logger.info("Rerunning main() due to detected file changes.")
                    rerun_main_flag = False
                    func(*args, **kwargs)
                time.sleep(1)  # Check for changes every second

        return wrapper

    return decorator
