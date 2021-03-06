import nl
from nl.log import logger

def reset():
    logger.info('\n\n\n---------RESET-----------\n\n\n')
    nl.clps.clips.Reset()
    nl.clps.clips.Clear()
    reload(nl.clps.clips)
    reload(nl.clps)
    reload(nl.metanl)
    reload(nl.nltime)
    reload(nl.thing)
    reload(nl.state)
    reload(nl.prop)
    reload(nl.rule)
    reload(nl.kb)
    reload(nl)


class cms_test(object):
    def setup(self):
        from nl.examples import cms2
        self.cms = cms2

    def teardown(self):
        reset()
        del self.cms

    def third_test(self):
        nl.nltime.now()
        # john is a person
        john = self.cms.Person('john')
        # pete is a person
        pete = self.cms.Person('pete')
        # jane is a person
        jane = self.cms.Person('jane')
        # c1 is a content
        c1 = self.cms.Content('c1')
        # c2 is a content
        c2 = self.cms.Content('c2')
        # john has role manager
        p1 = nl.Fact(john, self.cms.Has(what=self.cms.manager), self.cms.Duration(start=self.cms.Instant('now')))
        # jane has create_perm
        p2 = nl.Fact(jane, self.cms.Has(what=self.cms.create_perm), self.cms.Duration(start=self.cms.Instant('now')))
        # jane wants to create c1
        p3 = nl.Fact(jane, self.cms.Wants(to=self.cms.Create(what=c1)), self.cms.Instant('now'))
        # pete wants to create c2
        p4 = nl.Fact(pete, self.cms.Wants(to=self.cms.Create(what=c2)), self.cms.Instant('now'))
        # input everything into the db
        nl.kb.tell(john, pete, jane, c1, c2, p1, p2, p3, p4)
        # to the question is jane owner of c1?, the answer is no
        assert not nl.kb.ask(nl.Fact(jane, self.cms.Is_owner(of=c1), self.cms.Duration(start=self.cms.Instant('now'))))
        # extend the db
        nl.kb.extend()
        nl.nltime.now()
        # to the question is jane owner of c1?, the answer is yes
        assert nl.kb.ask(nl.Fact(jane, self.cms.Is_owner(of=c1), self.cms.Duration(start=self.cms.Instant('now'))))
        # to the question has c1 private state?, the answer is yes
        assert nl.kb.ask(nl.Fact(c1, self.cms.Has(what=self.cms.private), self.cms.Duration(start=self.cms.Instant('now'))))
        # to the question is pete owner of c2?, the answer is no
        assert not nl.kb.ask(nl.Fact(pete, self.cms.Is_owner(of=c2), self.cms.Duration(start=self.cms.Instant('now'))))
        # jane wants to publish c1
        nl.kb.tell(nl.Fact(jane, self.cms.Wants(to=self.cms.Publish(what=c1)), self.cms.Instant('now')))
        # pete wants to publish c2
        nl.kb.tell(nl.Fact(pete, self.cms.Wants(to=self.cms.Publish(what=c2)), self.cms.Instant('now')))
        # extend the db
        nl.kb.extend()
        nl.nltime.now()
        # to the question is c1 public?, the answer is no
        assert not nl.kb.ask(nl.Fact(c1, self.cms.Has(what=self.cms.public), self.cms.Duration(start=self.cms.Instant('now'))))
        # to the question is c2 public?, the answer is no
        assert not nl.kb.ask(nl.Fact(c2, self.cms.Has(what=self.cms.public), self.cms.Duration(start=self.cms.Instant('now'))))
        # to the question can jane view c1?, the answer is yes
        assert nl.kb.ask(nl.Fact(jane, self.cms.Can(what=self.cms.View(what=c1)), self.cms.Duration(start=self.cms.Instant('now'))))
        assert nl.kb.ask(nl.Fact(jane, self.cms.Can(what=self.cms.View('View1')), self.cms.Duration(start=self.cms.Instant('now'))))
        assert nl.kb.ask(nl.Fact(self.cms.admin, self.cms.Can(what=self.cms.Publish(what='Content1')), self.cms.Duration(start=self.cms.Instant('now'))))
        #assert len(nl.kb.ask(nl.Fact(self.cms.admin, self.cms.Can('X1'), self.cms.Duration(start=self.cms.Instant('now'))), nl.Fact(jane, self.cms.Can('X1'), self.cms.Duration(start=self.cms.Instant('now'))))) == 1
        # to the question can pete view c1?, the answer is no
        assert not nl.kb.ask(nl.Fact(pete, self.cms.Can(what=self.cms.View(what=c1)), self.cms.Duration(start=self.cms.Instant('now'))))
        # john wants to publish c1
        nl.kb.tell(nl.Fact(john, self.cms.Wants(to=self.cms.Publish(what=c1)), self.cms.Instant('now')))
        # extend the db
        nl.kb.extend()
        nl.nltime.now()
        # to the question is c1 private?, the answer is no
        assert not nl.kb.ask(nl.Fact(c1, self.cms.Has(what=self.cms.private), nl.Duration(start=nl.Instant('now'))))
        # to the question is c1 public?, the answer is yes
        assert nl.kb.ask(nl.Fact(c1, self.cms.Has(what=self.cms.public), nl.Duration(start=nl.Instant('now'))))
        # to the question can pete view c1?, the answer is yes
        assert nl.kb.ask(nl.Fact(pete, self.cms.Can(what=self.cms.View(what=c1)), nl.Duration(start=nl.Instant('now'))))

        # what can pete view? -> c1
        assert nl.kb.ask(self.cms.Content('Content1'), nl.Fact(pete, self.cms.Can(what=self.cms.View(what='Content1')), nl.Duration(start=nl.Instant('now')))) == [{'Content1': 'c1'}]

        # who can view what?
        assert nl.kb.ask(self.cms.Content('Content1'), self.cms.Person('Person1'), nl.Fact(self.cms.Person('Person1'), self.cms.Can(what=self.cms.View(what='Content1')), nl.Duration(start=nl.Instant('now')))) == [{'Person1': 'admin', 'Content1': 'c1'}, {'Person1': 'john', 'Content1': 'c1'}, {'Person1': 'pete', 'Content1': 'c1'}, {'Person1': 'jane', 'Content1': 'c1'}]

        # c2 is private
        nl.kb.tell(nl.Fact(c2, self.cms.Has(what=self.cms.private), nl.Duration(start=nl.Instant('now'))))
        nl.kb.extend()
        nl.nltime.now()

        # who can view what?
        assert nl.kb.ask(self.cms.Content('Content1'), self.cms.Person('Person1'), nl.Fact(self.cms.Person('Person1'), self.cms.Can(what=self.cms.View(what='Content1')), nl.Duration(start=nl.Instant('now')))) == [{'Person1': 'admin', 'Content1': 'c1'}, {'Person1': 'john', 'Content1': 'c1'}, {'Person1': 'pete', 'Content1': 'c1'}, {'Person1': 'jane', 'Content1': 'c1'}, {'Person1': 'admin', 'Content1': 'c2'}, {'Person1': 'john', 'Content1': 'c2'}]

        # who can hide what?
        assert nl.kb.ask(self.cms.Content('Content1'), self.cms.Person('Person1'), nl.Fact(self.cms.Person('Person1'), self.cms.Can(what=self.cms.Hide(what='Content1')), nl.Duration(start=nl.Instant('now')))) == [{'Person1': 'admin', 'Content1': 'c1'}, {'Person1': 'john', 'Content1': 'c1'}, {'Person1': 'jane', 'Content1': 'c1'}]

        # how many permissions has admin?
        assert len(nl.kb.ask(self.cms.Permission('Permission2'), nl.Fact(self.cms.admin, self.cms.Has(what=self.cms.Permission('Permission2')), nl.Duration(start=nl.Instant('Instant3'))))) == 3

        # can admin view c2?
        assert nl.kb.ask(nl.Fact(self.cms.admin, self.cms.Can(what=self.cms.View(what=c2)), nl.Duration(start=nl.Instant('now'))))

        assert nl.kb.ask(nl.Duration('Duration1'),
                             nl.Fact(c2,
                                 self.cms.Has(what=self.cms.private),
                                 nl.Duration('Duration1')))
        # john wants to publish c1
        nl.kb.tell(nl.Fact(john, self.cms.Wants(to=self.cms.Hide(what=c1)), self.cms.Instant('now')))
        # extend the db
        nl.kb.extend()
        nl.nltime.now()

        assert nl.kb.ask(nl.Fact(c1, self.cms.Has(what=self.cms.private), nl.Duration(start=nl.Instant('now'))))
        assert not nl.kb.ask(nl.Fact(c1, self.cms.Has(what=self.cms.public), nl.Duration(start=nl.Instant('now'))))
        assert not nl.kb.ask(nl.Fact(pete, self.cms.Can(what=self.cms.View(what=c1)), nl.Duration(start=nl.Instant('now'))))
        assert not nl.kb.ask(nl.Fact(pete, self.cms.Can(what=self.cms.View(what=c1)), nl.Duration('Duration1')))
        # who can view what?
        assert nl.kb.ask(self.cms.Person('Person1'), nl.Fact(self.cms.Person('Person1'), self.cms.Can(what=self.cms.View(what=c1)), nl.Instant('now'))) == [{'Person1': 'admin'}, {'Person1': 'john'}, {'Person1': 'jane'}]

        #import os
        #from nl.log import log_dir, log_file
        #os.remove(log_file)
        #os.rmdir(log_dir)


class cms3_test(object):
    def setup(self):
        nl.nltime.now()
        from nl.examples import cms3
        self.cms = cms3
        nl.nltime.now()
        nl.nltime.now()
        nl.nltime.now()

    def teardown(self):
        reset()
        del self.cms

    def _add_context(self, context):
        nl.kb.tell(self.cms.Context(context))

    def _add_content(self, content, status, context):
        nl.kb.tell(self.cms.Document(content),
                   nl.Fact(self.cms.Content(content),
                           self.cms.Has(what=self.cms.Status(status)),
                           nl.Duration(start=nl.Instant('now'))),
                   nl.Fact(self.cms.Content(content),
                           self.cms.Located(where=self.cms.Context(context)),
                           nl.Duration(start=nl.Instant('now'))))

    def _add_user(self, user, role, context):
        nl.kb.tell(self.cms.Person(user),
                   nl.Fact(self.cms.Person(user),
                           self.cms.Has(what=self.cms.Role(role),
                                        where=self.cms.Context(context)),
                           nl.Duration(start=nl.Instant('now'))))

    def cms_test(self):
        contexts = ('one', 'two', 'three')
        for c in contexts:
            self._add_context(c)
        self.cms.r_workflow_for_content(self.cms.Document,
                                        self.cms.doc_workflow,
                                        self.cms.Context('one'))
        for n in xrange(0, 10, 3):
            for m, c in enumerate(contexts):
                self._add_content('cpu%d' % (n+m), 'public', c)
        for n in xrange(0, 10, 3):
            for m, c in enumerate(contexts):
                self._add_content('cpr%d' % (n+m), 'private', c)
        for n in xrange(0, 50, 3):
            for m, c in enumerate(contexts):
                self._add_user('m%d' % (n+m), 'manager', c)
        for n in xrange(0, 10, 3):
            for m, c in enumerate(contexts):
                self._add_user('e%d' % (n+m), 'editor', c)
        for n in xrange(0, 30, 3):
            for m, c in enumerate(contexts):
                self._add_user('u%d' % (n+m), 'member', c)

        nl.kb.tell(nl.Fact(self.cms.Person('m3'),
                           self.cms.Wants(
                                   to=self.cms.Publish(
                                             what=self.cms.Content('cpr3'))),
                           self.cms.Instant('now')))
        nl.clips.Eval('(dribble-on "clipstrace")')
        nl.clips.Eval('(watch instances)')

        nl.kb.extend()
        assert nl.kb.ask(nl.Fact(self.cms.Person('m3'),
                                 self.cms.Publish(what=self.cms.Content('cpr3')),
                                 nl.Instant('now')))
        nl.clips.Eval('(unwatch all)')
        nl.clips.Eval('(dribble-off)')
        assert nl.kb.ask(nl.Fact(self.cms.Document('cpr3'),
                                 self.cms.Has(what=self.cms.Status('public')),
                                 nl.Duration(start=nl.Instant('now'))))

        nl.now()

        nl.kb.tell(nl.Fact(self.cms.Person('m3'),
                           self.cms.Wants(
                                   to=self.cms.Hide(
                                             what=self.cms.Content('cpu3'))),
                           self.cms.Instant('now')))

        nl.kb.extend()

        assert nl.kb.ask(nl.Fact(self.cms.Document('cpu3'),
                                 self.cms.Has(what=self.cms.Status('private')),
                                 nl.Instant('now')))

        nl.now()

        nl.kb.tell(nl.Fact(self.cms.Person('m6'),
                           self.cms.Wants(
                                   to=self.cms.Publish(
                                             what=self.cms.Content('cpu3'))),
                           self.cms.Instant('now')))

        nl.kb.extend()

        assert nl.kb.ask(nl.Fact(self.cms.Person('m6'),
                                 self.cms.Publish(what=self.cms.Content('cpu3')),
                                 nl.Instant('now')))

        assert nl.kb.ask(nl.Fact(self.cms.Document('cpu3'),
                                 self.cms.Has(what=self.cms.Status('public')),
                                 nl.Instant('now')))

        main_view = self.cms.Action_step('main_view')
        main_edit = self.cms.Action_step('main_edit')
        button_edit = self.cms.Action_step('button_edit')
        nl.kb.tell(main_view, main_edit, button_edit)

        nl.kb.tell(nl.Fact(self.cms.Edit,
                           self.cms.Contains(
                                   what=main_edit),
                           self.cms.Duration(start='now')))

        nl.kb.tell(nl.Fact(self.cms.View,
                           self.cms.Contains(
                                   what=main_view),
                           self.cms.Duration(start='now')))

        nl.kb.tell(nl.Fact(main_view,
                           self.cms.Has(
                                   what=button_edit),
                           self.cms.Duration(start='now')))

        nl.kb.tell(nl.Fact(self.cms.Person('m6'),
                           self.cms.Wants(to=self.cms.View(
                                             what=self.cms.Content('cpu3'))),
                           self.cms.Instant('now')))

        nl.kb.extend()

        assert nl.kb.ask(nl.Fact(self.cms.Person('m6'),
                           self.cms.Has(what=button_edit),
                           self.cms.Instant('now')))

        assert not nl.kb.ask(nl.Fact(self.cms.Person('m6'),
                           self.cms.Has(what=main_edit),
                           self.cms.Instant('now')))


#class physics_test(object):
#    def setup(self):
#        from nl.examples import physics22
#        self.p = physics22
#
#    def teardown(self):
#        reset()
#        del self.p
#
#    def first_test(self):
#        fact = nl.kb.ask_obj(nl.Fact(self.p.Body('c1'), self.p.Has_position(x='X2', y='X3'), 50))
#        assert str(fact[0]) == 'c1 hasposition y 57.641201061 x -65.0657847679 at 50.0'
#        resp = nl.kb.ask_obj(nl.Fact(self.p.c1, self.p.Has_position(x='X1', y='X2'), 'X3'))
#        assert len(resp) == 100
#
#
class noun_test(object):
    def setup(self):
        from nl.examples import nouns
        self.n = nouns

    def teardown(self):
        reset()
        del self.n

    def first_test(self):
        john = self.n.Person('john')
        nl.kb.tell(john)
        nl.kb.tell(nl.Fact(john, self.n.Wants(what=self.n.Eats)))
        nl.kb.extend()
        assert nl.kb.ask(nl.Fact(john, self.n.Tries(what=self.n.Eats)))
        assert nl.kb.ask(nl.Fact(john, self.n.Tries(what=nl.Verb('EatsVerb1', self.n.Eats))))
        assert nl.kb.ask(nl.Fact(john, self.n.Wants(what=nl.Verb('EatsVerb1', self.n.Eats))), nl.Fact(john, self.n.Tries(what=nl.Verb('EatsVerb1', self.n.Eats))))
        nl.kb.tell(nl.Fact(john, self.n.Wanting(what=self.n.Eating(what=self.n.b1))))
        nl.kb.extend()
        assert nl.kb.ask(nl.Fact(john, self.n.Eating(what=self.n.b1)))
        assert nl.kb.ask(nl.Fact(john, self.n.Feels(what=self.n.Eating(what=self.n.b1))))
        assert nl.kb.ask(nl.Fact(john, self.n.Smelling(what=self.n.b1)))


class multi_test(object):
    def setup(self):
        from nl.examples import multi
        self.m = multi

    def teardown(self):
        reset()
        del self.m

    def first_test(self):
        assert nl.kb.ask(nl.Fact(self.m.dos, self.m.Uno_verb(to=self.m.tre)))
        assert not nl.kb.ask(nl.Fact(self.m.tre, self.m.Uno_verb(to=self.m.dos)))
        nl.kb.extend()
        assert nl.kb.ask(nl.Fact(self.m.tre, self.m.Uno_verb(to=self.m.dos)))
        assert nl.kb.ask(nl.Fact(self.m.tre, self.m.Tre_verb(to=self.m.dos)))
        assert nl.kb.ask(nl.Fact(self.m.dos, self.m.Dos_verb(to=self.m.uno)))
        assert nl.kb.ask(nl.Fact(self.m.dos, self.m.Tre_verb(to=self.m.uno)))
