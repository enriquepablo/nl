"""

<common noun> is <common noun> [, <common noun> ...].

<verb> is <verb> [, <verb> ...] [that can be <prep> <symbol> [, <prep> <symbol> ...]].

"""

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
    'LPAREN',
    'RPAREN',
    'EXTEND',
    'ARE',
    'IS',
    'ANDCANBE',
    'A',
    'WITHSUBJECT',
    'IF',
    'THEN',
    'COLON',
    'SEMICOLON',
    'ENDDURATION',
    'COINCIDE',
    'DURING',
    'ONWARDS',
    'INTERSECTION',
    'MAXSTART',
    'MINEND',
)

reserved = {
    'isa': 'ISA',
    'now': 'NOW',
    'at': 'AT',
    'from': 'FROM',
    'till': 'TILL',
    'extend': 'EXTEND',
    'are': 'ARE',
    'is': 'IS',
    'andcanbe': 'ANDCANBE',
    'a': 'A',
    'withsubject': 'WITHSUBJECT',
    'if': 'IF',
    'then': 'THEN',
    'endduration': 'ENDDURATION',
    'coincide': 'COINCIDE',
    'during': 'DURING',
    'onwards': 'ONWARDS',
    'intersection': 'INTERSECTION',
    'maxstart': 'MAXSTART',
    'minend': 'MINEND',
}

t_COMMA = r','
t_DOT = r'\.'
t_QMARK = r'\?'
t_LPAREN = r'\['
t_RPAREN = r'\]'
t_COLON = r':'
t_SEMICOLON = r';'
from nl.utils import t_VAR
t_NUMBER = r'(\d+)'

def t_SYMBOL(t):
    r'[a-z_]+'
    t.type = reserved.get(t.value, 'SYMBOL')    # Check for reserved words
    return t

def t_TIME(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print "Invalid date: %s" % t.value
        t.value = 0
    return t

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
