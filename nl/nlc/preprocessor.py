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

"""

###############

def-macro name: $op @preds
    ...

macro name: $op: ... $
            @preds: ... @
                    ... @

"""

import re
from collections import defaultdict
import ply.yacc as yacc
import ply.lex as lex

OP_PAT = re.compile(r'^\$(\w+)$')

# lexer

class Prelex(object):
    tokens = (
        'SYMBOL',
        'DOLLAR',
        'DOT',
        'QMARK',
        'COLON',
        'DEFMACRO',
        'MACRO',
    )

    reserved = {
        'macro': 'MACRO',
        'def-macro': 'DEFMACRO',
    }

    def __init__(self):
        self.lexer = lex.lex(module=self)

    def t_DOLLAR(self, t):
        r'\$'
        return t

    def t_DOT(self, t):
        r'\.'
        return t

    def t_QMARK(self, t):
        r'\?'
        return t

    def t_COLON(self, t):
        r':'
        return t

    def t_SYMBOL(self, t):
        r'[^\s]*[^\s:\.\?]'
        t.type = self.reserved.get(t.value, 'SYMBOL')    # Check for reserved words
        return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'

    # Error handling rule
    def t_error(self, t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok: break
            print tok


# Preprocessor

class Macro(object):
    def __init__(self, name, ops, sen):
        self.name = name
        self.ops = ops
        self.sentence = sen

# BNF

class Preprocessor(object):

    def __init__(self):
        self.macros = defaultdict(dict)
        lexer = Prelex()
        self.tokens = lexer.tokens
        self.parser = yacc.yacc(module=self)
        self.lexer = lexer.lexer

    def parse(self, s):
        return self.parser.parse(s, lexer=self.lexer)

    def p_text(self, p):
        '''text : top text
                | top'''
        p[0] = '\n\n'.join(p[1:])

    def p_top(self, p):
        '''top : sentence
               | def-macro
               | macro'''
        p[0] = p[1]

    def p_sentence(self, p):
        '''sentence : symbols terminator'''
        p[0] = p[1] + p[2]

    def p_terminator(self, p):
        '''terminator : DOT
                      | QMARK'''
        p[0] = p[1]

    def p_symbols(self, p):
        '''symbols : SYMBOL symbols
                   | SYMBOL'''
        p[0] = ' '.join(p[1:])

    def p_defmacro(self, p):
        '''def-macro : DEFMACRO SYMBOL COLON ops COLON presymbols DOT'''
        self.macros[p[2]] = Macro(p[2], p[4], p[6])
        p[0] = ''

    def p_ops(self, p):
        '''ops : op ops
               | op'''
        if len(p) == 3:
            p[0] = p[2] + [p[1]]
        else:
            p[0] = [p[1]]

    def p_op(self, p):
        '''op :  DOLLAR SYMBOL'''
        p[0] = p[2]

    def p_macro(self, p):
        '''macro : MACRO SYMBOL COLON substitutions DOT'''
        macro = self.macros[p[2]]
        pat = macro.sentence
        for op in macro.ops:
            pat = pat.replace('$' + op, '%(' + op + ')s')
        p[0] = (pat % p[4]) + '.'

    def p_substitutions(self, p):
        '''substitutions : substitution substitutions
                         | substitution'''
        if len(p) == 3:
            p[2].update(p[1])
            p[0] = p[2]
        else:
            p[0] = p[1]

    def p_substitution(self, p):
        '''substitution : DOLLAR SYMBOL symbols DOLLAR'''
        p[0] = {p[2]: p[3]}

    def p_presymbols(self,p):
        '''presymbols : presymbol presymbols
                      | presymbol'''
        p[0] = ' '.join(p[1:])

    def p_presymbol(self, p):
        '''presymbol : DOLLAR SYMBOL
                     | SYMBOL
                     | COLON'''
        if len(p) == 3:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

    def p_error(self, p):
        print 'syntax error: ' + str(p)
