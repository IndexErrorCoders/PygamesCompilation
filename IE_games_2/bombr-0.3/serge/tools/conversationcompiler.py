"""Compile a conversation into a python file"""

from optparse import OptionParser
import sys
import os
from pyparsing import *
import pprint

if __name__ == '__main__':
    sys.path.append(os.path.abspath('.'))

    parser = OptionParser()
    parser.add_option("-s", "--source", dest="source", type="str",
                      help="source file for conversation")
    parser.add_option("-d", "--destination", dest="destination", type="str",
                      help="destination python file")
    parser.add_option("-x", "--xml", dest="xml", default=None, type="str",
                      help="destination xml file")
    parser.add_option("-t", "--test", dest="test", default=False, action="store_true",
                      help="test conversation when done")

    (options, args) = parser.parse_args()

    test = file(options.source, 'r').read()

    class Bag(object):
        pass
        
    STATE = Bag()
    STATE.stack = []
    STATE.text = '<nodes>'

    def gotLiteralLine(s, loc, toks):
        """Got a literal"""
        STATE.text += '<text person="NPC">%s</text>' % toks[0]

    def gotBlockStart(s, loc, toks):
        """Got a literal"""
        weight = (len(toks)-2)/4
        if toks[-2] == 'important':
            weight += 20
        #
        STATE.text += '<node person="%s" weight="%d">' % (toks[0], weight)
        STATE.stack.append('node')
        if len(toks) != 2:
            for idx in range((len(toks)-2)/4):
                name, _, prop = toks[4*idx+2:4*idx+5]
                STATE.text += '<condition name="%s" property="%s"/>' % (name, prop)
        #

    def gotStartMission(s, loc, toks):
        """Got the start of a mission"""
        STATE.text += '<mission name="%s">' % toks[0]
        STATE.stack.append('mission')
        
    def gotResponseLine(s, loc, toks):
        """Got a response"""
        STATE.text += '<text person="player">%s</text>' % toks[0]

    def gotChoice(s, loc, toks):
        """Got a choice"""
        STATE.text += '<options>'
        STATE.stack.append('options')

    def gotLoop(s, loc, toks):
        """Got a loop"""
        STATE.text += '<options loop="True">'
        STATE.stack.append('options')

    def gotEndBlock(s, loc, toks):
        """Got an end block"""
        STATE.text += '</%s>' % STATE.stack.pop()

    def gotCommand(s, loc, toks):
        """Got a command"""
        STATE.text += '<command name="%s"/>' % toks[0]

    def gotSetter(s, loc, toks):
        """Got a setter"""
        if toks[0] == '%!':
            STATE.text += '<setter name="%s" property="%s" value="False"/>' % (toks[1], toks[3])
        else:
            STATE.text += '<setter name="%s" property="%s" value="True"/>' % (toks[1], toks[3])

    Name = Word(alphas) + '.' + Word(alphas+'-')
    Loop = (Literal('loop') + '{').setParseAction(gotLoop)    
    Choice = (Literal('choice') + '{').setParseAction(gotChoice)
    StartMission = Literal('Mission:') + Word(alphanums).setParseAction(gotStartMission) + '{'
    StartBlock = (Word(alphas) + ZeroOrMore(',' + Name) + Optional(',' + Literal('important')) + '{').setParseAction(gotBlockStart)
    LiteralLine = Word(alphas) + '>' + SkipTo(LineEnd()).setParseAction(gotLiteralLine)
    ResponseLine = '>' + SkipTo(LineEnd()).setParseAction(gotResponseLine)
    EndBlock = Literal('}').setParseAction(gotEndBlock)
    Command = '$' + (Literal('break') | Literal('exit') | Literal('continue')).setParseAction(gotCommand)
    Setter = ((Literal('%!') | Literal('%')) + Name).setParseAction(gotSetter)
    Comment = '#' + SkipTo(LineEnd())
    Line = Comment | Loop | Choice | StartMission | StartBlock  | LiteralLine  | ResponseLine | EndBlock | Command | Setter
    block = Word(alphas) + '{' + OneOrMore(Line) + LineEnd() + '}'

    for idx, line in enumerate(test.splitlines()):
        if line.strip():
            #print line
            try:
                Line.parseString(line)
            except Exception, err:
                import pdb; pdb.set_trace()
                print '*** Failed on line %d "%s"\n%s' % (idx+1, line, err)
        else:
            STATE.text += '<blank/>'
                
    STATE.text += '</nodes>'

    if options.xml:
        file(options.xml, 'w').write(STATE.text)
        
    import xml.etree.ElementTree   
    tree = xml.etree.ElementTree.fromstring(STATE.text)


    class Node(object):
        def __init__(self, node):
            """Initialise the node"""
            self.node = node
            self.conditions = node.findall('condition')
           
        def convert(self, indent, index):
            """Return conversion"""
            lines = []
            self.addLine(lines, indent, "%s person == '%s'%s:" % (
                'if' if index == 0 else 'elif', 
                self.node.attrib['person'], self.convertConditions()))
            indent += 1
            #
            self.convertItems(self.node.getchildren(), indent, lines)               
            #
            return '\n'.join(lines)
        
        def convertItems(self, items, indent, lines):
            """Convert all items"""
            last_item = None
            for item in items:
                self.convertItem(item, indent, lines)
                last_item = item
                
        def convertItem(self, item, indent, lines):
            """Return the conversion of an item"""
            if item.tag == 'text':
                if item.attrib['person'] == 'NPC':
                    self.addLine(lines, indent, "yield '%s'" % self.safe(item.text))
                else:
                    self.addLine(lines, indent, "yield ('%s',)" % self.safe(item.text))
            elif item.tag == 'options':
                option = Option(item)
                option.convert(indent, lines)
            elif item.tag == 'condition':
                pass
            elif item.tag == 'blank':
                pass
            elif item.tag == 'command':
                if item.attrib['name'] == 'break':
                    self.addLine(lines, indent, 'break')
                elif item.attrib['name'] == 'exit':
                    self.addLine(lines, indent, 'raise StopIteration(0)')
                elif item.attrib['name'] == 'continue':
                    self.addLine(lines, indent, 'raise StopIteration(1)')
                else:
                    raise ValueError('Do not know what command "%s" is' % item.attrib['name'])
            elif item.tag == 'setter':
                self.addLine(lines, indent, "set_state(people, '%s', '%s', %s)" % (
                    item.attrib['name'], item.attrib['property'], item.attrib['value']))
            else:
                self.addLine(lines, indent, 'Dont know what "%s" is' % item)
            
        def addLine(self, lines, indent, line):
            """Add a line"""
            lines.append(' '*indent*4 + line)

        def addBlankResponse(self, lines, indent):
            """Add a simple blank response"""
            self.addLine(lines, indent, "result = (yield ('...', ))")
                    
        def convertConditions(self):
            """Return the converted conditions"""
            if not self.conditions:
                return ''
            else:
                return ' and ' + ' and '.join(
                    ["people['%s'].get('%s', False)" % (condition.attrib['name'], condition.attrib['property'])
                    for condition in self.conditions])   

        def safe(self, text):
            """Make text safe by escaping stuff"""
            safe = text.replace("'", "\\'")               
            return safe
            
    class Option(Node):
        """Convert an option node"""
        
        def __init__(self, node):
            """Initialise the node"""
            self.node = node

        def convert(self, indent, lines):
            """Return conversion"""
            options = []
            this_option = []
            for item in self.node.getchildren():
                if item.tag == 'blank':
                    if this_option:
                        options.append(this_option)
                        this_option = []
                else:
                    this_option.append(item)
            else:
                if this_option:
                    options.append(this_option)          
            #
            if self.node.attrib.get('loop', 'False') == 'True':
                self.addLine(lines, indent, 'while True:')
                indent += 1
            #
            if len(options) > 1:
                self.addLine(lines, indent, 'result = (yield %s)' % ', '.join(
                        ["'%s'" % self.safe(option[0].text) for option in options]))
            else:
                self.addLine(lines, indent, "result = (yield ('%s',))" % self.safe(options[0][0].text))
            #
            for idx, option in enumerate(options):
                prefix = 'if' if idx == 0 else 'elif'
                self.addLine(lines, indent, '%s result == "%s":' % (prefix, self.safe(option[0].text)))
                self.convertItems(option[1:], indent+1, lines)
               

    text = '''
# This file is autogenerated - do not edit it

import serge.events

E_CONVERSATION_STATE_CHANGE = 'conversation-state-change'
serge.events.getEventBroadcaster().registerEvent(E_CONVERSATION_STATE_CHANGE)

def set_state(people, person, property, value):
    """Set a conversation state"""
    people[person][property] = value
    serge.events.getEventBroadcaster().processEvent((E_CONVERSATION_STATE_CHANGE, (person, property, value)))
            
'''



    def getPeople(node):
        """Return a list of all the people"""
        people = set()
        for node in node.findall('.//node'):
            people.add(node.attrib['person'])
        return list(people)

    def getConditions(node):
        """Return all the conditions"""
        conditions = {}
        for person in getPeople(node):
            conditions[person] = {}
        for condition in node.findall('.//condition'):
            conditions[condition.attrib['name']][condition.attrib['property']] = False
        return conditions
        
    def getInitialDictionary(mission, node):
        """Return the text for the function to create the initial conversation dictionary"""
        conditions = getConditions(node)
        text = '\ndef conversation_dictionary_%s():\n\t return (%s\n\t)\n\n' % (
            mission, '\n\t'.join(pprint.pformat(conditions).splitlines()))
        return text

    missions = tree.findall('mission')
    for mission in missions: 
        text += '''def conversation_%s(person, people):\n    """The conversation"""\n''' % mission.attrib['name']
       
        nodes = [Node(node) for node in mission.findall('node')]
        nodes.sort(cmp=lambda x, y: cmp(int(x.node.attrib['weight']), int(y.node.attrib['weight'])))
        nodes.reverse()

        for idx, node in enumerate(nodes):
            text += (node.convert(1, idx) + '\n\n')


        text += getInitialDictionary(mission.attrib['name'], tree)
        
    file(options.destination, 'w').write(text)
             

