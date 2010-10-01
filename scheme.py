#!/usr/bin/python

import string
import sys

class Character(str):
    name2ord = {
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
    ord2name = dict((v, k) for k, v in name2ord.iteritems())
    name2ord['linefeed'] = '\n'

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
    
def peekc(f):
    global ungot
    if not ungot:
        ungot = getc()
    return ungot

def is_digit(c):
    return c in string.digits

def is_space(c):
    return c in string.whitespace

def is_delimiter(c):
    return not c or c in '()"' or is_space(c);

def read_character(f):
    c = getc(f)
    if not c:
        exit('incomplete character literal')
    if c in string.ascii_lowercase:
        s = ''
        while c in string.ascii_lowercase:
            s += c
            c = getc(f)
        if len(s) > 1:
            if s in Character.name2ord:
                return Character(Character.name2ord[s])
            else:
                exit('illegal character "#\%s' % s)
        c = s
    return Character(c)

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
                c = getc(f)
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
            c = getc(f)
            if c.lower() == 'f':
                return False
            elif c.lower() == 't':
                return True
            elif c == '\\':
                return read_character(f)
            else:
                exit('bad input.  Unexpected "#%s"' % c)
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
        x = Character.ord2name.get(x, x)
        sys.stdout.write('#\\%s' % x)
    else:
        exit("can't write unknown type")

def main():
    while True:
        sys.stdout.write('> ')
        schwrite(scheval(schread(sys.stdin)))
        print

if __name__ == '__main__':
    main()
