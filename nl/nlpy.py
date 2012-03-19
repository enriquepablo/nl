import code, re


def main():
   from nl import *
   print "AVAILABLE:"
   print '\n'.join(['\t%s'%x for x in locals().keys()
                    if re.findall('[A-Z]\w+|db|con', x)])
   code.interact(local=locals())
