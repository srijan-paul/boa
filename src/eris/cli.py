import os
import sys
import time

from driver import compile_py
from error_report import info, success
from termcolor import colored


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
            except Exception as inst:
                raise inst


file_path = None
out_path = None
out_bin = None
flags = '-O3'


def on_change():
    os.system('clear')
    src = open(file_path, 'r').read()
    curr_time = time.strftime('%H:%M:%S')
    print(f"[{curr_time}] checked '{file_path}'\n")

    try:
        info('Changes detected, restarting inference engine:')
        checked_tree = compile_py(src, False, 'infer')
        if not checked_tree:
            return None

        time.sleep(0.7)
        info('Generating Assembly (Syntax=ATnT):')

        time.sleep(0.7)
        # os.system(f'rm {out_path}')
        dst_bin = colored(out_bin, 'yellow')
        success(f'Linking successful. Output file: {dst_bin}')

    except SyntaxError as err:
        info('Syntax Error in source file')
        raise err

    except (NameError, AttributeError) as err:
        raise err


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) != 2:
        print('Usage: watch <filename>')
    else:
        file_path = argv[1]
        out_path = file_path.split('.')[0] + '.c'
        out_bin = file_path.split('.')[0] + '.exe'
        watcher = Watcher(file_path, call_func_on_change=on_change)
        watcher.watch()
