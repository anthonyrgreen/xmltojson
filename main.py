from xmlToJson import treeParser, toJsonSchema
from argparse import ArgumentParser

parser = ArgumentParser(description="Transform XML records to JSON records")
parser.add_argument("filename", help="The XML input file.")

if __name__ == "__main__":
  args = parser.parse_args()
  tree = treeParser(args.filename, toJsonSchema)
  with open(args.filename + ".json", "w") as output:
    for elem in tree:
      output.write(elem + "\n")
