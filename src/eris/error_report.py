from termcolor import colored, cprint
from os import system

system('color')


class Location:
    def __init__(self, node):
        self.line = node.lineno
        self.col_offset = node.col_offset
        self.end_col_offset = node.end_col_offset
        self.end_line = node.end_lineno


def report(src: str, msg: str, node):
    loc = Location(node)
    line_no_str = str(loc.line) + '| '
    line = src.splitlines()[loc.line - 1]

    padding = ' ' * (loc.col_offset  + len(line_no_str))

    squiggle_len = loc.end_col_offset - loc.col_offset
    squiggle = colored('^' * squiggle_len, 'red', 'on_grey', ['bold'])

    print(colored(line_no_str, 'red', 'on_grey', ['dark'])  + line)
    print(padding + squiggle)
    print(colored('[Error] ', 'red', 'on_grey', ['bold']) + msg)

def info(msg: str):
    print(colored('[INFO] ', 'blue') + msg)

def success(msg: str):
    print(colored('[DONE] ', 'green') + msg)