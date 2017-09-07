#!/usr/bin/python2.7

import sys, re, itertools

def print_usage():
  print "PyMacro is a preprocessor for powerful verilog metaprogramming. Usage:"
  print "%s <file.pm> [token='$']" % sys.argv[0]
  print "The *.pv file is standard verilog with embedded segments of arbitrary python: '$$EXPRESSION$$', or '$!ARBITRARY_CODE!$'."
  print "If a custom token is defined, say \%\%\%, the above becomes \%\%\%$EXPRESSION$\%\%\%', or '\%\%\%!ARBITRARY_CODE!\%\%\%"
  print "Any printouts from code inside $!...!$, and the result of evaluating expressions inside $$...$$ is inserted in place of these segments."
  print "Pro tip: You can use #import statements"
  print "There is no library; anything you need you write yourself."

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
  file = re.sub(r"\r?\n", ("%s#" % token), file) # Hide newlines for now
  segments = list(filter(None, re.split(r"%s([\$\!].*?)[\$\!]%s" % (re.escape(token), re.escape(token)), file, re.MULTILINE)))
  v_segments = [re.sub("%s#" % re.escape(token), "\n", s) for s in segments[0::2]]
  py_segments = [((s[0] == "$"),  re.sub(r"%s#" % re.escape(token), "\n", s[1:])) for s in segments[1::2]]

  #evaluate/execute py_segements in a presistent scope
  def do_exec(str):
    exec(str) in file_scope
    return ""
  print py_segments
  py_results = [( eval(s[1], file_scope) if s[0] else do_exec(s[1]) ) for s in py_segments]

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
