#!/usr/bin/python

import sys

ungot = None

def getc():
    global ungot
    if ungot:
        x, ungot = ungot, None
        return x
    return sys.stdin.read(1)

def ungetc(c):
    global ungot
    assert ungot is None
    ungot = c
    
def is_digit(c):
    return c in '0123456879'

def is_space(c):
    return c in ' \t\r\n'

def is_delimiter(c):
    return not c or c in '()"' or is_space(c);

def schread():
    sign = 1
    while True:
        c = getc()
        if not c:
            break
        if is_space(c):
            continue
        if c == '-' or is_digit(c):
            if c == '-':
                sign = -1
                c = getc()
            n = 0
            while is_digit(c):
                n = 10 * n + ord(c) - ord('0')
                c = getc()
            n *= sign
            if is_delimiter(c):
                ungetc(c)
                return int(n)
            exit('number not followed by delimiter')
        else:
            exit('bad input.  Unexpected "%s"' % c)
    print >>sys.stderr, 'EOF'
    exit(0)
        

def is_self_evaluating(exp):
    return isinstance(x, (int, long))

def scheval(exp):
    return exp

def schwrite(x):
    if isinstance(x, (int, long)):
        sys.stdout.write(str(x))
    else:
        exit("can't write unknown type")

def main():
    while True:
        print '>',
        schwrite(scheval(schread()))
        print

if __name__ == '__main__':
    main()
