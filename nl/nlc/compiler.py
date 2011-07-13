"""
satatement = sentence, QMARK;

statement = sentence, DOT;

sentence = fact;

sentence = copula;

copula = SYMBOL, ISA, SYMBOL;

fact = VAR, predicate, time;

fact = SYMBOL, predicate, time;

fact = VAR, VAR, time;

fact = SYMBOL, VAR, time;

time = AT instant;

time = FROM instant TILL instant;

instant = TIME;

instant = NOW;

instant = VAR;

predicate = SYMBOL, items;

items = modifier, items;

items = modifier;

items = ;

modifier = SYMBOL, VAR, COMMA;

modifier = SYMBOL, SYMBOL, COMMA;

modifier = SYMBOL, predicate, COMMA;

modifier = SYMBOL, NUMBER, COMMA;
"""
import re
import nl
import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from nl.nlc.lexer import tokens

VAR_PAT = re.compile(r'^([A-Z][a-zA-Z]+)(\d+)$')

precedence = (
    ('left', 'COMMA'),
        )

# UTILS

def _from_var(var):
    match = VAR_PAT.match(var)
    cls = nl.utils.get_class(match.group(1))
    return cls(var)

# BNF

def p_question(p):
    'statement : sentence QMARK'
    response = nl.kb.ask(p[1])
    p[0] = str(response)

def p_assertion(p):
    'statement : sentence DOT'
    response = nl.kb.tell(p[1])
    p[0] = str(response)

def p_sentence_fact(p):
    'sentence : fact'
    p[0] = p[1]

def p_sentence_copula(p):
    'sentence : copula'
    p[0] = p[1]

def p_copula(p):
    'copula : SYMBOL ISA SYMBOL'
    cls = nl.utils.get_class(p[3].capitalize())
    p[0] = cls(p[1])

def p_fact_var_pred(p):
    'fact : VAR predicate time'
    p[0] = nl.Fact(_from_var(p[1]), p[2], p[3])

def p_fact_symbol_pred(p):
    'fact : SYMBOL predicate time'
    p[0] = nl.Fact(*(p[1:]))

def p_fact_var_var(p):
    'fact : VAR VAR time'
    p[0] = nl.Fact(_from_var(p[1]), _from_var(p[2]), p[3])

def p_fact_symbol_var(p):
    'fact : SYMBOL VAR time'
    p[0] = nl.Fact(p[1], _from_var(p[2]), p[3])

def p_time_instant(p):
    'time : AT instant'
    p[0] = p[2]

def p_time_duration(p):
    'time : FROM instant TILL instant'
    p[0] = nl.Duration(start=p[2], end=p[4])

def p_instant_time(p):
    'instant : TIME'
    p[0] = nl.Instant(p[1])

def p_instant_now(p):
    'instant : NOW'
    p[0] = nl.Instant('now')

def p_time_var(p):
    'instant : VAR'
    p[0] = _from_var(p[1])

def p_predicate(p):
    'predicate : SYMBOL items'
    cls = nl.utils.get_class(p[1].capitalize())
    kwargs = p[2] and dict(p[2]) or {}
    p[0] = cls(**kwargs)
 
def p_items(p):
    'items : modifier items'
    p[0] = [p[1]] + p[2]
 
#def p_items_one(p):
#    'items : modifier'
#    p[0] = [p[1]]
 
def p_items_empty(p):
    'items :'
    pass
 
def p_modifier_symbol(p):
    'modifier : SYMBOL SYMBOL COMMA'
    thing = nl.kb.ask_obj(nl.Thing(p[2]))[0]
    p[0] = (p[1], thing)

def p_modifier_var(p):
    'modifier : SYMBOL VAR COMMA'
    p[0] = (p[1], _from_var(p[2]))

def p_modifier_pred(p):
    'modifier : SYMBOL predicate COMMA'
    p[0] = (p[1], p[2])

def p_modifier_number(p):
    'modifier : SYMBOL NUMBER COMMA'
    p[0] = (p[1], int(p[2]))


# Error rule for syntax errors
def p_error(p):
    print "Syntax error!! ",p

# Build the parser
# Use this if you want to build the parser using SLR instead of LALR
# yacc.yacc(method="SLR")
yacc.yacc()
