SPACES = [' ', '\t', '\n', '\r']


def read_file(filename: str) -> list[str]:
    with open(filename, 'r') as f:
        return [l[:-1] if l[-1] in SPACES else l for l in f.readlines()]


def skip_whitespaces(line, index) -> int:
    # skip until not a whitespace
    while index < len(line) and line[index] in SPACES:
        index += 1

    return index if index < len(line) else -1

def is_comment(line, index) -> int:
    return line[index] in (';', '#')


def parse_section(lines: list[str], index):
    props = {}

    for offset, line in enumerate(lines[index:]):
        i = skip_whitespaces(line, 0)

        if i == -1:
            continue

        # a comment, so move on to the next line
        if is_comment(line, i):
            continue

        if line[i] == '[':
            return props, index + offset
        
        eq_pos = line.find('=')
        
        if eq_pos == -1:
            raise SyntaxError(f'expected \'=\' to occur in <name>=<value> but got {line[i:]}')    

        name = line[i:eq_pos].strip()
        value_pos = eq_pos+1

        if value_pos >= len(line):
            raise SyntaxError(f'expected a value after \'=\' but got {line[i:]}') 

        props[name] = line[value_pos:].strip()

    return props, index + offset + 1


def parse_ini_file(filename):
    lines = read_file(filename)

    sections = {}
    i = 0

    while i < len(lines):
        j = skip_whitespaces(lines[i], 0)

        # start of a section
        if lines[i][j] == '[':
            # now read a name of the section
            name_end = lines[i].find(']', j)
            name = lines[i][j+1:name_end]

            # parse a section and return a dict of properties
            # and an index of the start of the next section
            sections[name], i = parse_section(lines, i + 1)
        else:
            if not is_comment(lines[i], j):
                raise SyntaxError(f'expected a section name: [<name>], but got \'{lines[i][j:]}\'')
            
            i += 1
        
    return sections
        

def main():
    from sys import argv
    print(parse_ini_file(argv[1]))


if __name__ == '__main__':
    main()
