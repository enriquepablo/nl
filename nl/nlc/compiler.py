"""
"""
import re
import nl
import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from nl.nlc.lexer import tokens, t_VAR, t_NUMBER

def shut_up_pyflakes():
    return tokens


class CompileError(Exception): pass

VAR_PAT = re.compile(t_VAR)
NUM_PAT = re.compile(t_NUMBER)

precedence = (
    ('left', 'COMMA'),
    ('left', 'LBRACK'),  )

# UTILS

def _from_var(var):
    m = VAR_PAT.match(var)
    name = m.group(1)
    try:
        cls = nl.utils.get_class(name)
    except KeyError:
        raise CompileError('invalid variable name: ' + name)
    if m.group(2):
        return nl.metanl.ClassVar(var, cls)
    return cls(var)

# BNF

def p_extend(p):
    'statement : EXTEND DOT'
    response = nl.kb.extend()
    p[0] = str(response)

def p_passtime(p):
    'statement : PASSTIME DOT'
    response = nl.now()
    p[0] = str(response)

def p_question(p):
    'statement : fact QMARK'
    response = nl.kb.ask_obj(p[1])
    if response:
        resp = []
        for r in response:
            resp.append(getattr(r, 'sen_tonl', r.tonl)())
        p[0] = '; '.join(resp)
    else:
        p[0] = str(nl.kb.ask(p[1]))

def p_assertion(p):
    '''statement : fact DOT
                 | rule DOT'''
    response = nl.kb.tell(p[1])

    p[0] = str(response)

def p_definition(p):
    'statement : definition DOT'
    response = p[1]
    p[0] = str(response)

def p_fact(p):
    '''fact : subject predicate
            | subject predicate time'''
    if len(p) == 3:
        args = (p[1], p[2])
    else:
        args = (p[1], p[2], p[3])
    try:
        p[0] = nl.Fact(*args)
    except ValueError, e:
        raise CompileError(e.args[0])

def p_subject(p):
    '''subject : SYMBOL
               | VAR
               | varvar'''
    if isinstance(p[1], basestring):
        if VAR_PAT.match(p[1]):
            p[0] = _from_var(p[1])
        else:
            sym = nl.kb.get_symbol(p[1])
            if isinstance(sym, basestring):
                raise CompileError('unknown word for subject: %s' % sym)
            p[0] = p[1]
    else:
        p[0] = p[1]

def p_time(p):
    '''time : NOW
            | VAR
            | AT instant
            | FROM instant ONWARDS
            | FROM instant TILL instant
            | INTERSECTION durations'''
    if p[1] == 'now':
        p[0] = nl.Instant('now')
    elif VAR_PAT.match(p[1]):
        var = _from_var(p[1])
        if not isinstance(var, nl.Duration):
            raise CompileError('invalid variable name for duration: %s' % p[1])
        p[0] = nl.Duration(p[1])
    elif p[1] == 'at':
        p[0] = p[2]
    elif p[1] == 'from':
        if p[3] == 'onwards':
            p[0] = nl.Duration(start=p[2], end='now')
        else:
            p[0] = nl.Duration(start=p[2], end=p[4])
    elif p[1] == 'intersection':
        p[0] = nl.Intersection(*p[2])

def p_instant(p):
    '''instant : TIME
               | VAR
               | NOW
               | MAXSTART durations
               | MINEND durations'''
    if p[1] == 'maxstart':
        p[0] = nl.Max_end(*p[2])
    elif p[1] == 'minend':
        p[0] = nl.Min_end(*p[2])
    else:
        if VAR_PAT.match(p[1]):
            var = _from_var(p[1])
            if not isinstance(var, nl.Instant):
                raise CompileError('invalid variable name for instant: %s' % p[1])
            p[0] = var
        else:
            p[0] = nl.Instant(p[1])

def p_predicate(p):
    '''predicate : LBRACK verb modification RBRACK
                 | LBRACK VAR modification RBRACK
                 | LBRACK VAR VAR RBRACK
                 | LBRACK verb RBRACK
                 | LBRACK VAR RBRACK'''
    if len(p) == 5:
        if isinstance(p[2], basestring) and VAR_PAT.match(p[2]):
            verb = _from_var(p[2])
            if not isinstance(verb.cls, nl.Exists):
                raise CompileError(
                     'not a valid variable name for a verb: ' + p[2])
            if isinstance(p[3], basestring) and VAR_PAT.match(p[3]):
                pred = _from_var(p[3])
                if not isinstance(pred, nl.Exists):
                    raise CompileError(
                         'not a valid variable name for a predicate: ' + p[3])
                try:
                    p[0] = verb(p[3])
                except ValueError, e:
                    raise CompileError(e.args[0])
            else:
                try:
                    p[0] = verb(**p[3])
                except ValueError, e:
                    raise CompileError(e.args[0])
        else:
            try:
                p[0] = p[2](**p[3])
            except ValueError, e:
                raise CompileError(e.args[0])
    else:
        if isinstance(p[2], basestring) and VAR_PAT.match(p[2]):
            pred = _from_var(p[2])
            if not isinstance(pred, nl.Exists):
                raise CompileError(
                     'not a valid variable name for a predicate: ' + p[2])
            p[0] = pred
        else:
            try:
                p[0] = p[2]()
            except ValueError, e:
                raise CompileError(e.args[0])

def p_verb(p):
    '''verb : SYMBOL'''
    try:
        verb = nl.utils.get_class(p[1])
    except KeyError:
        raise CompileError('unknown verb: ' + p[1])
    if not issubclass(verb, nl.Exists):
        raise CompileError('not a verb: ' + p[1])
    p[0] = verb
 
def p_modification(p):
    '''modification : modifier COMMA modification
                    | modifier'''
    if len(p) == 4:
        p[1].update(p[3])
    p[0] = p[1]
 
def p_modifier(p):
    '''modifier : SYMBOL object'''
    p[0] = {p[1]: p[2]}
    
 
def p_object(p):
    '''object : SYMBOL
              | NUMBER
              | VAR
              | predicate
              | varvar'''
    if isinstance(p[1], basestring):
        if VAR_PAT.match(p[1]):
            p[0] = _from_var(p[1])
        elif NUM_PAT.match(p[1]):
            p[0] = nl.Number(p[1])
        else:
            obj = nl.kb.get_symbol(p[1])
            if isinstance(obj, basestring):
                raise CompileError('unknown word: ' + p[1])
            p[0] = obj
    else:
        p[0] = p[1]

def p_varvar(p):
    'varvar :  VAR LPAREN VAR RPAREN'
    m = VAR_PAT.match(p[1])
    try:
        cls = nl.utils.get_class(m.group(1))
    except KeyError:
        raise CompileError('invalid variable name for a proper name: ' + p[1])
    m = VAR_PAT.match(p[3])
    try:
        cls = nl.utils.get_class(m.group(1))
    except KeyError:
        raise CompileError('invalid variable name for a noun, '
                           'unknown symbol %s: %s' % (m.group(1).lower(), p[3]))
    else:
        if not issubclass(cls, nl.Thing):
            raise CompileError('invalid variable name for a noun, '
                               '%s are not thing: %s' % (m.group(1).lower(),
                                                         p[3]))
        if not m.group(2):
            raise CompileError('invalid variable name for a noun, '
                               '%s are not noun: %s' % (m.group(1).lower(),
                                                         p[3]))
    p[0] = nl.metanl.ClassVarVar(p[3], cls, p[1])

def p_def(p):
    '''definition : noun-def
                  | name-def
                  | verb-def'''
    p[0] = p[1]

def p_noun_def(p):
    'noun-def : SYMBOL ARE SYMBOL'
    try:
        superclass = nl.utils.get_class(p[3])
    except KeyError:
        raise CompileError('unknown name for noun: ' + p[3])
    else:
        if not issubclass(superclass, nl.Thing):
            raise CompileError('this is not a noun: ' + p[3])
    metaclass = superclass.__metaclass__
    name = p[1].capitalize()
    try:
        cls = metaclass(name, bases=(superclass,), newdict={})
    except ValueError:
        raise CompileError('ilegal name for noun: ' % (p[1]))
    nl.utils.register(name, cls)
    p[0] = 'Noun %s defined.' % name

def p_name_def(p):
    'name-def : SYMBOL ISA SYMBOL'
    try:
        cls = nl.utils.get_class(p[3])
    except KeyError:
        raise CompileError('unknown noun: %s' % p[3])
    p[0] = cls(p[1])

def p_verb_def(p):
    '''verb-def : SYMBOL IS SYMBOL WITHSUBJECT SYMBOL ANDCANBE modification-def
                | SYMBOL IS SYMBOL WITHSUBJECT SYMBOL
                | SYMBOL IS SYMBOL ANDCANBE modification-def
                | SYMBOL IS SYMBOL'''
    try:
        superclass = nl.utils.get_class(p[3])
    except KeyError:
        raise CompileError('unknown name for verb: ' + p[3])
    else:
        if not issubclass(superclass, nl.Exists):
            raise CompileError('this is not a verb: ' + p[3])
    metaclass = superclass.__metaclass__
    newdict = {}
    if len(p) > 4 and p[4] != 'andcanbe':
        try:
            nclass = nl.utils.get_class(p[5])
        except KeyError:
            raise CompileError('unknown word for subject: ' + p[5])
        newdict['subject'] = nclass
    if len(p) == 6 and p[4] == 'andcanbe':
        newdict['mods'] = p[5]
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
        p[1].update(p[3])
    p[0] = p[1]

def p_mod_def(p):
    'mod-def : SYMBOL A SYMBOL'
    try:
        typ = nl.utils.get_class(p[3])
    except KeyError:
        raise CompileError('unknown word for modifier: ' + p[3])
    name = nl.kb.get_symbol(p[1])
    if not isinstance(name, basestring):
        prev = name.__class__.__name__.lower()
        raise CompileError('bad name for modifier, already a %s: %s' + (prev,
                                                                        p[1]))
    p[0] = {name: typ}

def p_rule(p):
    'rule : IF COLON conditions SEMICOLON THEN COLON consecuences'
    try:
        p[0] = nl.Rule(p[3], p[7])
    except ValueError, e:
        raise CompileError(e.args[0])

def p_conditions(p):
    '''conditions : conditions SEMICOLON condition
                  | condition'''
    if len(p) == 4:
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = [p[1]]

def p_condition(p):
    '''condition : fact
                 | name-def
                 | coincidence
                 | during
                 | subword'''
    p[0] = p[1]

def p_coincidence(p):
    'coincidence : COINCIDE durations'
    p[0] = nl.Coincide(*p[2])

def p_durations(p):
    '''durations : durations COMMA VAR
                 | VAR COMMA VAR'''
    if isinstance(p[1], list):
        newd = _from_var(p[3])
        if not isinstance(newd, nl.Duration):
            raise CompileError('bad name for duration variable: ' + p[3])
        p[1].append(newd)
        p[0] = p[1]
    else:
        durs = {1: _from_var(p[1]), 3: _from_var(p[3])}
        for k, d in durs.items():
            if not isinstance(d, nl.Duration):
                raise CompileError('bad name for duration variable: ' + p[k])
        p[0] = durs.values()

def p_during(p):
    '''during : instant DURING durations
              | instant DURING VAR'''
    if isinstance(p[3], basestring) and VAR_PAT.match(p[3]):
        dur = _from_var(p[3])
        if not isinstance(dur, nl.Duration):
            raise CompileError(
                         'not a valid variable name for a duration: ' % p[3])
        p[0] = nl.During(p[1], dur)
    else:
        p[0] = nl.During(p[1], *p[3])

def p_subword(p):
    '''subword : SYMBOL SUBWORDOF SYMBOL
               | SYMBOL SUBWORDOF VAR
               | VAR SUBWORDOF SYMBOL
               | VAR SUBWORDOF VAR'''
    if VAR_PAT.match(p[1]):
        p1 = _from_var(p[1])
    else:
        try:
            p1 = nl.utils.get_class(p[1])
        except KeyError:
            raise CompileError('unknown word in variable: ' + p[1])
    if VAR_PAT.match(p[3]):
        p2 = _from_var(p[3])
    else:
        try:
            p2 = nl.utils.get_class(p[2])
        except KeyError:
            raise CompileError('unknown word in variable: ' + p[2])
    if not issubclass(p1.__class__, p2.__class__):
        raise CompileError('do not be absurd, you know %s can not '
                           'be a subword of %s' % (p[1], p[3]))
    p[0] = nl.Subword(p1, p2)

def p_consecuences(p):
    '''consecuences : consecuences SEMICOLON consecuence
                    | consecuence'''
    if len(p) == 4:
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = [p[1]]

def p_consecuence(p):
    '''consecuence : fact
                   | end-duration'''
    p[0] = p[1]

def p_end_duration(p):
    '''end-duration : ENDDURATION VAR NOW
                  | ENDDURATION VAR AT instant'''
    dur = _from_var(p[2])
    if not isinstance(dur, nl.Duration):
        raise CompileError('not a valid variable name for a duration: ' % p[3])
    if p[3] == 'now':
        p[0] = nl.Finish(dur, nl.Instant('now'))
    else:
        p[0] = nl.Finish(dur, p[4])

# Error rule for syntax errors
def p_error(p):
    print "Syntax error!! ",p

# Build the parser
# Use this if you want to build the parser using SLR instead of LALR
# yacc.yacc(method="SLR")
yacc.yacc()
