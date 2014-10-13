from gen_references import gen_refs
from inline_citation import inline_citation
import argparse

parser = argparse.ArgumentParser(usage="python main.py bibtex-file tex-file")
parser.add_argument("bibtex-file")
parser.add_argument("tex-file")
args = parser.parse_args()
print args

 
