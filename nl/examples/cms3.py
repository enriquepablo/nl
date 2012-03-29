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

from nl.log import logger
from nl import (Noun, Verb, Number, Thing, Exists, Fact, Rule,
                Subword, Duration, Instant, During, Coincide,
                Intersection, Finish, Max_end, Min_end, kb)
from people import Person
from modality import Wants, Can, Must

admin = Person('admin')
kb.tell(admin)

anonymous = Person('anonymous')
kb.tell(anonymous)

class Role(Thing):
    """
    The name role, for roles that can be had in contexts by people,
    and have some associated permissions
    """

member = Role('member')
kb.tell(member)

editor = Role('editor')
kb.tell(editor)

manager = Role('manager')
kb.tell(manager)

class Context(Thing):
    """
    content can be located in some context
    """

basic_context = Context('basic_context')
kb.tell(basic_context)

class Has(Exists):
    """
    a thing can have other things in a certain context
    """
    subject = Thing
    mods = {'what': Thing,
            'where': Context}

# admin is a manager in the basic context from now on
kb.tell( Fact(admin, Has(what=manager, where=basic_context), Duration(start='now')) )

class Permission(Thing):
    """
    a permission that can protect some action on some context
    """

view_perm = Permission('view_perm')
kb.tell(view_perm)

edit_perm = Permission('edit_perm')
kb.tell(edit_perm)

manage_perm = Permission('manage_perm')
kb.tell(manage_perm)

def p_role_has_perm(role, perm):
    """
    Role role has permission perm from now on
    """
    kb.tell( Fact(role, Has(what=perm), Duration(start='now')) )

p_role_has_perm(member, view_perm)

p_role_has_perm(editor, view_perm)

p_role_has_perm(editor, edit_perm)

p_role_has_perm(manager, view_perm)

p_role_has_perm(manager, edit_perm)

p_role_has_perm(manager, manage_perm)

class Content(Thing):
    """
    a content object
    """

class Located(Exists):
    """
    a thing can be located in some context
    """
    subject = Thing
    mods = {'where': Context}

class Status(Thing):
    """
    content objects have a status
    """

public = Status('public')
kb.tell(public)

private = Status('private')
kb.tell(private)

class Action(Exists):
    """
    an abstract action over a content
    """
    subject = Person
    mods = {'what': Content}

class View(Action):
    """
    a person can view some content
    """

class Edit(Action):
    """
    a person can edit some content
    """

class Wf_action(Action):
    """
    abstract workflow action on some content
    """

class Publish(Wf_action):
    """
    a person can publish some content
    """

class Hide(Wf_action):
    """
    a person can hide some content
    """

class Workflow(Thing):
    """
    a content type can have a workflow in a context
    """

class Required(Exists):
    """
    an abstract action over a content
    """
    subject = Permission
    mods = {'to': Verb,
            'over': Status}

#If a person wants to perform a certain action on a content object,
#and that object is in some context and has a certain status,
#and the person has some role on that context,
#and that permission is required to perform that kind of action over an object with that certain status,
#and that role has that permission,
#all at the same time,
#the person performs the given action
try:
  kb.tell(Rule([
     Fact(Permission('Permission1'), Required(to=Verb('ActionVerb1', Action), over=Status('Status1')), Duration('Duration1')),
     Fact(Person('Person1'), Wants(to=Verb('ActionVerb1', Action)(what=Content('Content1'))), Instant('Instant1')),
     Fact(Content('Content1'), Has(what=Status('Status1')), Duration('Duration5')),
     Fact(Content('Content1'), Located(where=Context('Context1')), Duration('Duration2')),
     Fact(Person('Person1'), Has(what=Role('Role1'), where=Context('Context1')), Duration('Duration3')),
     Fact(Role('Role1'), Has(what=Permission('Permission1')), Duration('Duration4')),
     During('Instant1', 'Duration1','Duration2','Duration3','Duration4', 'Duration5')
 ],[
     Fact(Person('Person1'), Verb('ActionVerb1', Action)(what=Content('Content1')), Instant('Instant1'))]))
except:
    import clips
    logger.info(clips.ErrorStream.Read())
    raise

kb.tell( Fact(view_perm, Required(to=View, over=public), Duration(start='now', end='now')) )

def r_permission(action, status, perm):
    """
    """
    kb.tell( Fact(perm, Required(to=action, over=status), Duration(start='now', end='now')) )

r_permission(Edit, public, edit_perm)

r_permission(Hide, public, manage_perm)

r_permission(View, private, manage_perm)

r_permission(Edit, private, manage_perm)

r_permission(Publish, private, manage_perm)

#def r_transition(action, workflow, initial, final):
#    """
#    If a person performs a workflow action on a content object,
#    and that object has the intitial status up till that moment,
#    from now on it has status final
#    """
#    kb.tell( Rule([
#        Fact(Person('P1'), action(what=Content('C1')), Instant('I1')),
#        Fact(Content('C1'), Has(what=initial), Duration('T1')),
#        Fact(Content('C1'), Has(what=workflow), Duration('T2')),
#        During('I1', 'T1','T2')
#    ],[
#        Fact(Content('C1'), Has(what=final), Duration(start=Instant('I1'), end=Min_end('T1', 'T2'))),
#        Finish('T1', 'I1')]))
#
def r_workflow_for_content(content_type, workflow, context):
    """
    assign workflow to content_type in context
    """
    kb.tell( Fact(workflow, Assigned(to=content_type, where=context), Duration(start=Instant('now'))))



class Assigned(Exists):
    """
    an abstract action over a content
    """
    subject = Workflow
    mods = {'to': Noun,
            'where': Context}

class Has_transition(Exists):
    subject = Workflow
    mods = {'start': Status,
            'end': Status,
            'by': Verb} #Wf_action

#if some workflow has some transition,
#and that workflow is assigned to some content type in some context,
#and a person performs the workflow action of the transition on a content object of thet type,
#and the mentioned content object is located in the mentioned context,
#and that object has the intitial status of the transtion up till that moment,
#from now on it has status final
#and no longer has status initial.

try:
  kb.tell(Rule([
    Fact(Workflow('Workflow1'), Has_transition(start=Status('Status1'), end=Status('Status2'), by=Verb('Wf_actionVerb1', Wf_action)), Duration('Duration1')),
    Fact(Workflow('Workflow1'), Assigned(to=Noun('ContentNoun1', Content), where=Context('Context1')), Duration('Duration2')),
    Fact(Noun('ContentNoun1', Content)('Content1'), Located(where=Context('Context1')), Duration('Duration3')),
    Fact(Person('Person1'), Verb('Wf_actionVerb1', Wf_action)(what=Noun('ContentNoun1', Content)('Content1')), Instant('Instant1')),
    Fact(Noun('ContentNoun1', Content)('Content1'), Has(what=Status('Status1')), Duration('Duration4')),
    During('Instant1', 'Duration3','Duration2', 'Duration4', 'Duration1')
],[
    Fact(Noun('ContentNoun1')('Content1'), Has(what=Status('Status2')), Duration(start=Instant('Instant1'), end='now')),
    Finish('Duration4', 'Instant1')]))
except:
   import clips
   logger.info(clips.ErrorStream.Read())



def r_transition(action, workflow, initial, final):
    """

    """
    kb.tell( Fact(workflow, Has_transition(start=initial, end=final, by=action), Duration(start='now', end='now')) )



#def r_transition(action, workflow, content_type, initial, final):
#    """
#    If a person performs a workflow action on a content object,
#    and that object has the intitial status up till that moment,
#    and that workflow is assigned to the type of the object in the context in which it is,
#    from now on it has status final
#
#    Note: The usage of Noun here is merely for testing purposes,
#    the rule would be simpler substituting Noun('N1', content_type) for content_type
#    """
#    kb.tell( Rule([
#        Fact(workflow, Assigned(to=Noun('N1', content_type), where=Context('X1')), Duration('T2')),
#        Fact(Noun('N1', content_type)('C1'), Located(where=Context('X1')), Duration('T1')),
#        Fact(Person('P1'), action(what=Noun('N1', content_type)('C1')), Instant('I1')),
#        Fact(Noun('N1', content_type)('C1'), Has(what=initial), Duration('T3')),
#        During('I1', 'T1','T2', 'T3')
#    ],[
#        Fact(Noun('N1', content_type)('C1'), Has(what=final), Duration(start=Instant('I1'), end=Min_end('T1', 'T2'))),
#        Finish('T3', 'I1')]))


class Document(Content):
    """
    a document
    """

doc_workflow = Workflow('doc_workflow')
kb.tell(doc_workflow)

r_workflow_for_content(Document, doc_workflow, basic_context)

r_transition(Publish, doc_workflow, private, public)

r_transition(Hide, doc_workflow, public, private)

class Owns(Exists):
    """
    a person can own some content
    """
    subject = Person
    mods = {'what': Content}

def r_owner_can_action(action):
    """
    The owner of a content can perform the given action on the content
    """
    kb.tell( Rule([
        Fact(Person('Person1'), Wants(to=action(what=Content('Content1'))), Instant('Instant1')),
        Fact(Person('Person1'), Owns(what=Content('Content1')), Duration('Duration1')),
        During('Instant1','Duration1')
    ],[
        Fact(Person('Person1'), action(what=Content('Content1')), Instant('Instant1'))]))

r_owner_can_action(View)

r_owner_can_action(Edit)

r_owner_can_action(Hide)


class Give(Exists):
    """
    a person can give some content to someone else
    """
    subject = Person
    mods = {'what': Content,
            'whom': Person}

# if someone wants to give some content to someone else, and owns the content,
# then he gives it to her
# and she owns it from then on
kb.tell(Rule([
        Fact(Person('Person1'), Wants(to=Give(what=Content('Content1'), whom=Person('Person2'))), Instant('Instant1')),
        Fact(Person('Person1'), Owns(what=Content('Content1')), Duration('Duration1')),
        During('Instant1', 'Duration1')
    ],[
        Fact(Person('Person1'), Give(what=Content('Content1'), whom=Person('Person2')), Instant('Instant1')),
        Fact(Person('Person2'), Owns(what=Content('Content1')), Duration(start=Instant('Instant1'))),
        Finish('Duration1', 'Instant1')]))


# ACTION STEPS

class Action_step(Thing): pass

class Contains(Exists):
    subject = Verb
    mods = {'what': Thing,
            'pos': Number}

# try:
kb.tell(Rule([
    Subword(Verb('ActionVerb1'), Action),
    Fact(Person('Person1'), Verb('ActionVerb1')('Action1'), Instant('Instant1')),
    Fact(Verb('ActionVerb1'), Contains(what=Action_step('Action_step1')), Duration('Duration1')),
    During('Instant1', 'Duration1')
],[
    Fact(Person('Person1'), Has(what=Action_step('Action_step1')), Instant('Instant1')),
]))
# except:
#     import clips
#    logger.info(clips.ErrorStream.Read())


kb.tell(Rule([
    Fact(Thing('Thing1'), Has(what=Action_step('Action_step1')), Instant('Instant1')),
    Fact(Action_step('Action_step1'), Has(what=Action_step('Action_step2')), Duration('Duration1')),
    During('Instant1', 'Duration1')
],[
    Fact(Thing('Thing1'), Has(what=Action_step('Action_step2')), Instant('Instant1')),
]))

