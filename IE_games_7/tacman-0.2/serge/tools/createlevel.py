"""Simple way to create a level for a game"""

from optparse import OptionParser
import sys
import os
import shutil

sys.path.append(os.path.abspath('.'))
import serge

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-g", "--name", dest="name", default='game', type="str",
                      help="name of the game")
    parser.add_option("-n", "--world", dest="world", default='world', type="str",
                      help="name of the world")
    parser.add_option("-l", "--location", dest="location", default=os.curdir, type="str",
                      help="location to place the game")
    parser.add_option("-f", "--force", dest="force", default=False, action="store_true",
                      help="overwrite existing folder (all folder contents will be deleted)")
    parser.add_option("-w", "--width", dest="width", default=32, type="int",
                      help="width of the level in squares")
    parser.add_option("-v", "--height", dest="height", default=32, type="int",
                      help="height of the level in squares")
    parser.add_option("-W", "--cellwidth", dest="cellwidth", default=32, type="int",
                      help="width of the cells in the level in pixels")
    parser.add_option("-V", "--cellheight", dest="cellheight", default=32, type="int",
                      help="height of the cells in the level in pixels")


def getSergePath():
    """Return path to serge"""
    return os.path.dirname(serge.__file__)


def copyTemplate(path, src, dest, names=None, binary=False):
    """Copy a template file"""
    destination = os.path.join(path, *dest)
    if os.path.isfile(destination):
        if not options.force:
            result = raw_input('"%s" already exists, overwrite (n)?' % destination)
            if result.lower() != 'y':
                print 'Level not created'
                sys.exit(1)
    #
    use_names = names if names else {}
    binary = 'b' if not names else ''
    with file(os.path.join(getSergePath(), *src), 'r'+binary) as f:
        text = f.read()
    with file(destination, 'w'+binary) as f:
        if names:
            result = text % use_names
        else:
            result = text
        if not binary:
            result = result.replace('@', '%')
        f.write(result)

    
tile_layer_template = """
 <layer name="%(layername)s" width="%(width)d" height="%(height)d"  opacity="%(opacity)f">
  <properties>
   <property name="type" value="%(layertype)s"/>
  </properties>
  <data encoding="csv">
  %(data)s
  </data>
 </layer>
"""

def createMainFile(path, options):
    """Create the main module"""
    data_names = {
            'game' : options.name,
             'world' : options.world,
             'width' : options.width, 'height' : options.height,
             'cellwidth' : options.cellwidth, 'cellheight' : options.cellheight,
     }
    #
    # Tile based layers
    layers = []
    for layer, layertype, datavalue in (
                ('Background', 'visual', 0), ('Main', 'visual', 0), ('Decor', 'visual', 0),
                ('Movement', 'movement', 1), ('Visibility', 'visibility', 2), ('Bullets', 'bullet_traversal', 3), 
                ('Destructible', 'destructible', 4)
            ):
        data_names['layername'] = layer
        data_names['layertype'] = layertype
        data = [[datavalue]*options.width]*options.height
        data_names['data'] = ',\n'.join([','.join(map(str, line)) for line in data])
        data_names['opacity'] = 1.0 if layertype == 'visual' else 0.5
        layers.append(tile_layer_template % data_names)
    data_names['layers'] = '\n'.join(layers)
    #
    # Object based layers
    copyTemplate(path, ['tools', 'template-world', 'template.tmx'], ['worlds', '%s.tmx' % options.world], data_names, options)
        


          
def main(options):
    """Create the template"""
    path = os.path.join(options.location, options.name.lower())
    createMainFile(path, options)
    print 'Game created'
    
if __name__ == '__main__':
    (options, args) = parser.parse_args()
    main(options)
    
