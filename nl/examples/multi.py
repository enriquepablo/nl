import nl


class Uno_verb(nl.Exists):
    subject = nl.Thing
    mods = {'to': nl.Thing}

r1 = nl.Rule([
        nl.Fact(nl.Thing('Thing1'), nl.Verb('Uno_verb1', Uno_verb)(to=nl.Thing('Thing2'))),
        ],[
        nl.Fact(nl.Thing('Thing2'), nl.Verb('Uno_verb1', Uno_verb)(to=nl.Thing('Thing1'))),
        ])

class Dos_verb(nl.Exists):
    subject = nl.Thing
    mods = {'to': nl.Thing}

uno = nl.Thing('uno')

r2 = nl.Rule([
        nl.Fact(nl.Thing('Thing1'), nl.Verb('Dos_verb1', Dos_verb)(to=nl.Thing('Thing2'))),
        ],[
        nl.Fact(nl.Thing('Thing1'), nl.Verb('Dos_verb1', Dos_verb)(to=uno)),
        ])

dos = nl.Thing('dos')
tre = nl.Thing('tre')

class Tre_verb(Uno_verb, Dos_verb): pass

f1 = nl.Fact(dos, Tre_verb(to=tre))

nl.kb.tell(r1, uno, r2, dos, tre, f1)
