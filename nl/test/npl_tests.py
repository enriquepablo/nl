import os
import re
import nl
from nl.log import logger
from nl.conf import here
from nl.test.functional_test import reset


def test_npl(): # test generator
    # read contents of npl/
    # feed each content to run_npl
    d = os.path.join(here, 'npl_tests')
    files = os.listdir(d)
    for f in files:
        if f.endswith('.npl'):
            reset()
            yield run_npl, os.path.join(d, f)


def run_npl(fname):
    # open file, read lines
    # tell asserions
    # compare return of questions with provided output
    with open(fname) as f:
        resp, buff = None, ''
        for sen in f.readlines():
            logger.info(sen)
            sen = sen.strip('\n ')
            if resp is not None:
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
