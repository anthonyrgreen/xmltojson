from xmlToJson import treeParser, toJsonSchema
from argparse import ArgumentParser
import re, mmap

parser = ArgumentParser(description="Transform XML records to JSON records",
                        epilog="Example: python main.py ClinVarFullRelease_2014-08.xml -o out.json")
parser.add_argument("input_filename",
                    help="The XML input file.")
parser.add_argument("--output_filename", "-o", default = "",
                    help="The file into which json will be output (default: input_filename.json)")
parser.add_argument("--test", "-t",
                    help="Include a testing step which ensures that the number of parsed records is equal to the number of ReferenceClinVarAssertion records in the xml file.",
  action="store_true", default=False)

if __name__ == "__main__":
  args = parser.parse_args()
  input_filename = args.input_filename
  if args.output_filename == "":
    output_filename = input_filename + ".json"
  else:
    output_filename = args.output_filename
  tree = treeParser(input_filename, "ClinVarSet", toJsonSchema)
  with open(output_filename, "w") as output:
    print "Parsing..."
    tagsFound = 0
    for elem in tree:
      tagsFound = tagsFound + 1
      output.write(elem + "\n")
  if args.test:
    print "Testing output..."
    testTree = treeParser(input_filename, "ReferenceClinVarAssertion", lambda _: 0)
    tagsInTree = 0
    for elem in testTree:
      tagsInTree = tagsInTree + 1
    print "ReferenceClinVarAssertion elements in tree: " + str(tagsInTree)
    print "ReferenceClinVarAssertion elements successfully parsed: " + str(tagsFound)
    if tagsInTree == tagsFound:
      print "Success!"
    else:
      print "Failure!"
