"""
"""

import datetime
import time
import ply.lex as lex

tokens = (
    'DOT',
    'QMARK',
    'ISA',
    'SYMBOL',
    'VAR',
    'NUMBER',
    'TIME',
    'NOW',
    'COMMA',
    'AT',
    'FROM',
    'TILL',
)

reserved = {
    'isa': 'ISA',
    'now': 'NOW',
    'at': 'AT',
    'from': 'FROM',
    'til': 'TILL',
}

t_COMMA = r','
t_DOT = r'\.'
t_QMARK = r'\?'
t_VAR = r'[A-Z][A-Za-z]+[0-9]+'

def t_SYMBOL(t):
    r'[a-z]+'
    t.type = reserved.get(t.value, 'SYMBOL')    # Check for reserved words
    return t

def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)    
    except ValueError:
        print "Number %s is too large!" % t.value
        t.value = 0
    return t

def t_TIME(t):
    r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\{2}'
    try:
        dt = datetime.datetime.strptime(t.value, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        print "Invalid date: %s" % t.value
    return int(time.mktime(dt.timetuple()))

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

# Build the lexer
lex.lex()

if __name__ == '__main__':
    lex.runmain()
