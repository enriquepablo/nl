"""
"""
import re
import urllib2
from collections import defaultdict
import nl
import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from nl.nlc.lexer import tokens, t_VAR, t_NUMBER

def shut_up_pyflakes():
    return tokens


class CompileError(Exception): pass
class ParseError(Exception): pass

VAR_PAT = re.compile(t_VAR)
NUM_PAT = re.compile(t_NUMBER)

SPECIAL_VARS = {
    re.compile(r'^I(\d+)$'): 'Instant',
    re.compile(r'^D(\d+)$'): 'Duration',
    re.compile(r'^O(\d+)$'): 'Duration',
    re.compile(r'^N(\d+)$'): 'Number',
}

precedence = (
    ('left', 'COMMA'),
    ('left', 'LBRACK'),  )

# UTILS

def _from_var(var):
    for pat, name in SPECIAL_VARS.items():
        m = pat.match(var)
        if m:
            var = name + m.group(1)
            break
    m = VAR_PAT.match(var)
    name = m.group(1)
    try:
        cls = nl.utils.get_class(name)
    except KeyError:
        raise CompileError('invalid variable name: ' + var)
    if m.group(2):
        return nl.metanl.ClassVar(var, cls)
    return cls(var)

# BNF

def p_sentence(p):
    '''sentence : statement
                | question
                | order'''
    p[0] = p[1]

def p_extend(p):
    'order : EXTEND DOT'
    response = nl.kb.extend()
    p[0] = str(response)

def p_passtime(p):
    '''order : PASSTIME DOT
             | NOW DOT'''
    response = nl.now()
    p[0] = str(response)

def p_import(p):
    'order : IMPORT URI DOT'
    uri = p[2][1:-1]
    try:
        remote = urllib2.urlopen(uri)
    except Exception, e:
        raise ImportError('Could not import %s. '
                          'Reason: %s' % (uri, str(e)))
    buff = ''
    for sen in remote.readlines():
        sen = sen.strip()
        if sen and not sen.startswith('#'):
            buff += ' ' + sen
            if buff.endswith('.'):
                yacc.parse(buff)
                buff = ''
    p[0] = 'Contents of %s imported' % uri


def p_question(p):
    '''question : fact QMARK
                | definition QMARK'''
    response = nl.kb.ask_obj(p[1])
    if response:
        resp = []
        for r in response:
            resp.append(getattr(r, 'sen_tonl', r.tonl)())
        p[0] = '; '.join(resp)
    else:
        p[0] = str(nl.kb.ask(p[1]))

def p_assertion(p):
    '''statement : definition DOT
                 | fact DOT
                 | rule DOT'''
    if isinstance(p[1], basestring):
        # name-defs already told
        response = p[1]
    else:
        response = nl.kb.tell(p[1])
    p[0] = str(response)

def p_fact(p):
    '''fact : truth
            | NOT truth'''
    if p[1] == 'not':
        p[2].truth = 0
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_truth(p):
    '''truth : subject predicate
             | subject predicate time'''
    try:
        p[0] = nl.Fact(*p[1:])
    except ValueError, e:
        raise CompileError(e.args[0])

def p_subject(p):
    '''subject : TERM
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
            | ONWARDS
            | INTERSECTION durations
            | SINCE instant ONWARDS
            | SINCE instant TILL instant
            | SINCE instant UNTIL durations
            | UNTIL durations'''
    if p[1] == 'now':
        p[0] = nl.Instant('now')
    elif VAR_PAT.match(p[1]):
        var = _from_var(p[1])
        if not isinstance(var, nl.Duration):
            raise CompileError('invalid variable name for duration: %s' % p[1])
        p[0] = var
    elif p[1] == 'at':
        p[0] = p[2]
    elif p[1] == 'onwards':
        p[0] = nl.Duration(start='now', end='now')
    elif p[1] == 'since':
        if p[3] == 'onwards':
            p[0] = nl.Duration(start=p[2], end='now')
        elif p[3] == 'till':
            p[0] = nl.Duration(start=p[2], end=p[4])
        elif p[3] == 'until':
            p[0] = nl.Duration(start=p[2], end=nl.Min_end(*p[4]))
    elif p[1] == 'intersection':
        p[0] = nl.Intersection(*p[2])
    elif p[1] == 'until':
        p[0] = nl.Duration(start='now', end=nl.Min_end(*p[2]))

def p_instant(p):
    '''instant : arith
               | VAR
               | NOW
               | MAXSTART durations
               | MINEND durations'''
    if p[1] == 'maxstart':
        p[0] = nl.Max_end(*p[2])
    elif p[1] == 'minend':
        p[0] = nl.Min_end(*p[2])
    else:
        if isinstance(p[1], basestring) and VAR_PAT.match(p[1]):
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
            try:
                if not isinstance(verb.cls, nl.Verb):
                    raise CompileError(
                         'not a valid variable name for a verb: ' + p[2])
            except AttributeError:
                raise CompileError('you should use a verb variable(with "Verb"'
                                   ' in it) rather than a predicate variable')
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
    '''verb : TERM'''
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
    '''modifier : TERM object'''
    p[0] = {p[1]: p[2]}
    
 
def p_object(p):
    '''object : TERM
              | arith
              | VAR
              | predicate
              | varvar'''
    if isinstance(p[1], basestring):
        if VAR_PAT.match(p[1]):
            p[0] = _from_var(p[1])
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
    'noun-def : TERM ARE terms'
    superclasses = []
    for noun in p[3]:
        try:
            superclass = nl.utils.get_class(noun)
        except KeyError:
            raise CompileError('unknown name for noun: ' + noun)
        if not issubclass(superclass, nl.Thing):
            raise CompileError('this is not a noun: ' + noun)
        superclasses.append(superclass)
    name = p[1].capitalize()
    try:
        cls = nl.Noun(name, bases=tuple(superclasses), newdict={})
    except ValueError:
        raise CompileError('ilegal name for noun: ' % (p[1]))
    p[0] = 'Noun %s defined.' % name
 
def p_terms(p):
    '''terms : TERM COMMA terms
             | TERM'''
    _terms(p)

def _terms(p):
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]

def p_name_def(p):
    '''name-def : TERM ISA TERM
                | VAR ISA TERM'''
    if isinstance(p[1], basestring):
        if VAR_PAT.match(p[1]):
            p[0] = _from_var(p[1])
        else:
            try:
                cls = nl.utils.get_class(p[3])
            except KeyError:
                raise CompileError('unknown noun: %s' % p[3])
            p[0] = cls(p[1])
    else:
        p[0] = p[1]

def p_verb_def(p):
    '''verb-def : A TERM CAN TERM LPAREN verbs RPAREN modification-def
                | A TERM CAN TERM modification-def
                | A TERM CAN TERM LPAREN verbs RPAREN'''
    superclasses = []
    newdict = {}
    if len(p) == 6:
        superclasses.append(nl.Exists)
        newdict['mods'] = p[5]
    else:
        for v in p[6]:
            try:
                superclass = nl.utils.get_class(v)
            except KeyError:
                raise CompileError('unknown name for verb: ' + v)
            if not issubclass(superclass, nl.Exists):
                raise CompileError('this is not a verb: ' + v)
            superclasses.append(superclass)
    try:
        nclass = nl.utils.get_class(p[2])
    except KeyError:
        raise CompileError('unknown word for subject: ' + p[2])
    newdict['subject'] = nclass
    if len(p) == 9:
        newdict['mods'] = p[8]
    name = p[4].capitalize()
    vclass = nl.Verb(name, bases=tuple(superclasses), newdict=newdict)
    p[0] = 'Verb %s defined.' % name
 
def p_verbs(p):
    '''verbs : verb COMMA verbs
             | verb'''
    _terms(p)

def p_modification_def(p):
    '''modification-def : mod-def COMMA modification-def
                        | mod-def'''
    if len(p) == 4:
        p[1].update(p[3])
    p[0] = p[1]

def p_mod_def(p):
    'mod-def : TERM A TERM'
    try:
        typ = nl.utils.get_class(p[3])
    except KeyError:
        raise CompileError('unknown type for modifier: ' + p[3])
    name = nl.kb.get_symbol(p[1])
    if not isinstance(name, basestring):
        prev = name.__class__.__name__.lower()
        raise CompileError('bad label for modifier, already a %s: %s' + (prev,
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
                 | subword
                 | arith-condition
                 | distinct-condition'''
    p[0] = p[1]

def p_coincidence(p):
    'coincidence : COINCIDE durations'
    p[0] = nl.Coincide(*p[2])

def p_durations(p):
    '''durations : VAR COMMA durations
                 | VAR'''
    newd = _from_var(p[1])
    if not isinstance(newd, nl.Duration):
        raise CompileError('bad name for duration variable: ' + p[1])
    if len(p) == 4:
        p[3].append(newd)
        p[0] = p[3]
    else:
        p[0] = [newd]

def p_during(p):
    '''during : instant DURING durations'''
    p[0] = nl.During(p[1], *p[3])

def p_subword(p):
    '''subword : TERM SUBWORDOF TERM
               | TERM SUBWORDOF VAR
               | VAR SUBWORDOF TERM
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
    '''end-duration : FINISH VAR
                    | FINISH VAR NOW
                    | FINISH VAR AT instant'''
    dur = _from_var(p[2])
    if not isinstance(dur, nl.Duration):
        raise CompileError('not a valid variable name for a duration: ' % p[3])
    if len(p) in (3, 4):
        p[0] = nl.Finish(dur, nl.Instant('now'))
    else:
        p[0] = nl.Finish(dur, p[4])


# Arithmetics

def p_arith(p):
    '''arith : NUMBER
             | LCURL arith-operation RCURL'''
    if len(p) == 2:
        p[0] = nl.Number(p[1])
    else:
        p[0] = p[2]

def p_arith_operation(p):
    '''arith-operation : arith-operand arith-operator arith-operation
                       | arith-operand arith-operator arith-operand'''
    p[0] = nl.Number(p[2], arg1=p[1], arg2=p[3])

def p_arith_operand(p):
    '''arith-operand : NUMBER
                     | VAR
                     | LPAREN arith-operation RPAREN'''
    if len(p) == 4:
        p[0] = p[2]
    elif VAR_PAT.match(p[1]):
        p[0] = _from_var(p[1])
    else:
        p[0] = nl.Number(p[1])

def p_arith_operator(p):
    '''arith-operator : PLUS
                      | MINUS
                      | PRODUCT
                      | DIVISION'''
    p[0] = p[1]

def p_arith_condition(p):
    '''arith-condition : LCURL arith-predication RCURL'''
    p[0] = p[2]

def p_arith_predication(p):
    '''arith-predication : arith-operand arith-predicate arith-operand'''
    p[0] = nl.Arith(p[2], arg1=p[1], arg2=p[3])

def p_arith_predicate(p):
    '''arith-predicate : LT
                       | GT
                       | EQ
                       | NEQ'''
    p[0] = p[1]


def p_distinct_condition(p):
    '''distinct-condition : DISTINCT objects'''
    p[0] = nl.Distinct(*p[2])

def p_objects(p):
    '''objects : object COMMA objects
               | object'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

# Error rule for syntax errors
def p_error(p):
    raise ParseError('syntax error: ' + str(p))

# Build the parser
# Use this if you want to build the parser using SLR instead of LALR
# yacc.yacc(method="SLR")
yacc.yacc()


# To print the grammar #
########################

def print_grammar():
    grammar = defaultdict(list)
    rules = []
    gused = set()
    for name, obj in globals().items():
        if name.startswith('p_'):
            if not getattr(obj, '__doc__', False):
                continue
            rule, defs = [o.strip() for o in obj.__doc__.split(':')]
            defs = [d.strip().split(' ') for d in  defs.split('|')]
            used = []
            for d in defs:
                for n in d:
                    if n.islower():
                        used.append(n)
            grammar[rule] += defs
            grammar[rule + 'used'] += used
            gused = gused.union(set(used))
    first = None
    for rule in grammar:
        if not rule.endswith('used') and rule not in gused:
            first = rule
            break
    ruleprint(first, grammar[first])
    printrule(first, grammar, set())

def printrule(rule, grammar, done):
    spawn = []
    for r in grammar[rule + 'used']:
        if r not in done:
            done.add(r)
            ruleprint(r, grammar[r])
            spawn.append(r)
    for r in spawn:
        printrule(r, grammar, done)

def ruleprint(name, defs):
    try:
        print '    ', name, ' : ', ' '.join(defs[0])
        for d in defs[1:]:
            print '    ', ' ' * len(name), ' | ', ' '.join(d)
    except IndexError:
        print '    ', name
    print '\n'
