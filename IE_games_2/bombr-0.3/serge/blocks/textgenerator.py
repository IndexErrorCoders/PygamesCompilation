"""Implements a class to help with randomized text generation"""
# coding: utf-8

import random
import re

class NameNotFound(Exception): """An expansion for the name was not found"""


class TextGenerator(object):
    """Generate text from forms
    
    A form gives the possible values for something, for example the
    form for colour might give [red, green, blue].
    
    You can then convert sentences like 'the @colour@ book'
    
    Conversion can be hierarchical like:
        objects are [book, table, @{colour}@ cat]
        
    Sentence 'the @{object}@' would give a "book" or a "red cat".
    
    When looking up examples from text or files the form should be:
    
        type: example1
        type: example2
        
    Or
    
        type {
            example1
            example2
        }
    """
    
    def __init__(self):
        """Initialise the generator"""
        self.forms = {}
        
    def addExample(self, name, conversion):
        """Add a new form"""
        try:
            the_form = self.forms[name]
        except KeyError:
            the_form = set()
            self.forms[name] = the_form
        #
        the_form.add(conversion)

    def addExampleFromText(self, text):
        """Add an example from text - the name is ':' separated from the conversion"""
        parts = [i.strip() for i in text.strip().split(':', 1)]
        if len(parts) != 2:
            raise ValueError('Need ":" separated name and then conversion. Got [%s]' % (parts,))
        self.addExample(*parts)
    
    def addExamplesFromText(self, text):
        """Add a number of examples from text"""
        in_multiline = None
        for idx, full_line in enumerate(text.splitlines()):
            line = full_line.strip()
            if line and not line.startswith('#'):
                if line.endswith('{'):
                    # Multiple lines follow - store the name
                    parts = line.split(' ')
                    if len(parts) != 2:
                        raise ValueError('Need "<name> {" for multi-line (line %d:"%s")' % (idx, full_line))
                    in_multiline = parts[0].strip()
                elif line.endswith('}'):
                    # Multiple lines end
                    in_multiline = None
                else:
                    if not in_multiline:
                        self.addExampleFromText(line)
                    else:
                        self.addExample(in_multiline, line)
    
    def addExamplesFromFile(self, filename):
        """Add multiple examples from a file"""
        text = file(filename, 'r').read()
        self.addExamplesFromText(text)
                
    def getRandomFormCompletion(self, name, properties=None):
        """Return the comletion of a form randomly"""
        properties = {} if properties is None else properties
        try:
            results = self.forms[name]
        except KeyError:
            # No name found
            raise NameNotFound('The expansion @%s@ was not defined' % name)
        else:
            result = random.choice(list(results))
            if name not in properties:
                properties[name] = result
            return result
        
    def getRandomSentence(self, text, properties=None):
        """Return a random sentence from the text"""
        if properties is None:
            properties = {}
        match = re.match('(.*)@{(.+?)}@(.*)', text, re.DOTALL+re.M)
        if match:
            name = match.groups()[1]
            try:
                notfound = False
                replacement = properties[name]
            except KeyError:
                replacement = self.getRandomFormCompletion(name, properties)
            #
            result = self.getRandomSentence(
                match.groups()[0] + 
                replacement + 
                match.groups()[2], properties)
            return result
        else:
            return text

import random

# from http://www.geocities.com/anvrill/names/cc_goth.html
PLACES = ['Adara', 'Adena', 'Adrianne', 'Alarice', 'Alvita', 'Amara', 'Ambika', 'Antonia', 'Araceli', 'Balandria', 'Basha',
'Beryl', 'Bryn', 'Callia', 'Caryssa', 'Cassandra', 'Casondrah', 'Chatha', 'Ciara', 'Cynara', 'Cytheria', 'Dabria', 'Darcei',
'Deandra', 'Deirdre', 'Delores', 'Desdomna', 'Devi', 'Dominique', 'Drucilla', 'Duvessa', 'Ebony', 'Fantine', 'Fuscienne',
'Gabi', 'Gallia', 'Hanna', 'Hedda', 'Jerica', 'Jetta', 'Joby', 'Kacila', 'Kagami', 'Kala', 'Kallie', 'Keelia', 'Kerry',
'Kerry-Ann', 'Kimberly', 'Killian', 'Kory', 'Lilith', 'Lucretia', 'Lysha', 'Mercedes', 'Mia', 'Maura', 'Perdita', 'Quella',
'Riona', 'Safiya', 'Salina', 'Severin', 'Sidonia', 'Sirena', 'Solita', 'Tempest', 'Thea', 'Treva', 'Trista', 'Vala', 'Winta']


###############################################################################
# Markov Name model
# A random name generator, by Peter Corbett
# http://www.pick.ucam.org/~ptc24/mchain.html
# This script is hereby entered into the public domain
###############################################################################

class Mdict:
    def __init__(self):
        self.d = {}
    def __getitem__(self, key):
        if key in self.d:
            return self.d[key]
        else:
            raise KeyError(key)
    def add_key(self, prefix, suffix):
        if prefix in self.d:
            self.d[prefix].append(suffix)
        else:
            self.d[prefix] = [suffix]
    def get_suffix(self,prefix):
        l = self[prefix]
        return random.choice(l)


class MarkovNameGenerator(object):
    """
    A name from a Markov chain
    """
    def __init__(self, names, chainlen=2):
        """
        Building the dictionary
        """
        if chainlen > 10 or chainlen < 1:
            print "Chain length must be between 1 and 10, inclusive"
            sys.exit(0)

        self.mcd = Mdict()
        oldnames = []
        self.chainlen = chainlen

        for l in names:
            l = l.strip()
            oldnames.append(l)
            s = " " * chainlen + l
            for n in range(0,len(l)):
                self.mcd.add_key(s[n:n+chainlen], s[n+chainlen])
            self.mcd.add_key(s[len(l):len(l)+chainlen], "\n")

    def getName(self, max_length=9):
        """
        New name from the Markov chain
        """
        prefix = " " * self.chainlen
        name = ""
        suffix = ""
        while True:
            suffix = self.mcd.get_suffix(prefix)
            if suffix == "\n" or len(name) > max_length:
                break
            else:
                name = name + suffix
                prefix = prefix[1:] + suffix
        return name.capitalize()

EUROPE = [
    "Moscow",
    "LONDON",
    "St Petersburg",
    "BERLIN",
    "MADRID",
    "ROMA",
    "KIEV",
    "PARIS",
    "Bucharest",
    "BUDAPEST",
    "Hamburg",
    "MINSK",
    "Warsaw",
    "Belgrade",
    "Vienna",
    "Kharkov",
    "Barcelona",
    "Novosibirsk",
    "Nizhny Novgorod",
    "Milan",
    "Ekaterinoburg",
    "Munich",
    "Prague",
    "Samara",
    "Omsk",
    "SOFIA",
    "Dnepropetrovsk",
    "Kazan",
    "Ufa",
    "Chelyabinsk",
    "Donetsk",
    "Naples",
    "Birmingham",
    "Perm",
    "Rostov-na-Donu",
    "Odessa",
    "Volgograd",
    "Cologne",
    "Turin",
    "Voronezh",
    "Krasnoyarsk",
    "Saratov",
    "ZAGREB",
    "Zaporozhye",
    "Lódz",
    "Marseille",
    "RIGA",
    "Lvov",
    "Athens",
    "Salonika",
    "STOCKHOLM",
    "Kraków",
    "Valencia",
    "AMSTERDAM",
    "Leeds",
    "Tolyatti",
    "Kryvy Rig",
    "Sevilla",
    "Palermo",
    "Ulyanovsk",
    "KISHINEV",
    "Genova",
    "Izhevsk",
    "Frankfurt am Main",
    "Krasnodar",
    "Breslau",
    "Glasgow",
    "Yaroslave",
    "Khabarovsk",
    "Vladivostok",
    "Zaragoza",
    "Essen",
    "Rotterdam",
    "Irkutsk",
    "Dortmund",
    "Stuttgart",
    "Barnaul",
    "VILNIUS",
    "Poznan",
    "Düsseldorf",
    "Novokuznetsk",
    "Lisbon",
    "HELSINKI",
    "Málaga",
    "Bremen",
    "Sheffield",
    "SARAJEVO",
    "Penza",
    "Ryazan",
    "Orenburg",
    "Naberezhnye Tchelny",
    "Duisburg",
    "Lipetsk",
    "Hannover",
    "Mykolaiv",
    "Tula",
    "OSLO",
    "Tyumen",
    "Copenhagen",
    "Kemerovo",
    "Moscow",
    "LONDON",
    "St Petersburg",
    "BERLIN",
    "MADRID",
    "ROMA",
    "KIEV",
    "PARIS",
    "Bucharest",
    "BUDAPEST",
    "Hamburg",
    "MINSK",
    "Warsaw",
    "Belgrade",
    "Vienna",
    "Kharkov",
    "Barcelona",
    "Novosibirsk",
    "Nizhny Novgorod",
    "Milan",
    "Ekaterinoburg",
    "Munich",
    "Prague",
    "Samara",
    "Omsk",
    "SOFIA",
    "Dnepropetrovsk",
    "Kazan",
    "Ufa",
    "Chelyabinsk",
    "Donetsk",
    "Naples",
    "Birmingham",
    "Perm",
    "Rostov-na-Donu",
    "Odessa",
    "Volgograd",
    "Cologne",
    "Turin",
    "Voronezh",
    "Krasnoyarsk",
    "Saratov",
    "ZAGREB",
    "Zaporozhye",
    "Lódz",
    "Marseille",
    "RIGA",
    "Lvov",
    "Athens",
    "Salonika",
    "STOCKHOLM",
    "Kraków",
    "Valencia",
    "AMSTERDAM",
    "Leeds",
    "Tolyatti",
    "Kryvy Rig",
    "Sevilla",
    "Palermo",
    "Ulyanovsk",
    "KISHINEV",
    "Genova",
    "Izhevsk",
    "Frankfurt am Main",
    "Krasnodar",
    "Breslau",
    "Glasgow",
    "Yaroslave",
    "Khabarovsk",
    "Vladivostok",
    "Zaragoza",
    "Essen",
    "Rotterdam",
    "Irkutsk",
    "Dortmund",
    "Stuttgart",
    "Barnaul",
    "VILNIUS",
    "Poznan",
    "Düsseldorf",
    "Novokuznetsk",
    "Lisbon",
    "HELSINKI",
    "Málaga",
    "Bremen",
    "Sheffield",
    "SARAJEVO",
    "Penza",
    "Ryazan",
    "Orenburg",
    "Naberezhnye Tchelny",
    "Duisburg",
    "Lipetsk",
    "Hannover",
    "Mykolaiv",
    "Tula",
    "OSLO",
    "Tyumen",
    "Copenhagen",
    "Kemerovo",
]
            
if __name__ == '__main__':
    t = TextGenerator()
    t.addExample('colour', 'red')
    t.addExample('colour', 'green')
    t.addExample('colour', 'blue')
    t.addExample('object', '@thing@')
    t.addExample('object', 'a @colour@ @thing@')
    t.addExample('object', 'a @colour@ @thing@')    
    t.addExample('thing', 'cat')
    t.addExample('thing', 'dog')
    t.addExample('thing', 'book')
    t.addExample('size', 'small')
    t.addExample('size', 'tiny')
    t.addExample('size', 'large')
    t.addExample('thing', '@size@ @thing@')
    
    for i in range(10):
        print t.getRandomSentence('@object@')

    n = TextGenerator()
    n.addExamplesFromText(
    """
     colour:  red
    colour:  blue
    colour:  green 
    colour:  yellow
    colour:  purple 
    colour:  black 
    colour:  fuscia 
    #
    jewel:   diamond
    jewel:   ruby
    jewel:   emerald
    jewel:   saphire    
    #
    size: small
    size: tiny
    size: large
    size: giant
    #
    time-span: everlasting
    time-span: temporary
    time-span: nighttime
    time-span: daytime
    time-span: lifelong
    time-span: eternal
    #
    effect: wellness
    effect: charm
    effect: charisma
    effect: intellect
    #
    jewel-item:  @colour@ @jewel@
    jewel-item:  @jewel@
    #
    jewel-description: The @size@ @jewel-item@ of @property@
    jewel-description: The @jewel-item@ of @property@
    short-jewel-description: @jewel-item@
    #
    property: @time-span@ @effect@
    property: @effect@
    #
    reason: was @verb@ by @name@ in @time@
    verb: lost
    verb: placed
    verb: discarded
    verb: mislaid
    verb: recorded
    #
    name: @first-name@ @last-name@
    name: @first-name@ @last-name@ @post-name@
    first-name: Bob
    first-name: Fred
    first-name: Jim
    first-name: Bill
    first-name: Marvin
    first-name: Jill
    first-name: Alice
    first-name: Sheila
    first-name: Lemon
    last-name: Smith
    last-name: Jones
    last-name: Crimson
    last-name: Little
    last-name: Jenson
    last-name: Williams
    post-name: Junior
    post-name: Senior
    post-name: I
    post-name: II
    #
    time: 1900's
    time: 1800's
    time: 1950's
    time: 1960's
    time: 1970's
    time: 1980's
    time: 1990's
    #
    description: @jewel-description@ @reason@
    #
    """
    )              
    
    for i in range(20):
        print n.getRandomSentence('@description@')

