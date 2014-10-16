from bib2json import bib2json
from gen_references import gen_refs
import re

def inline_citation(bib_file, input_file, output_file=None):
    """
    Replace all the citation tags from the input
    file with the inline citations in an apa style, 
    write the result in the output_file.
    Also add the references as a separate section
    at the end of the output file.

    Args
    ----
    bib_file:   name of the bibtex file
    input_file: input_file containing the tex document
    output_file: file to be written, if not provided then
                 generate using out_file_name function
    """
    if not output_file:
        output_file = out_file_name(input_file)
    
    ptrn = re.compile(r"""
    \\cite(?P<suf> [A]? | year?) # either \cite or \citeA or \citeyear
    (< (?P<ang>[^>]*) >)? # txt in <>, if <> present
    { (?P<tags>[^}]*) } # {tag1,tag2,..}
    """, re.VERBOSE)
    
    tags = [] # keep track of tags which has appeared\
           # if a tag appear again then citation style might\
           # be different.
    json_db = bib2json(bib_file)
    txt = open(input_file).read()
    
    def apa(match):
        "helper function used as an argument of the ptrn.sub function, below"
        tags = match.groupdict()['tags'].split(',')
        suf = match.groupdict()['suf']
        ang = match.groupdict()['ang'] ## txt inside <..> if present
        rslt = reduce(lambda s1, s2: s1 + "; " + s2, 
                      [apa_helper(t, suf) for t in tags])
        if ang:
            rslt = "{0} {1}".format(ang, rslt)
        if suf == "":
            rslt = '(' + rslt + ')'
        return rslt
        
    def apa_helper(tag, suf):
        """ 
        suf is in the set {\citeA, \citedate, \cite}.
        if suf is 'A'(\citeA) then return 'a_1, a_2,..and a_n (date)'
        if suf is 'date'(\citedate) then return '(year)'
        if suf is None(\cite) then return 'a_1, a_2,..\& a_n, date'
        """
        bib = json_db[tag.lower().strip()]
        names = map(lambda author: author['last'], 
                    bib['author']) # list of last names
        if suf == 'year':
            tags.append(tag)
            return "(" + bib['year'] + ")"

        if suf == 'A':
            and_style = ' and '
            yr_style = " ({0})".format(bib['year'])
        else:
            and_style = ' \& '
            yr_style = ", {0}".format(bib['year'])

        if len(names) == 1:
            rslt = names[0]
        elif (len(names) > 2) and (tag in tags):
            rslt = "%s et al."%names[0]
        else:
            rslt = reduce(lambda s1, s2: s1 +', '+ s2, names[:-1]) +\
                   and_style + names[-1] 
        rslt += yr_style
        tags.append(tag)
        return rslt

    rslt = ptrn.sub(apa, txt)
    file(output_file, "w").write(rslt)

    # adding reference list at the end of the output file.
    refs = lst2txt(gen_refs(input_file, json_db))
    add_refs(refs, output_file)
    return None

def add_refs(refs, fl):
    """
    Insert references in the file(fl) just before
    the \end{document}
    """
    file_txt = open(fl).read()

    # find the '\end{document}' in the file_txt and
    # insert references before it
    ptrn = r"\end{document}"
    repl = r"\\section{References}" + \
           '\n'*2 + refs.encode('string-escape') +\
           '\n' + ptrn
    if not re.search(ptrn, file_txt):
        raise Exception("\end{document} missing")
    file_txt = re.sub(ptrn, repl, file_txt)
    # modify the file
    open(fl, "w").write(file_txt)
    return None

def lst2txt(lst):
    """
    >>> lst2txt(['a','b','c'])
    "a\nb\c"
    """
    return reduce(lambda s, t: s + '\n' + t, lst)

    
def out_file_name(in_file_name):
    """construct name of the output file 
    from the name of the input file.
    >>> out_file_name("foo.tex")
    "foo_output.tex"
    >>> out_file_name("../foo.tex")
    "../foo_output.tex"
    """
    try:
        base, extension = re.search("(.*\w+)[.](\w+)", in_file_name).groups()
        return base + "_output." + extension
    except AttributeError: # no extension
        return in_file_name + "_output"
