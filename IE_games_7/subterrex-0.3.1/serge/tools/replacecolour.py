"""Change a graphic to remove pixels of a given colour"""

from PIL import Image
from optparse import OptionParser


if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-c", "--colour", dest="colour", default='255,0,255', type="str",
                      help="colour to replace")
    parser.add_option("-a", "--accuracy", dest="accuracy", default=0, type="int",
                      help="sum of difference between the colour and the target colour to be a match")
                    
    (options, args) = parser.parse_args()

    c = map(int, options.colour.split(','))
    filename = args[0]

    im = Image.open(filename)
    width, height = im.size

    for x in range(width):
        for y in range(height):
            diff = sum([abs(im.getpixel((x, y))[idx] - c[idx]) for idx in range(3)])
            if diff <= options.accuracy:
                im.putpixel((x, y), (0, 0, 0, 0))

    im.save(filename)
    print 'Image updated\n\n'
