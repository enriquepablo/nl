from nl import *
from people import *
from modality import *
from cms3 import *


class Project(Thing):
    """
    """

class Component(Content):
    """
    A component belongs to a project,
    and can have subcomponents, features, and errors.
    It is a Content type, so it can have workflow
    """

class Milestone(Content):
    """
    A milestone has a due date,
    and can have components, features, and errors.
    It is a Content type, so it can have workflow
    """

class Open(WfAction):
    """
    A Component can be opened to current
    """

class Close(WfAction):
    """
    A Component can be closed to closed
    """

class Works(Exists):
    """
    A person can work on some content: Error, feature, component
    """
    subject = Person
    mods = {'on': Content}


boss = Role('boss')
developer = Role('developer')
qaboss = Role('qaboss')
qateam = Role('qateam')

current = Status('current')
closed = Status('closed')
# duplicate = Status('duplicate')
# invalid = Status('invalid')


class Server(Thing):
    """
    A server corresponds to some service in some address,
    and has one branch installed.
    And speaks some protocol
    """

class Protocol(Thing):
    """
    Corresponds to some communication protocol
    """

class Branch(Thing):
    """
    A project can have any number of branches,
    as can be installed in one or more Servers.
    """

class Changeset(Thing):
    """
    a Changeset corresponds to a changeset :)
    """

class Merge(Exists):
    """
    a person can merge some changeset into some branch
    """
    subject = Person
    mods = {'what': Changeset,
            'where': Branch}

class Test(Exists):
    """
    a person can merge some changeset into some branch
    """
    subject = Person
    mods = {'what': Ticket,
            'where': Server}

class Ticket(Content):
    """
    A ticket can be in one or more servers,
    A changeset can affect one (or more) tickets
    A ticket can be open or closed or accepted for merging any associated 
    It can be owned by any number of people,
    at least a developer and a qateam.
    """

class Error(Ticket):
    """
    An error can be in one or more servers,
    A changeset can affect one (or more) errors
    An error can be open or closed or accepted for merge
    It can be owned by any number of people,
    at least a developer and a qateam.
    """

class Feature(Ticket):
    """
    A changeset can affect some feature.
    A feature can be open or closed or accepted for merge
    """

class Affects(Exists):
    """
    something can affect something
    """
    subject = Thing
    mods = {'affected': Thing}


################################
# RULES
################################


# A ticket is current (in some server)
# And a server doesn't have that ticket neither current nor closed
# ->
# A qateam person with the less tickets has to review it on that server

Rule([
      Fact(Ticket('Ticket1'), Has(what=open), Instant('Instant1')),
      Not(Fact(Ticket('Ticket1'), Has(where=Server('Server1')), Instant('Instant1'))),
      Fact(Person('Person1'), Has(what=qateam), Instant('Instant1')),
      Arith('=', Count(Fact(Person('Person1'), Owns(what=Ticket('Ticket1')), Instant('Instant1')))
                 MinCount(('Person2',), Fact(Person('Person2'), Owns(what=Ticket('Ticket2')), Instant('Instant1')))),
     ],[
      Fact(Person('Person1'), Must(do=Test(what=Ticket('Ticket1'), where=Server('Server1'))), Duration(Instant('Instant1'), 'now')),
     ])

# A ticket is open
# and no developer owns it
# ->
# The boss has to give that ticket to some one
# (or: I ask the boss to whom do we give the ticket -> hook a notification)

Rule([
      Fact(Ticket('Ticket1'), Has(what=current), Instant('Instant1')),
      Fact(Person('Person3'), Has(what=boss), Instant('Instant1')),
      Not(And(Fact(Person('Person1'), Has(what=developer), Instant('Instant1')),
              Fact(Person('Person2'), Owns(what=Ticket('Ticket2')), Instant('Instant1')))),
    ],[
      Fact(Person('Person3'), Must(do=Give(what=Ticket('Ticket1'))), Duration(Instant('Instant1'), 'now')),
    ])

# A server has an open ticket
# and another server has it closed
# and a changeset that affects that ticket
# has been merged to the branch in the second but not to the one in the first
# ->
# The boss has to apply it in the first
# (or: I merge the changeset an update -> hook a script to do it and notify the boss)

Rule([
      Fact(Person('Person1'), Has(what=boss), Instant('Instant1')),
      Fact(Ticket('Ticket1'), Has(what=open, where=Server('Server1')), Instant('Instant1')),
      Fact(Server('Server1'), Has(what=Branch('Branch1')), Instant('Instant1')),
      Fact(Ticket('Ticket1'), Has(what=closed, where=Server('Server2')), Instant('Instant1')),
      Fact(Server('Server2'), Has(what=Branch('Branch2')), Instant('Instant1')),
      Fact(Changeset('Changeset1'), Affects(what=Ticket('Ticket1')), Instant('Instant1')),
      Fact(Person('Person1'), Merge(what=Changeset('Changeset1'), where=Branch('Branch2')), Instant('Instant2')),
      Not(Fact(Person('Person1'), Merge(what=Changeset('Changeset1'), where=Branch('Branch1')), Instant('Instant2'))),
    ],[
      Fact(Person('Person1'), Must(do=Merge(what=Changeset('Changeset1'), where=Branch('Branch1'))), Duration(Instant('Instant1'), 'now')),
    ])

# A server has a current ticket
# and another has it closed
# and the number of changesets that affect that ticket applied in each branch is the same
# ->
# a qateam person has to test that ticket in the first server

Rule([
      Fact(Ticket('Ticket1'), Has(what=open, where=Server('Server1')), Instant('Instant1')),
      Fact(Server('Server1'), Has(what=Branch('Branch1')), Instant('Instant1')),
      Fact(Ticket('Ticket1'), Has(what=closed, where=Server('Server2')), Instant('Instant1')),
      Fact(Server('Server2'), Has(what=Branch('Branch2')), Instant('Instant1')),
      Fact(Person('Person1'), Has(what=boss), Instant('Instant1')),
      Arith('=', Count(Fact(Person('Person1'), Merge(what=Changeset('Changeset1'), where=Branch('Branch1')), Instant('Instant2')),
                       Fact(Changeset('Changeset1'), Affects(what=Ticket('Ticket1')), Instant('Instant2'))),
                 Count(Fact(Person('Person1'), Merge(what=Changeset('Changeset1'), where=Branch('Branch2')), Instant('Instant2')),
                       Fact(Changeset('Changeset1'), Affects(what=Ticket('Ticket1')), Instant('Instant2')))),
      Fact(Person('Person2'), Has(what=qateam), Instant('Instant1')),
      Arith('=', Count(Fact(Person('Person2'), Owns(what=Ticket('Ticket1')), Instant('Instant1')))
                 MinCount(('Person3'), Fact(Person('Person3'), Owns(what=Ticket('Ticket2')), Instant('Instant1')))),
     ],[
      Fact(Person('Person2'), Must(do=Test(what=Ticket('Ticket1'), where=Server('Server1'))), Duration(Instant('Instant1'), 'now')),
     ])

