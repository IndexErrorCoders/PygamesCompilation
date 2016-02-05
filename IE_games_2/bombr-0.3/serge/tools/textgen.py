"""A simple script to allow you to test text generator files"""

import sys
import optparse

import serge.blocks.textgenerator


parser = optparse.OptionParser()
parser.add_option("-p", "--persist", dest="persist", default=False, action="store_true",
                  help="whether to persist the chosen options or not")
parser.add_option("-f", "--form", dest="form", default="", type="str",
                  help="the form to use")
parser.add_option("-n", "--number", dest="number", default=1, type="int",
                  help="the number of repetitions")


options, args = parser.parse_args()

#
# Make sure we have the right number of arguments
if len(args) != 1:
    print 'usage: textgen.py filename'
    sys.exit(1)

#
# Initialise the generator
t = serge.blocks.textgenerator.TextGenerator()
t.addExamplesFromFile(args[0])

#
# The main testing loop
if not options.form:
    print 'Enter <sentence name>, <number of iterations> ... or "q" to quit, or "r" to re-read'
last = ''

while True:
    if not options.form:
        text = raw_input('> ')
    else:
        text = '%s, %d' % (options.form, options.number)
    if text.lower() == 'q':
        break
    elif text.lower() == 'r':
        t = serge.blocks.textgenerator.TextGenerator()
        t.addExamplesFromFile(args[0])
        text = last
    elif not text:
        text = last
    else:
        last = text
    #
    parts = text.split(',')
    if len(parts) != 2:
        print 'Needs to be <sentence>, <number>'
        continue
    try:
        n = int(parts[1])
    except ValueError:
        print 'Second value must be number'
        continue
    #
    d = dict()
    print '\n----\n'
    for i in range(n):
        if not options.persist:
            d = dict()
        print '%3d - %s' % (i + 1, t.getRandomSentence(parts[0], d))
    print '\n----\n'
    #
    if options.form:
        break