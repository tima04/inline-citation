inline-citation
===============
###Motivation:
JDM journal requires the authors to provide a latex file with references cited inline in apa style. Most authors write a latex file and a bibtex file separately and then run the bibtex program to generate the references. This program replaces bibtex. It generates a latex file with references cited inline and the reference list appended at the end of the file from the standard latex and bibtex file. For the time being only apa style references are supported.

###Usage:
Download or clone the repository. Suppose foo.bib is the reference file and bar.tex is the latex file, then from the command line: python /path-to-main/main.py /path-to-bibtex-file/foo.bib /path-to-texfile/bar.tex

If everything goes well then a output file bar_output.tex will be generated in the same folder as bar.tex.
