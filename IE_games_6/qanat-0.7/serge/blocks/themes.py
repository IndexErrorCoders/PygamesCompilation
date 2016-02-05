"""Classes to implement themes

Themes are sets of settings that may affect anything. The idea is that
you may have a number of settings to do with visuals on a world and you
want to control those centrally, potentially also allowing things
to switch during a game.

The themes are managed by a manager.

"""

class BadThemeDefinition(Exception): """The theme was not of the right format"""
class MissingDefault(Exception): """There was no default theme"""
class MissingSchema(Exception): """There was no schema in the theme definition"""
class ThemeNotFound(Exception): """The named scheme was not found"""
class BadInheritance(Exception): """A theme subclass was not found"""
class BadThemeFile(Exception): """The specified theme file was not found"""
class PropertyNotFound(Exception): """Could not find a property"""
class InvalidFormat(Exception): """The format for the data was invalid"""


class Manager(object):
    """Manages a theme"""
    
    def __init__(self):
        """Initialise the manager"""
        self.themes = {}
        self.current_theme = None
        
    def loadFrom(self, text):
        """Load a theme from some text
        
        The theme is a dictionary where each entry is either a theme
        or the definition of the schema or the special entry __default__,
        which gives the name of the default theme.
        
        If there is an entry then it is a tuple with the name of the
        base theme class followed by a dictionary of entries which
        overide the base class.
        
        Classes are really just the name of another theme.
        
        """
        #
        # Read the definition
        try:
            temp_themes = eval(text)
        except Exception, err:
            raise BadThemeDefinition('Could not read themes from text: %s' % err)
        return self.load(temp_themes)

    def load(self, themes):
        """Load definitions from a dictionary"""
        if not isinstance(themes, dict):
            raise BadThemeDefinition('Theme definition was not a dictionary')
        #
        # Get the default theme
        try:
            self.current_theme = themes['__default__']
        except KeyError:
            raise MissingDefault('The theme definition did not specify a default theme')
        #
        self.themes = themes
        self._verifyThemes()
        
    def loadFromFile(self, filename):
        """Load a theme definition from a file"""
        try:
            with file(filename, 'r') as f:
                return self.loadFrom(f.read())
        except (IOError, OSError), err:
            raise BadThemeFile('Unable to load theme from "%s": %s' % (filename, err))
            
    def selectTheme(self, name):
        """Select the named theme"""
        if name in self.themes:
            self.current_theme = name
        else:
            raise ThemeNotFound('The theme "%s" was not found' % name)
    
    def getTheme(self, name):
        """Return a theme object with a default of the given name"""
        new = Manager()
        new.themes = self.themes
        new.selectTheme(name)
        return new
        
    def hasTheme(self, name):
        """Return True if we have this theme"""
        return name in self.themes
        
    def getProperty(self, name, from_theme=None):
        """Return the named property"""
        try:
            theme = self.themes[from_theme if from_theme else self.current_theme]
        except KeyError:
            raise BadInheritance('The theme "%s" was not found in the inheritance tree' % from_theme)
        try:
            return theme[1][name]
        except KeyError:
            if theme[0] == '':
                raise PropertyNotFound('Could not find property "%s"' % name)
            else:
                return self.getProperty(name, theme[0])

    def getPropertyWithDefault(self, name, default, from_theme=None):
        """Return a property and if it is missing then return the default value
        
        Use this method sparingly. It puts default values in source code
        rather than in the theme files.
        
        """
        try:
            return self.getProperty(name, from_theme)
        except PropertyNotFound:
            return default
            
    def setProperty(self, name, value, from_theme=None):
        """Set a property in a theme"""
        try:
            theme = self.themes[from_theme if from_theme else self.current_theme]
        except KeyError:
            raise BadInheritance('The theme "%s" was not found in the inheritance tree' % from_theme)
        theme[1][name] = value
        
    def updateFromString(self, string):
        """Update the theme from a string of data
        
        Data should be provided as comma separated values like
            name="bob",value=123,etc
            
        """
        for item in string.split(','):
            parts = item.split('=')
            if len(parts) != 2:
                raise InvalidFormat('The string was invalid, should be a=b,c=d etc (%s)' % item)
            self.setProperty(parts[0], eval(parts[1]))

    def _verifyThemes(self):
        """Sanity check on themes"""
        #
        # Is there a base schema and are all inheritance items found
        schema = False
        for name, theme in self.themes.iteritems():
            if name != '__default__':
                if theme[0] == '':
                    schema = True
                elif theme[0] not in self.themes:
                    raise BadInheritance('The inherited name "%s" for theme "%s" was not found' % (theme[0], name))
        if not schema:
            raise MissingSchema('There was no schema definition in the theme')

