import re

# # # # # # # # # # # # # # # # # #
# An Example of User Defined Syntax
#(Familiarity with regex is assumed)
# ---------------------------------
# First create a regular expression to match the syntax you want
re_add = re.compile(r'(?P<left_op>\S+)\s*[+]\s*(?P<right_op>\S+)')
# This one allows us to find things that match "x + y" where x and y
# are integers.
#
# Then we define a function.
# The console will always pass itself as the first argument,
# and the SRE_Match object as the second.
#
# Everything in the match group will be a string at first so you need
# to convert each element to its correct type, the console can handle this
# with the console.convert_token method
# perform whatever operation you wish to perform (don't foget
# to validate the input, at the very least enclose it in a try..except block)
# Then output it to the console, or do whatever you want with the data.
def console_add(console, match):
        left = console.convert_token(match.group("left_op"))
        right = console.convert_token(match.group("right_op"))
        try:
                out = left + right
        except Exception, strerror:
                console.output(strerror)
        else:
                console.output(out)
        return out


re_function = re.compile(r'(?P<name>\S+)(?P<params>[\(].*[\)])')
def console_func(console, match):
    func = console.convert_token(match.group("name"))
    params = console.convert_token(match.group("params"))


    if not isinstance(params, tuple):
        params = [params]

    try:
        out = func(*params)
    except Exception, strerror:
        console.output(strerror)
    else:
        console.output(out)