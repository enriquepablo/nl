"""
statement : EXTEND DOT | sentence QMARK | sentence DOT | definition DOT

sentence : fact | copula

copula : SYMBOL ISA SYMBOL

fact : subject predicate time

subject : SYMBOL | VAR

time : NOW | AT instant | FROM instant TILL instant

instant : TIME | VAR | NOW

predicate : predication | VAR

predication : LPAREN v_verb modification RPAREN | LPAREN v_verb RPAREN

v_verb : SYMBOL | VAR

modification : modifier COMMA modification | modifier

modifier :  SYMBOL object

object : SYMBOL | NUMBER | pred | VAR

definition : noun-def | verb-def

noun-def : SYMBOL ARE SYMBOL

verb-def : SYMBOL IS SYMBOL WITHSUBJECT SYMBOL ANDCANBE modification-def | SYMBOL IS SYMBOL WITHSUBJECT SYMBOL

modification-def : mod-def COMMA modification-def | mod-def

mod-def : SYMBOL A SYMBOL
"""
import re
import nl
import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from nl.nlc.lexer import tokens, t_VAR, t_NUMBER

def shut_up_pyflakes():
    return tokens

VAR_PAT = re.compile(t_VAR)
NUM_PAT = re.compile(t_NUMBER)

precedence = (
    ('left', 'COMMA'),
        )

# UTILS

def _from_var(var):
    match = VAR_PAT.match(var)
    cls = nl.utils.get_class(match.group(1))
    return cls(var)

# BNF

def p_extend(p):
    'statement : EXTEND DOT'
    response = nl.kb.extend()
    p[0] = str(response)

def p_question(p):
    'statement : sentence QMARK'
    response = nl.kb.ask(p[1])
    p[0] = str(response)

def p_assertion(p):
    'statement : sentence DOT'
    response = nl.kb.tell(p[1])
    p[0] = str(response)

def p_definition(p):
    'statement : definition DOT'
    response = p[1]
    p[0] = str(response)

def p_sentence(p):
    '''sentence : fact
                | copula'''
    p[0] = p[1]

def p_copula(p):
    'copula : SYMBOL ISA SYMBOL'
    cls = nl.utils.get_class(p[3].capitalize())
    p[0] = cls(p[1])

def p_fact(p):
    'fact : subject predicate time'
    p[0] = nl.Fact(p[1], p[2], p[3])

def p_subject(p):
    '''subject : SYMBOL
               | VAR'''
    if VAR_PAT.match(p[1]):
        p[0] = _from_var(p[1])
    else:
        p[0] = p[1]

def p_time(p):
    '''time : NOW
            | AT instant
            | FROM instant TILL instant'''
    if p[1] == 'now':
        p[0] = nl.Instant('now')
    elif p[1] == 'at':
        p[0] = nl.Instant(p[2])
    elif p[1] == 'from':
        p[0] = nl.Duration(start=p[2], end=p[4])

def p_instant(p):
    '''instant : TIME
               | VAR
               | NOW'''
    p[0] = nl.Instant(p[1])

def p_predicate(p):
    '''predicate : predication
                 | VAR'''
    if VAR_PAT.match(p[1]):
        p[0] = _from_var(p[1])
    else:
        p[0] = p[1]

def p_predication(p):
    '''predication : LPAREN v_verb modification RPAREN
                   | LPAREN v_verb RPAREN'''
    if p[3] == ']':
        p[0] = p[2]()
    else:
        p[0] = p[2](**p[3])

def p_v_verb(p):
    '''v_verb : SYMBOL
              | SYMBOL VAR'''
    if VAR_PAT.match(p[1]):
        p[0] = _from_var(p[1])
    else:
        p[0] = nl.utils.get_class(p[1])
 
def p_modification(p):
    '''modification : modifier COMMA modification
                    | modifier'''
    if len(p) == 4:
        p[0] = p[1].update(p[3])
    else:
        p[0] = p[1]
 
def p_modifier(p):
    'modifier :  SYMBOL object'
    p[0] = {p[1]: p[2]}
    
 
def p_object(p):
    '''object : SYMBOL
              | NUMBER
              | predication
              | VAR'''
    if VAR_PAT.match(p[1]):
        p[0] = _from_var(p[1])
    elif NUM_PAT.match(p[1]):
        p[0] = nl.Number(p[1])
    else:
        p[0] = p[1]

def p_def(p):
    '''definition : noun-def
                  | verb-def'''
    p[0] = p[1]

def p_noun_def(p):
    'noun-def : SYMBOL ARE SYMBOL'
    superclass = nl.utils.get_class(p[3].capitalize())
    metaclass = superclass.__metaclass__
    name = p[1].capitalize()
    cls = metaclass(name, bases=(superclass,), newdict={})
    nl.utils.register(name, cls)
    p[0] = 'Noun %s defined.' % name

def p_verb_def(p):
    '''verb-def : SYMBOL IS SYMBOL WITHSUBJECT SYMBOL ANDCANBE modification-def
                | SYMBOL IS SYMBOL WITHSUBJECT SYMBOL'''
    superclass = nl.utils.get_class(p[3].capitalize())
    metaclass = superclass.__metaclass__
    nclass = nl.utils.get_class(p[5].capitalize())
    newdict = {'subject': nclass}
    if len(p) == 8:
        newdict['mods'] = p[7]
    name = p[1].capitalize()
    vclass = metaclass(name, bases=(superclass,), newdict=newdict)
    nl.utils.register(name, vclass)
    p[0] = 'Verb %s defined.' % name

def p_modification_def(p):
    '''modification-def : mod-def COMMA modification-def
                        | mod-def'''
    if len(p) == 4:
        p[0] = p[1].update(p[3])
    else:
        p[0] = p[1]

def p_mod_def(p):
    'mod-def : SYMBOL A SYMBOL'
    obj = nl.utils.get_class(p[3].capitalize())
    p[0] = {p[1]: obj}


# Error rule for syntax errors
def p_error(p):
    print "Syntax error!! ",p

# Build the parser
# Use this if you want to build the parser using SLR instead of LALR
# yacc.yacc(method="SLR")
yacc.yacc()
