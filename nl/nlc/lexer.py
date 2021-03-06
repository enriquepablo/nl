# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 by Enrique Pérez Arnaud <enriquepablo@gmail.com>
#
# This file is part of nlproject.
#
# The nlproject is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The nlproject is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with any part of the nlproject.
# If not, see <http://www.gnu.org/licenses/>.

import ply.lex as lex

tokens = (
    'DOT',
    'QMARK',
    'ISA',
    'TERM',
    'VAR',
    'NUMBER',
    'TIME',
    'NOW',
    'COMMA',
    'AT',
    'SINCE',
    'TILL',
    'LBRACK',
    'RBRACK',
    'EXTEND',
    'ARE',
    'IS',
    'A',
    'CAN',
    'IF',
    'THEN',
    'COLON',
    'SEMICOLON',
    'FINISH',
    'COINCIDE',
    'DURING',
    'ONWARDS',
    'INTERSECTION',
    'MAXSTART',
    'MINEND',
    'LPAREN',
    'RCURL',
    'LCURL',
    'RPAREN',
    'SUBWORDOF',
    'PASSTIME',
    'UNTIL',
    'PLUS',
    'MINUS',
    'PRODUCT',
    'DIVISION',
    'LT',
    'GT',
    'EQ',
    'NEQ',
    'DISTINCT',
    'NOT',
    'IMPORT',
    'URI',
)

reserved = {
    'isa': 'ISA',
    'now': 'NOW',
    'at': 'AT',
    'since': 'SINCE',
    'till': 'TILL',
    'extend': 'EXTEND',
    'are': 'ARE',
    'is': 'IS',
    'a': 'A',
    'can': 'CAN',
    'if': 'IF',
    'then': 'THEN',
    'finish': 'FINISH',
    'coincide': 'COINCIDE',
    'during': 'DURING',
    'onwards': 'ONWARDS',
    'intersection': 'INTERSECTION',
    'maxstart': 'MAXSTART',
    'minend': 'MINEND',
    'subwordof': 'SUBWORDOF',
    'passtime': 'PASSTIME',
    'until': 'UNTIL',
    'distinct': 'DISTINCT',
    'not': 'NOT',
    'import': 'IMPORT',
}

t_COMMA = r','
t_DOT = r'\.'
t_QMARK = r'\?'
t_LBRACK = r'\['
t_RBRACK = r'\]'
t_COLON = r':'
t_SEMICOLON = r';'
from nl.utils import t_VAR
t_NUMBER = r'(-?\d*\.?\d+)'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LCURL = r'\{'
t_RCURL = r'\}'
t_PLUS = r'\+'
t_MINUS = r'-'
t_PRODUCT = r'\*'
t_DIVISION = r'/'
t_LT = r'<'
t_GT = r'>'
t_EQ = r'='
t_NEQ = r'<>'
t_URI = r'"[^"]+"'


def t_TERM(t):
    r'[a-z][a-z_]*\d*'
    t.type = reserved.get(t.value, 'TERM')    # Check for reserved words
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
