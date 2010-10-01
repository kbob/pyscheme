#!/usr/bin/python

import string
import sys

# Data Type Map
#
# Scheme Type                   Python Type
# ------ ----                   ------ ----
#   boolean                       bool
#   integer                       int, long
#   character                     Character
#   string                        str
#   empty list			  None
#   pair			  Pair

class Character(str):
    name_to_char = {
        'nul'      : '\0',
        'alarm'    : '\a',
        'backspace': '\b',
        'tab'      : '\t',
        'newline'  : '\n',
        'vtab'     : '\v',
        'page'     : '\f',
        'return'   : '\r',
        'esc'      : '\033',
        'space'    : ' ',
        'delete'   : '\0177',
        }
    char_to_name = dict((c, n) for n, c in name_to_char.iteritems())
    name_to_char['linefeed'] = '\n'  # synonym for #\newline

string_escapes = 'abtnvfr"\\'
string_escape_to_char = dict((e, eval('"\\%s"' % e)) for e in string_escapes)
string_char_to_escape = dict((c, e)
                             for e, c in string_escape_to_char.iteritems())


ungot = None

def getc(f):
    global ungot
    if ungot:
        x, ungot = ungot, None
        return x
    return f.read(1)

def ungetc(c):
    global ungot
    assert ungot is None
    ungot = c
    
def getc_or_die(f):
    c = getc(f)
    if not c:
        exit('Unexpected EOF')
    return c


def is_digit(c):
    return c in string.digits

def is_space(c):
    return c in string.whitespace

def is_delimiter(c):
    return not c or c in '()"' or is_space(c);

def read_character(f):
    c = getc_or_die(f)
    if c in string.ascii_lowercase:
        s = ''
        while c in string.ascii_lowercase:
            s += c
            c = getc_or_die(f)
        if len(s) > 1:
            if s in Character.name_to_char:
                return Character(Character.name_to_char[s])
            else:
                exit('illegal character "#\%s' % s)
        c = s
    return Character(c)

def read_string(f):
    s = ''
    while True:
        c = getc_or_die(f)
        if c == '"':
            return s
        elif c == '\\':
            c = getc_or_die(f)
            c = string_escape_to_char.get(c, c)
        s += c

def schread(f):
    sign = 1
    while True:
        c = getc(f)
        if not c:
            break
        if is_space(c):
            continue
        if c == '-' or is_digit(c):
            if c == '-':
                sign = -1
                c = getc_or_die(f)
            n = 0
            while is_digit(c):
                n = 10 * n + ord(c) - ord('0')
                c = getc(f)
            n *= sign
            if is_delimiter(c):
                ungetc(c)
                return int(n)
            exit('number not followed by delimiter')
        elif c == '#':
            c = getc_or_die(f)
            if c.lower() == 'f':
                return False
            elif c.lower() == 't':
                return True
            elif c == '\\':
                return read_character(f)
            else:
                exit('bad input.  Unexpected "#%s"' % c)
        elif c == '"':
            return read_string(f)
        else:
            exit('bad input.  Unexpected "%s"' % c)
    print >>sys.stderr, 'EOF'
    exit(0)
        

def is_self_evaluating(exp):
    return isinstance(x, (int, long, bool, Character, str))

def scheval(exp):
    return exp

def schwrite(x):
    if isinstance(x, bool):
        sys.stdout.write(x and '#t' or '#f')
    elif isinstance(x, (int, long)):
        sys.stdout.write(str(x))
    elif isinstance(x, Character):
        x = Character.char_to_name.get(x, x)
        sys.stdout.write('#\\%s' % x)
    elif isinstance(x, str):
        print 'x=%r' % x
        s = '"'
        for c in x:
            if c in string_char_to_escape:
                s += '\\%s' % string_char_to_escape[c]
            else:
                s += c
        s += '"'
        sys.stdout.write(s)
    else:
        exit("can't write unknown type")

def main():
    while True:
        sys.stdout.write('> ')
        schwrite(scheval(schread(sys.stdin)))
        print

if __name__ == '__main__':
    main()
