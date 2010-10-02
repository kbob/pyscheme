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
#   symbol			  Symbol
#   empty list			  None
#   pair			  Pair
#   eof-object                    exit
#                                 (a built-in function with a suggestive name)

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

class Symbol(str):

    all = {}

    def __new__(cls, value):
        try:
            return cls.all[value]
        except KeyError:
            new_sym = super(Symbol, cls).__new__(cls, value)
            cls.all[value] = new_sym
            return new_sym


class Pair(list):
    pass

def cons(car, cdr):
    return Pair([car, cdr])

def car(pair):
    assert isinstance(pair, Pair)
    return pair[0]

def cdr(pair):
    assert isinstance(pair, Pair)
    return pair[1]

def setcar(pair, new_car):
    assert isinstance(pair, Pair)
    pair[0] = new_car
    
def setcdr(pair, new_cdr):
    assert isinstance(pair, Pair)
    pair[1] = new_cdr


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
    ungot = getc(f)
    return ungot

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

def is_initial(c):
    return c in string.ascii_letters or c in '!$%&*:<=>?^_~'

def is_subsequent(c):
    return is_initial(c) or is_digit(c) or c in '+=.@'

def eat_whitespace(f):
    while True:
        c = getc(f)
        if not is_space(c):
            ungetc(c)
            break

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
                exit('illegal character "#\%s"' % s)
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

def read_pair(f):
    eat_whitespace(f)
    c = getc_or_die(f)
    if c == ')':
        return None
    ungetc(c)
    car_obj = read_or_die(f)
    eat_whitespace(f)
    c = getc_or_die(f)
    if c == '.':
        c = peekc(f)
        if not is_delimiter(c):
            exit('dot not followed by delimiter')
        eat_whitespace(f)
        cdr_obj = read_or_die(f)
        eat_whitespace(f)
        c = getc_or_die(f)
        if c != ')':
            exit('expected ")", got "%s"' % c)
    else:
        ungetc(c)
        cdr_obj = read_pair(f)
    return cons(car_obj, cdr_obj)

def read_or_die(f):
    exp = read(f)
    if exp is exit:
        exit('unexpected EOF')
    return exp

def read(f):
    sign = 1
    while True:
        c = getc(f)
        if not c:
            break
        if is_space(c):
            continue
        if (c == '-' and is_digit(peekc(f))) or is_digit(c):
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
        elif is_initial(c) or (c in '+-' and
                               (is_delimiter(peekc(f)) or peekc(f) == '>')):
            sym = c
            while is_subsequent(peekc(f)):
                sym += getc(f)
            return Symbol(sym)
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
        elif c == '(':
            return read_pair(f)
        elif c == "'":
            return cons(Symbol('quote'), cons(read(f), None))
        else:
            exit('bad input.  Unexpected "%s"' % c)
    return exit
        

def is_self_evaluating(exp):
    return isinstance(exp, (int, long, bool, Character, str))

def is_quotation(exp):
    return isinstance(exp, Pair) and car(exp) is Symbol('quote')

def scheval(exp):
    if is_self_evaluating(exp):
        return exp
    elif is_quotation(exp):
        return car(cdr(exp))
    exit('must be expression: "%s"' % exp)

def write_pair(pair):
    assert isinstance(pair, Pair)
    write(car(pair))
    rest = cdr(pair)
    if isinstance(rest, Pair):
        sys.stdout.write(' ')
        write_pair(rest)
    elif rest is not None:
        sys.stdout.write(' . ')
        write(rest)

def write(x):
    if isinstance(x, bool):
        sys.stdout.write(x and '#t' or '#f')
    elif isinstance(x, (int, long)):
        sys.stdout.write(str(x))
    elif isinstance(x, Character):
        x = Character.char_to_name.get(x, x)
        sys.stdout.write('#\\%s' % x)
    elif isinstance(x, Symbol):
        sys.stdout.write(x)
    elif isinstance(x, str):
        s = '"'
        for c in x:
            if c in string_char_to_escape:
                s += '\\%s' % string_char_to_escape[c]
            else:
                s += c
        s += '"'
        sys.stdout.write(s)
    elif isinstance(x, Pair):
        
        sys.stdout.write('(')
        write_pair(x)
        sys.stdout.write(')')
    elif x is None:
        sys.stdout.write('()')
    else:
        exit("can't write unknown type")

def main():
    while True:
        sys.stdout.write('> ')
        exp = read(sys.stdin)
        if exp is exit:
            print
            break
        write(scheval(exp))
        print

if __name__ == '__main__':
    main()
