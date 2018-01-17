#!/usr/bin/python2.7

import sys, re, itertools

def print_usage():
  print "PyMacro is a preprocessor for powerful verilog metaprogramming. Usage:"
  print "%s <file> [token='$']" % sys.argv[0]
  print "The macro processor requires a unique token to identify python segments, one that should not be used in the file elsewhere. By default, the unique token is \"$\"."
  print "The file is text with embedded segments of arbitrary python: '$(EXPRESSION)$', or '${ARBITRARY_CODE}$'."
  print "If a custom token is defined, say %%%, the above becomes %%%(EXPRESSION)%%%', or '%%%{ARBITRARY_CODE}%%%"
  print "Any printouts from python code, and the result of evaluating expressions is inserted in place of these segments."
  print "There is no standard library; anything you need you write yourself. Pro tip: You can use #import statements to reuse library code."

file_scope = {}

def main(filename = None, args={}):
  # Default variable values
  token = "$"

  # Override defaults with any values provided as args
  if "token" in args:
    token = args["token"]

  # Open and read PV file
  file = ""
  with open (filename, "r") as f:
    file=f.read()

  # Chop file up into verilog and python tokens.
  # Odd elements are python, of the form (expr?, py_str), where expr? is a boolean denoting that the py_str is an EXPRESSION, and not a block of code.
  file = re.sub(r"\r?\n", ("#%s#" % token), file) # Hide newlines for now
  segments = re.split(r"(%s[\(\{].*?)[\)\}]%s" % (re.escape(token), re.escape(token)), file, flags=re.MULTILINE)
  v_segments = [re.sub("#%s#"%re.escape(token), "\n", s) for s in segments[0::2]]
  py_segments = [(s[0:1+len(token)]==("%s("%token), re.sub(r"#%s#"%re.escape(token), "\n", s[(1+len(token)):])) for s in segments[1::2] ]

  #evaluate/execute py_segements in a presistent scope
  def do_exec(statements):
    exec(statements) in file_scope
    return ""
  py_results = [( eval(s[1].strip(), file_scope) if s[0] else do_exec(s[1].strip()) ) for s in py_segments]

  # Join result into a string
  result = "".join(list(str(it.next()) for it in itertools.cycle([iter(v_segments), iter(py_results)])))

  print result

#
# Break the file into sections.

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print_usage()
  else:
    args = dict(arg.split('=') for arg in sys.argv[2:])
    main(sys.argv[1], args)
