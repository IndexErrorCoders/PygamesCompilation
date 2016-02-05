"""Represents a conversation

A conversation is a set of nodes with optional branches afterwards.

Each node has some text, either a single line or multiple lines.


"""

from xml.etree.ElementTree import ElementTree

import serge.common


class InvalidFile(Exception): """The XML file was not valid"""
class NodeNotFound(Exception): """The node was not found in the tree"""
class BadOption(Exception): """The option was not found"""

# Events
E_CONVERSATION_ENDED = 'conversation-ended'

class ConversationManager(serge.common.Loggable, serge.common.EventAware):
    """Manages a conversation"""

    def __init__(self, tree, callback=None, root=None, variables=None):
        """Initialise the ConversationManager"""
        self.addLogger()
        self.initEvents()
        self.tree = tree
        self.callback = callback
        self.root = root
        self.variables = variables

    @classmethod
    def fromXMLFile(cls, filename):
        """Load from an XML filename"""
        try:
            tree = ElementTree().parse(filename)
        except Exception, err:
            raise InvalidFile('Could not load XML file from %s: %s' % (filename, err))
        return cls(tree, root=tree, variables={})

    def getNewManager(self, parent):
        """Return a new manager pointing to the parent"""
        return self.__class__(parent, self.callback, self.root, self.variables)
        
    def setCallback(self, callback):
        """Set the callback"""
        self.callback = callback
        
    def findNode(self, *names):
        """Return the node with the given name"""
        root_node = self.root
        for name in names:
            root_node = root_node.find(r".//node[@TEXT='%s']" % name)
            if root_node is None:
                raise NodeNotFound('Could not find a node named "%s"' % name)
        manager = self.getNewManager(root_node)
        manager.processNodeVariables(manager)
        return manager

    def findNodeByID(self, ID):
        """Return the node with the given ID"""
        root_node = self.root.find(r".//node[@ID='%s']" % ID)
        if root_node is None:
            raise NodeNotFound('Could not find a node with id "%s"' % ID)
        manager = self.getNewManager(root_node)
        manager.processNodeVariables(manager)
        return manager
            
    def getChild(self):
        """Return the first child"""
        return self.getNewManager(self.tree.find('node'))

    def moveNext(self):
        """Move on to the next node"""
        node = self.tree.find('node')
        if node is None:
            self.restartConversation()
        else:
            self.tree = node
            self.processNodeVariables(self)

    def getChildren(self):
        """Return the children"""
        return [self.getNewManager(child) for child in self.tree.findall('node')]
        
    def getText(self):
        """Return the text for this node"""
        if self.tree is None:
            return ''
        rich = self.tree.find('richcontent')
        if rich is not None:
            variables, text = self.parseRichText([i.text.strip() for i in rich.findall('html/body/p')], 
                {'me' : self.tree.attrib['ID']})
            #
            # Watch for a case statement
            variables_dict = dict(variables)
            if 'case' in variables_dict:
                case_variable = variables_dict['case']
                value = self.variables.get(case_variable, '')    
                for child in self.getChildren():
                    if value == '' or child.getText() == value:
                        child.moveNext()
                        return child.getText()
                else:
                    raise ValueError('Case statement for "%s" on node "%s" didn\'t find a valid option with value "%s"' % 
                        (case_variable, self, value))
            if text:
                return text
        #
        return self.tree.attrib['TEXT']

    def getNodeVariables(self, node):
        """Return the variables for this node"""
        rich = node.find('richcontent')
        if rich is not None:
            variables, text = self.parseRichText([i.text.strip() for i in rich.findall('html/body/p')], 
                {'me':node.attrib['ID']})
            if variables:
                return variables
        #
        return []
 
    def getVariable(self, name):
        """Return the value of a variable"""
        return self.variables[name]
 
    def parseRichText(self, lines, data):
        """Return the variables and text from a rich text list"""
        variables, text = [], []
        for line in lines:
            if line.startswith('$'):
                name, value = line[1:].split('=')
                variables.append((name.strip(), eval(value, data)))
            else:
                text.append(line)
        return variables, '\n'.join(text)


    def getLink(self):
        """Return a link or None if we don't have one"""
        link = self.tree.find('arrowlink')            
        if link is None:
            return None
        else:
            dest_id = link.attrib['DESTINATION']
            dest = self.root.find('.//node[@ID="%s"]' % dest_id)
            if dest is None:
                raise BadLink('Followed a link but could not find id %s' % (destination,))
            return self.getNewManager(dest)
            
    def processNodeVariables(self, node):
        """Process variables in the current node"""
        variables = self.getNodeVariables(node.tree)
        for name, value in variables:
            self.variables[name] = value
            if name == 'callback' and self.callback:
                self.callback(node, value)

    def chooseOption(self, name):
        """Choose an option named name"""
        #
        # Choose the matching option
        for option in self.getChildren():
            if option.getText() == name:
                chosen = option
                break
        else:
            raise BadOption('The option "%s" was not found in node "%s"' % (name, self.getText()))
        #
        self.processNodeVariables(chosen)
        #
        # Move on
        link = chosen.getLink()
        if link:
            chosen = link.tree
        else:
            chosen = chosen.getChild().tree
        #
        if chosen is not None:
            self.tree = chosen
        else:
            self.restartConversation()
        self.log.info('Chose option "%s", new node is "%s"' % (name, self.getText()))
        
    def restartConversation(self):
        """Try to restart the conversation"""
        self.processEvent((E_CONVERSATION_ENDED, self))
        go_to = self._findReturnTo()
        if go_to is None:
            self.tree = self.root.find('node')
            self.log.info('Returning to the root of the conversation')
        else:
            if go_to.startswith('ID_'):
                self.tree = self.findNodeByID(go_to).tree
            else:
                new = self.findNode(*go_to.split('.'))
                self.tree = new.tree
            self.log.info('Returning to node "%s"' % self.getText())
        self.moveNext()

    def _findReturnTo(self):
        """Find the return to for this node"""
        print self.tree.attrib
        rich = self.tree.find('richcontent')
        if rich:
            variables, text = self.parseRichText([i.text.strip() for i in rich.findall('html/body/p')], 
                {'me' : self.tree.attrib['ID']})
            #
            # Watch for a case statement
            variables_dict = dict(variables)
            if 'return-to' in variables_dict:
                return variables_dict['return-to']
        #
        # Try parent
        parent = self.getParent()
        if parent is None:
            return None
        else:
            return parent._findReturnTo()
        
    def getParent(self):
        """Return the parent node"""
        if 'ID' not in self.tree.attrib:
            return None
        else:
            return self.getNewManager(self.root.find('.//node[@ID="%s"]..' % self.tree.attrib['ID']))
