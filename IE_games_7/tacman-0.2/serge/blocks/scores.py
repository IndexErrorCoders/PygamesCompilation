"""Handling high score type tables"""

import operator

import serge.serialize

class DuplicateCategory(Exception): """The category was already added"""
class BadCategory(Exception): """The category was not found"""
class BadData(Exception): """The data provided for a category was not valid"""
class InvalidSort(Exception): """The sort direction was invalid"""
class InvalidSortColumn(Exception): """The column specified for sorting was not valid"""


class HighScoreTable(serge.serialize.Serializable):
    """A high score table
    
    The table can contain scores in a number of categories. Each
    category is a table with multiple columns. The table can be
    sorted by any one column and can have a limited set of 
    values
    
    """

    my_properties = (
        serge.serialize.D('categories', {}, 'the categories in this table'),
    )
    
    def __init__(self):
        """Initialise the HighScoreTable"""
        self.categories = {}
        
    def addCategory(self, name, number=None, sort_columns=None, directions=('ascending',)):
        """Add a new category"""
        if name in self.categories:
            raise DuplicateCategory('The category "%s" has already been added to this table' % name)
        self.categories[name] = Category(name, number, sort_columns, directions)
        
    def addScore(self, category_name, name, *args):
        """Add a score to a category"""
        return self.getCategory(category_name).addScore(name, *args)
        
    def getCategory(self, category_name):
        """Return a category"""
        try:
            return self.categories[category_name]
        except KeyError:
            raise BadCategory('The category "%s" was not found' % category_name)
        
    def resetTable(self):
        """Clear the entire table"""
        self.categories = {}

    def resetCategory(self, category_name):
        """Reset the category name"""
        try:
            self.categories[category_name].resetCategory()
        except KeyError:
            raise BadCategory('The category "%s" was not found' % category_name)
        
class Category(list):
    """A category for an individual score table"""
    
    def __init__(self, name, number=None, sort_columns=None, directions=('ascending',)):
        """Initialise the Category"""
        self.name = name
        self.number = number
        for direction in directions:
            if direction not in ('ascending', 'descending'):
                raise InvalidSort('The sort direction (%s) was invalid. Should be either "ascending" or "descending"' % direction)
        self.sort_columns = sort_columns
        self.directions = directions
        
    def addScore(self, name, *args):
        """Add a new score"""
        if self.sort_columns and max(self.sort_columns) > len(args):
            raise InvalidSortColumn('The data provided (%s) is not as long as the sort column (%s)' % (args, self.sort_columns))
        #
        # Add the new item
        this_row = (name,) + args
        self.append(this_row)
        #
        # Apply sorting
        def sorter(a, b):
            """Sorter that can cope with multiple levels of sort"""
            for column, direction in zip(self.sort_columns, self.directions):
                c = cmp(a[column], b[column])
                if direction == 'ascending':
                    c *= -1
                if c:
                    return c
            return 0
        #
        if self.sort_columns:
            self.sort(cmp=sorter)
        #
        # And limit the size of the table
        if self.number:
            del(self[self.number:])
        #
        # Now find out position
        for position, row in enumerate(self):
            if row == this_row:
                return position+1
        else:
            return None
        
    def resetCategory(self):
        """Reset this category, deleting all the data but maintaining the configuration"""
        del(self[:])
