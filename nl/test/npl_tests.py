import os
import re
import nl
from nl.log import logger
from nl.conf import here
from nl.nlc.preprocessor import Preprocessor
from nl.test.functional_test import reset


def test_npl(): # test generator
    # read contents of npl/
    # feed each content to run_npl
    d = os.path.join(here, 'npl_tests')
    files = os.listdir(d)
#    yield run_npl, '/home/eperez/virtualenvs/ircbot/src/nl/nl/npl_tests/lists.npl'
    for f in files:
        if f.endswith('.npl'):
            reset()
            yield run_npl, os.path.join(d, f)


def run_npl(fname):
    # open file, read lines
    # tell asserions
    # compare return of questions with provided output
    with open(fname) as f:
        prep = Preprocessor().parse(f.read())
        resp, buff = None, ''
        for sen in prep.split('\n'):
            logger.info(sen)
            sen = sen.strip('\n ')
            if resp is not None:
                sen = sen.strip('.')
                logger.info('%s match %s' % (sen, resp))
                assert re.compile(sen).match(resp)
                resp = None
            elif sen and not sen.startswith('#'):
                buff += ' ' + sen
                if buff.endswith('.'):
                    logger.info(nl.yacc.parse(buff))
                    buff = ''
                elif buff.endswith('?'):
                    resp = nl.yacc.parse(buff)
                    buff = ''
