#!/usr/bin/python

import string
import sys

# TODO: reimplement reader in PLY.
# TODO: reimplement writer as methods.

# Data Type Map
#
# Scheme Type                   Python Type
# ------ ----                   ------ ----
#   boolean                       bool
#   integer                       int, long
#   character                     class Character(str)
#   string                        class String(str)
#   symbol			  class Symbol(str)
#   empty list			  None
#   pair			  class Pair(list)
#   procedure                     <type 'function'>
#   environment                   class Environment(dict)
#   port                          file
#   eof-object                    type(class EOF)

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

class String(str):
    escapes = 'abtnvfr"\\'
    escape_to_char = dict((e, eval('"\\%s"' % e)) for e in escapes)
    char_to_escape = dict((c, e) for e, c in escape_to_char.iteritems())


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

def caar(pair):
    assert isinstance(pair, Pair)
    assert isinstance(pair[0], Pair)
    return pair[0][0]
    
def cadr(pair):
    assert isinstance(pair, Pair)
    assert isinstance(pair[1], Pair)
    return pair[1][0]
    
def cdar(pair):
    assert isinstance(pair, Pair)
    assert isinstance(pair[0], Pair)
    return pair[0][1]
    
def cddr(pair):
    assert isinstance(pair, Pair)
    assert isinstance(pair[1], Pair)
    return pair[1][1]
    
def caddr(pair):
    assert isinstance(pair, Pair)
    assert isinstance(pair[1], Pair)
    assert isinstance(pair[1][1], Pair)
    return pair[1][1][0]

def cdddr(pair):
    assert isinstance(pair, Pair)
    assert isinstance(pair[1], Pair)
    assert isinstance(pair[1][1], Pair)
    return pair[1][1][1]

def cadddr(pair):
    assert isinstance(pair, Pair)
    assert isinstance(pair[1], Pair)
    assert isinstance(pair[1][1], Pair)
    assert isinstance(pair[1][1][1], Pair)
    return pair[1][1][1][0]

def setcar(pair, new_car):
    assert isinstance(pair, Pair)
    pair[0] = new_car
    
def setcdr(pair, new_cdr):
    assert isinstance(pair, Pair)
    pair[1] = new_cdr

def ziplists(*lists):
    while all(lists):
        yield [car(list) for list in lists]
        lists = [cdr(list) for list in lists]

def make_compound_proc(params, body, env):
    body = cons(Symbol('begin'), body)
    return lambda args: (body, Environment.extend(params, args, env))

def is_primitive_proc(exp):
    return isinstance(exp, type(lambda: None)) and exp.func_name != '<lambda>'

class EOF(object):
    pass

def is_null_proc(args):
    return car(args) is None

def is_boolean_proc(args):
    return isinstance(car(args), bool)

def is_symbol_proc(args):
    return isinstance(car(args), Symbol)

def is_integer_proc(args):
    return isinstance(car(args), (int, long))

def is_char_proc(args):
    return isinstance(car(args), Character)

def is_string_proc(args):
    return isinstance(car(args), String)

def is_pair_proc(args):
    return isinstance(car(args), Pair)

def is_procedure_proc(args):
    return isinstance(car(args), type(lambda: None))

def char_to_integer_proc(args):
    return ord(car(args))

def integer_to_char_proc(args):
    return Character(chr(car(args)))

def number_to_string_proc(args):
    return String(car(args))

def string_to_number_proc(args):
    return int(car(args))

def symbol_to_string_proc(args):
    return String(car(args))

def string_to_symbol_proc(args):
    return Symbol(car(args))

def add_proc(args):
    result = 0
    while args:
        result += car(args)
        args = cdr(args)
    return result

def sub_proc(args):
    if cdr(args) is None:
        return -car(args)
    result = car(args)
    args = cdr(args)
    while args:
        result -= car(args)
        args = cdr(args)
    return result

def mul_proc(args):
    result = 1
    while args:
        result *= car(args)
        args = cdr(args)
    return result
    
def quotient_proc(args):
    return car(args) / cadr(args)

def remainder_proc(args):
    return car(args) % cadr(args)

def is_equal_proc(args):
    z1 = car(args)
    args = cdr(args)
    while args:
        z0, z1, args = z1, car(args), cdr(args)
        if z0 != z1:
            return False
    return True

def is_less_than_proc(args):
    z1 = car(args)
    args = cdr(args)
    while args:
        z0, z1, args = z1, car(args), cdr(args)
        if z0 >= z1:
            return False
    return True

def is_greater_then_proc(args):
    z1 = car(args)
    args = cdr(args)
    while args:
        z0, z1, args = z1, car(args), cdr(args)
        if z0 <= z1:
            return False
    return True

def cons_proc(args):
    return cons(car(args), cadr(args))

def car_proc(args):
    return caar(args)

def cdr_proc(args):
    return cdar(args)

def set_car_proc(args):
    setcar(car(args), cadr(args))
    return Symbol('ok')

def set_cdr_proc(args):
    setcdr(car(args), cadr(args))
    return Symbol('ok')

def list_proc(args):
    return args

def is_eq_proc(args):
    z1 = car(args)
    args = cdr(args)
    while args:
        z0, z1, args = z1, car(args), cdr(args)
        if z0 is not z1:
            return False
    return True

def apply_proc(args):
    exit('apply can not be called')

def interaction_environment_proc(args):
    return global_env

def null_environment_proc(args):
    return Environment(None)

def environment_proc(args):
    env = Environment(None)
    env.populate()
    return env

def eval_proc(args):
    exit('eval can not be called')

def load_proc(args):
    fname = car(args)
    assert isinstance(fname, String)
    with open(fname) as f:
        while True:
            exp = read(f)
            if exp is EOF:
                break
            result = scheval(exp, global_env)
    return result

def read_proc(args):
    port = sys.stdin if args is None else car(args)
    return read(port)

def read_char_proc(args):
    port = sys.stdin if args is None else car(args)
    c = getc(port)
    return c if c is EOF else Character(c)

def peek_char_proc(args):
    port = sys.stdin if args is None else car(args)
    c = peekc(port)
    return c if c is EOF else Character(c)

def is_input_port_proc(args):
    return isinstance(car(args), file)

def open_input_file_proc(args):
    return open(car(args))

def close_input_port_proc(args):
    car(args).close()
    return Symbol('ok')

def is_eof_object_proc(args):
    return car(args) is EOF

def open_output_file_proc(args):
    return open(car(args), 'w')

def close_output_port_proc(args):
    car(args).close()
    return Symbol('ok')

def is_output_port_proc(args):
    port = car(args)
    return isinstance(port, file) and 'r' in port.mode

def write_char_proc(args):
    c = car(args)
    assert isinstance(c, Character)
    port = sys.stdout if cdr(args) is None else cadr(args)
    port.write(c)
    return Symbol('ok')

def write_proc(args):
    obj = car(args)
    port = sys.stdout if cdr(args) is None else cadr(args)
    write(port, exp)
    port.flush()
    return Symbol('ok')

def error_proc(args):
    sys.stdout.flush()
    while args is not None:
        write(sys.stderr, car(args))
        sys.stderr.write('\n' if cdr(args) is None else ' ')
        args = cdr(args)
    exit('exiting')

class Environment(dict):
    def __init__(self, parent):
        self.parent = parent

    @classmethod
    def extend(cls, vars, values, parent):
        env = cls(parent)
        env.update(ziplists(vars, values))
        return env

    def __getitem__(self, var):
        if var in self:
            return self.get(var)
        if not isinstance(self.parent, Environment):
            exit('variable "%s" not found' % var)
        return self.parent[var]

    def set_variable(self, var, value):
        if var in self:
            self[var] = value
        else:
            assert isinstance(self.parent, Environment)
            self.parent.set_variable(var, value)

    def populate(self):
        self['null?']                   = is_null_proc
        self['boolean?']                = is_boolean_proc
        self['symbol?']                 = is_symbol_proc
        self['integer?']                = is_integer_proc
        self['char?']                   = is_char_proc
        self['string?']                 = is_string_proc
        self['pair?']                   = is_pair_proc
        self['procedure?']              = is_procedure_proc
        self['char->integer']           = char_to_integer_proc
        self['integer->char']           = integer_to_char_proc
        self['number->string']          = number_to_string_proc
        self['string->number']          = string_to_number_proc
        self['symbol->string']          = symbol_to_string_proc
        self['string->symbol']          = string_to_symbol_proc
        self['+']                       = add_proc
        self['-']                       = sub_proc
        self['*']                       = mul_proc
        self['quotient']                = quotient_proc
        self['remainder']               = remainder_proc
        self['=']                       = is_equal_proc
        self['<']                       = is_less_than_proc
        self['>']                       = is_greater_then_proc
        self['cons']                    = cons_proc
        self['car']                     = car_proc
        self['cdr']                     = cdr_proc
        self['set-car!']                = set_car_proc
        self['set-cdr!']                = set_cdr_proc
        self['list']                    = list_proc
        self['eq?']                     = is_eq_proc
        self['apply']                   = apply_proc
        self['interaction-environment'] = interaction_environment_proc
        self['null-environment']        = null_environment_proc
        self['environment']             = environment_proc
        self['eval']                    = eval_proc
        self['load']                    = load_proc
        self['read']                    = read_proc
        self['read-char']               = read_char_proc
        self['peek-char']               = peek_char_proc
        self['input-port?']             = is_input_port_proc
        self['open-input-file']         = open_input_file_proc
        self['close-input-port']        = close_input_port_proc
        self['eof-object?']             = is_eof_object_proc
        self['write']                   = write_proc
        self['write-char']              = write_char_proc
        self['output-port?']            = is_output_port_proc
        self['open-output-file']        = open_output_file_proc
        self['close-output-port']       = close_output_port_proc
        self['error']                   = error_proc

global_env = Environment(None)
global_env.populate()

ungot = {}

def getc(f):
    if f in ungot:
        c = ungot[f]
        del ungot[f]
        return c
    else:
        return f.read(1) or EOF

def ungetc(f, c):
    assert f not in ungot
    ungot[f] = c
    
def peekc(f):
    ungot[f] = c = getc(f)
    return c

def getc_or_die(f):
    c = getc(f)
    if c is EOF:
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
    return (c is not EOF and (is_initial(c) or is_digit(c) or c in '+-.@'))

def eat_whitespace(f):
    while True:
        c = getc(f)
        if c is EOF:
            ungetc(f, c)
            break
        if c == ';':
            while c and c != '\n':
                c = getc(f)
            continue
        if not is_space(c):
            ungetc(f, c)
            break

def read_character(f):
    c = getc_or_die(f)
    if c in string.ascii_lowercase:
        s = ''
        while c in string.ascii_lowercase:
            s += c
            c = getc(f)
        ungetc(f, c)
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
            return String(s)
        elif c == '\\':
            c = getc_or_die(f)
            c = String.escape_to_char.get(c, c)
        s += c

def read_pair(f):
    eat_whitespace(f)
    c = getc_or_die(f)
    if c == ')':
        return None
    ungetc(f, c)
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
        ungetc(f, c)
        cdr_obj = read_pair(f)
    return cons(car_obj, cdr_obj)

def read_or_die(f):
    exp = read(f)
    if exp is EOF:
        exit('unexpected EOF')
    return exp

def read(f):
    sign = 1
    while True:
        eat_whitespace(f)
        c = getc(f)
        if c is EOF:
            return EOF
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
                ungetc(f, c)
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
        

def is_self_evaluating(exp):
    return isinstance(exp, (int, long, bool, Character, String))

def is_variable(exp):
    return isinstance(exp, Symbol)

def tagged_list_predicate(sym):
    sym = Symbol(sym)    
    return lambda exp: isinstance(exp, Pair) and car(exp) is sym

is_quotation  = tagged_list_predicate('quote')
is_definition = tagged_list_predicate('define')
is_assignment = tagged_list_predicate('set!')
is_if         = tagged_list_predicate('if')
is_lambda     = tagged_list_predicate('lambda')
is_begin      = tagged_list_predicate('begin')
is_cond       = tagged_list_predicate('cond')
is_let        = tagged_list_predicate('let')
is_and        = tagged_list_predicate('and')
is_or         = tagged_list_predicate('or')

def is_true(exp):
    return exp is not False

def is_false(exp):
    return exp is False

def is_application(exp):
    return isinstance(exp, Pair)

def eval_variable(exp, env):
    return env[exp]

def eval_quotation(exp, env):
    return cadr(exp)

def eval_definition(exp, env):
    var = cadr(exp)
    if isinstance(var, Pair):
        var, params = car(var), cdr(var)
        value = make_compound_proc(params, cddr(exp), env)
    else:
        value = scheval(caddr(exp), env)
    env[var] = value
    return Symbol('ok')

def eval_assignment(exp, env):
    env.set_variable(cadr(exp), scheval(caddr(exp), env))
    return Symbol('ok')

def eval_lambda(exp, env):
    return make_compound_proc(cadr(exp), cddr(exp), env)

def cond_to_if(exp):

    def make_if(predicate, consequent, alternative):
        return cons(Symbol('if'),
                    cons(predicate,
                         cons(consequent,
                              cons(alternative, None))))

    is_cond_else_clause = tagged_list_predicate('else')

    def sequence_to_exp(seq):
        if seq is None:
            return None
        if cdr(seq) is None:
            return car(seq)
        return make_begin(seq)

    def expand_clauses(clauses):
        if clauses is None:
            return False
        clause = car(clauses)
        if is_cond_else_clause(clause):
            if cdr(clauses) is not None:
                exit("else clause isn't last in cond")
            return sequence_to_exp(cdr(clause))
        return make_if(car(clause),
                       sequence_to_exp(cdr(clause)),
                       expand_clauses(cdr(clauses)))

    return expand_clauses(cdr(exp))

def let_to_application(exp):
    make_application  = cons
    let_bindings      = cadr
    let_body          = cddr
    binding_parameter = car
    binding_argument  = cadr

    def bindings_parameters(bindings):
        if bindings is None:
            return None
        return cons(binding_parameter(car(bindings)),
                    bindings_parameters(cdr(bindings)))

    def bindings_arguments(bindings):
        if bindings is None:
            return None
        return cons(binding_argument(car(bindings)),
                    bindings_arguments(cdr(bindings)))

    def let_parameters(exp):
        return bindings_parameters(let_bindings(exp))

    def let_arguments(exp):
        return bindings_arguments(let_bindings(exp))

    def make_lambda(params, body):
        return cons(Symbol('lambda'), cons(params, body))


    return make_application(make_lambda(let_parameters(exp),
                                        let_body(exp)),
                            let_arguments(exp))

def apply_operands(args):
    def prepare_apply_operands(args):
        if cdr(args) is None:
            return car(args)
        return cons(car(args), prepare_apply_operands(cdr(args)))
    return prepare_apply_operands(cdr(args))

def list_of_values(exp, env):
    if exp is None:
        return None
    return cons(scheval(car(exp), env), list_of_values(cdr(exp), env))

def scheval(exp, env):
    while True:
        if is_self_evaluating(exp):
            return exp
        elif is_variable(exp):
            return eval_variable(exp, env)
        elif is_quotation(exp):
            return eval_quotation(exp, env)
        elif is_definition(exp):
            return eval_definition(exp, env)
        elif is_assignment(exp):
            return eval_assignment(exp, env)
        elif is_if(exp):
            if is_true(scheval(cadr(exp), env)):
                exp = caddr(exp)
                continue
            elif isinstance(cdddr(exp), Pair):
                exp = cadddr(exp)
                continue
            return False
        elif is_lambda(exp):
            return eval_lambda(exp, env)
        elif is_begin(exp):
            exp = cdr(exp)
            while cdr(exp) is not None:
                scheval(car(exp), env)
                exp = cdr(exp)
            exp = car(exp)
            continue
        elif is_cond(exp):
            exp = cond_to_if(exp)
            continue
        elif is_let(exp):
            exp = let_to_application(exp)
            continue
        elif is_and(exp):
            exp = cdr(exp)
            if exp is None:
                return True
            while cdr(exp) is not None:
                result = scheval(car(exp), env)
                if is_false(result):
                    return result
                exp = cdr(exp)
            exp = car(exp)
            continue
        elif is_or(exp):
            exp = cdr(exp)
            if exp is None:
                return False
            while cdr(exp) is not None:
                result = scheval(car(exp), env)
                if is_true(result):
                    return result
                exp = cdr(exp)
            exp = car(exp)
            continue
        elif is_application(exp):
            proc = scheval(car(exp), env)
            args = list_of_values(cdr(exp), env)
            if proc is eval_proc:
                exp = car(args)
                env = cadr(args)
                continue
            if proc is apply_proc:
                proc = car(args)
                args = apply_operands(args)
            if is_primitive_proc(proc):
                return proc(args)
            else:
                exp, env = proc(args)
                continue
        else:
            exit('must be expression: "%s"' % exp)

def write_pair(f, pair):
    assert isinstance(pair, Pair)
    write(f, car(pair))
    rest = cdr(pair)
    if isinstance(rest, Pair):
        f.write(' ')
        write_pair(f, rest)
    elif rest is not None:
        f.write(' . ')
        write(f, rest)

def write(f, x):
    if isinstance(x, bool):
        f.write(x and '#t' or '#f')
    elif isinstance(x, (int, long)):
        f.write(str(x))
    elif isinstance(x, Character):
        x = Character.char_to_name.get(x, x)
        f.write('#\\%s' % x)
    elif isinstance(x, Symbol):
        f.write(x)
    elif isinstance(x, String):
        s = '"'
        for c in x:
            if c in String.char_to_escape:
                s += '\\%s' % String.char_to_escape[c]
            else:
                s += c
        s += '"'
        f.write(s)
    elif isinstance(x, Environment):
        while x is not None:
            f.write(str(x))
            x = x.parent
    elif isinstance(x, Pair):
        f.write('(')
        write_pair(f, x)
        f.write(')')
    elif isinstance(x, type(lambda: None)):
        f.write('#<procedure>')
    elif x is None:
        f.write('()')
    elif isinstance(x, file):
        f.write('#<port>')
    elif x is EOF:
        f.write('#<eof-object>')
    else:
        exit("can't write unknown type")

def main():
    while True:
        sys.stdout.write('> ')
        exp = read(sys.stdin)
        if exp is EOF:
            print
            break
        write(sys.stdout, scheval(exp, global_env))
        print

if __name__ == '__main__':
    main()
