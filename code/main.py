from inline_citation import inline_citation
import argparse

def main():
    parser = argparse.ArgumentParser(usage="python main.py bibtex-file tex-file")
    parser.add_argument("bibtex_file")
    parser.add_argument("tex_file")
    args = parser.parse_args()
    inline_citation(args.bibtex_file, args.tex_file)
    return None

if __name__ == "__main__":
    main()
 
