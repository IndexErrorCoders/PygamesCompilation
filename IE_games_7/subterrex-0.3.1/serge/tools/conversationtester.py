"""Test a conversation"""

from optparse import OptionParser
import sys
import os
from pyparsing import *

if __name__ == '__main__':
    sys.path.append(os.path.abspath('.'))

    parser = OptionParser()
    parser.add_option("-s", "--source", dest="source", type="str",
                      help="source file for conversation")
    (options, args) = parser.parse_args()

    d = {}
    exec(file(options.source, 'r').read(), d)
    c = d['conversation']




    people = {'Fred':{}, 'Bob':{}}
    retry = False

    while True:
        if not retry:
            person = raw_input('Who do you want to talk to? ')
        if person == '':
            print people
            continue
        conversation = c(person, people)
        feedback = None
        retry = False
        while True:
            #
            # Get next item
            try:
                if feedback is None:
                    result = conversation.next()
                else:
                    result = conversation.send(feedback)
            except StopIteration, err:
                if err.args == (1,):
                    retry = True
                else:
                    retry = False
                break
            #
            if isinstance(result, str):
                print '%s> %s' % (person, result)
                feedback = None
            else:
                for idx, item in enumerate(result):
                    print '%d - %s' % (idx+1, item)
                chosen = input('Choice: ')
                feedback = result[chosen-1]
                
