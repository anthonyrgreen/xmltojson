This is a utility for parsing NCBI ClinVar xml data and converting it according to a preset JSON schema.
It depends on the following two packages:
1. argparse
2. lxml
which can both be installed via pip.

Usage is simple:
[user]$ python main.py --help
brings up the run options. A typical use case is:
[user]$ python main.py data/ClinVarFullRelease_2014-08.xml -o out.json

To ensure that the operation is going as planned, a test can be added, as follows:
[user]$ python main.py data/ClinVarFullRelease_2014-08.xml -o out.json --test
