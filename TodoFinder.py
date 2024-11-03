"""
    A small utility file that allows you to find TODOs in any directory or a file.
    Edit the TODO_BASE and FILE_FORMATS constants for your needs. You can use absolute and relative paths.
    Usage:
        python todo.py [path]
"""

import sys
import os
from typing import Union


CPP_COMMENTS = [('//', '\n'), ('/*', '*/')]
PY_COMMENTS = [('#', '\n'), ('"""', '"""')]


TODO_BASE = 'TODO:'
FILE_FORMATS = {
    'cpp': CPP_COMMENTS, 'hpp': CPP_COMMENTS,
    'py': PY_COMMENTS
}


def find_next_comment(content: str, comments: str, start=0):
    for begin, end in comments:
        index_begin = content.find(begin, start)

        if index_begin != -1:
            index_end = content.find(end, index_begin)

            if index_end == -1:
                index_end = len(content) - 1

            return index_begin, index_end


def parse(path: str, comments) -> list[str]:
    with open(path, 'r') as file:
        content = ''.join(file.readlines())

    todos = []
    start = 0

    while indecies := find_next_comment(content, comments, start):
        begin, todo_end = indecies
        todo_begin = content.find(TODO_BASE, begin)

        if todo_begin != -1 and todo_begin < todo_end:
            todo = content[todo_begin + len(TODO_BASE):todo_end+1].strip()

            if len(todo) > 0:
                todos.append(todo)

        start = todo_end + 1

    return todos


def search(path: str) -> Union[str, dict]:
    name = os.path.basename(path)

    if os.path.isdir(path):
        for entry in os.listdir(path):
            search(f'{path}/{entry}')
    else:
        dot_index = name.find('.')

        if dot_index == 0:
            dot_index = name.find('.')

        if dot_index == -1 and FILE_FORMATS.count('') > 0 or dot_index >= 0:
            if dot_index < len(name) - 1:
                format = name[dot_index+1:]

                if format in FILE_FORMATS:
                    for todo in parse(path, FILE_FORMATS[format]):
                        print(f'{path}: {todo}')


def main(args: list[str]):
    assert len(args) == 2, "No path was provided"
    assert os.path.exists(args[1]), "Path doesn't exist"

    search(os.path.abspath(args[1]).replace('\\', '/'))


if __name__ == "__main__":
    main(sys.argv)
