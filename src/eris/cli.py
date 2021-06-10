import os
import sys
import time

from checker import Checker
from ast import parse


class Watcher(object):
    running = True
    refresh_delay_secs = 1

    def __init__(self, watch_file, call_func_on_change=None, *args, **kwargs):
        self._cached_stamp = 0
        self.filename = watch_file
        self.call_func_on_change = call_func_on_change
        self.args = args
        self.kwargs = kwargs

    def look(self):
        stamp = os.stat(self.filename).st_mtime
        if stamp != self._cached_stamp:
            self._cached_stamp = stamp
            if self.call_func_on_change is not None:
                self.call_func_on_change(*self.args, **self.kwargs)

    def watch(self):
        while self.running:
            try:
                # Look for changes
                time.sleep(self.refresh_delay_secs)
                self.look()
            except KeyboardInterrupt:
                print('\nDone')
                break
            except FileNotFoundError:
                # Action on file not found
                print('File not found')
                return
            except:
                print('Unhandled error: %s' % sys.exc_info()[0])


file_path = None


def on_change():
    os.system('clear')
    src = open(file_path, 'r').read()
    curr_time = time.strftime('%H:%M:%S')
    print(f"[{curr_time}] checked '{file_path}'\n")

    try:
        checker = Checker(parse(src), src)
        checker.check()
    except SyntaxError:
        print('Syntax error')


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) != 2:
        print('Usage: watch <filename>')
    else:
        file_path = argv[1]
        watcher = Watcher(file_path, call_func_on_change=on_change)
        watcher.watch()
