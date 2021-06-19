import os
import sys
import time

from driver import compile_py


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
out_path  = None

def on_change():
    os.system('clear')
    src = open(file_path, 'r').read()
    curr_time = time.strftime('%H:%M:%S')
    print(f"[{curr_time}] checked '{file_path}'\n")

    try:
        code = compile_py(src)
        if not code:
            return None
        
        out_file = open(out_path, "w")
        out_file.write(code)
        out_file.close()
        os.system(f'clang-format -i {out_path}')
    except SyntaxError as s:
        print('Syntax error')
    except (NameError, AttributeError) as err:
        raise err


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) != 2:
        print('Usage: watch <filename>')
    else:
        file_path = argv[1]
        out_path = file_path.split('.')[0] + '.c'
        watcher = Watcher(file_path, call_func_on_change=on_change)
        watcher.watch()
