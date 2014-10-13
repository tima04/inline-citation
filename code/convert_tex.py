import re

def main(bib_file, input_file, output_file=None):
    if not output_file:
        output_file = "converted_" + input_file
    
    ptrn = re.compile(r"""
    \\cite(?P<suf> [A]? | year?) # either \cite or \citeA or \citeyear
    (< (?P<ang>[^>]*) >)? # txt in <>, if <> present
    { (?P<tags>[^}]*) } # {tag1,tag2,..}
    """, re.VERBOSE)
    
    tags = [] # keep track of tags which has appeared\
           # if a tag appear again then citation style might\
           # be different.
    
    ptrn.sub(apa, )
    
    
    

        

ptrn = re.compile(r"""
\\cite(?P<suf> [A]? | year?) # either \cite or \citeA or \citeyear
(< (?P<ang>[^>]*) >)? # txt in <>, if <> present
{ (?P<tags>[^}]*) } # {tag1,tag2,..}
""", re.VERBOSE)

tags = [] # keep track of tags which has appeared\
       # if a tag appear again then citation style might\
       # be different.

def apa(match, json_db):
    "inline citation in apacite style"

    tags = match.groupdict()['tags'].split(',')
    suf = match.groupdict()['suf']
    ang = match.groupdict()['ang'] ## txt inside <..> if present
    rslt = reduce(lambda s1, s2: s1 + "; " + s2, 
                  [apa_helper(t, suf, json_db) for t in tags])
    if ang:
        rslt = "{0} {1}".format(ang, rslt)
    if suf == "":
        rslt = '(' + rslt + ')'
    return rslt

def apa_helper(tag, suf, json_db):
    """ 
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
        #rslt = "{0} et al.".format(names[0])
        rslt = "%s et al."%names[0]
    else:
        rslt = reduce(lambda s1, s2: s1 +', '+ s2, names[:-1]) +\
               and_style + names[-1] 
    
    rslt += yr_style
    tags.append(tag)
    return rslt

#ptrn.sub(apa,txt2)

fl = open("source.tex")
txt = fl.read()
fl.close()

out = ptrn.sub(apa,txt)
fl = open("manuscript.tex",'w')
fl.write(out)
fl.close()

example_txt = """
So far we have shown that the proposed stopping policy is optimal. But is it psychologically plausible? When sampling from a known distribution with or without recall an optimally acting decision maker should always stop right after encountering an alternative with a value higher than the optimal threshold. Several variations of such optimal threshold problems have been studied extensively in psychology and economics. We have identified five studies reporting results on experiments in which subjects sampled from a known distribution with recall \cite{Rapoport1970choice,Schotter1981economic,Hey1987still,Kogut1990consumer,Sonnemans1998strategies}. In sum, a moderate proportion of the participants in these studies behaved in a manner consistent with the optimal stopping rule. Common discrepancies from the optimal strategy included stopping too early and exercising recall. Nonetheless, the researchers found that the average performance of the participants was near optimal. \citeA{Hey1982search} and \citeA{Sonnemans1998strategies} reported that many subjects used heuristic strategies that appeared consistent with the optimal rule and led to near optimal performance. In the stopping policy we have presented, the decision maker should at every search step reevaluate the returns from sampling the next alternative in line. This task may appear demanding in relation to the optimal threshold rule. However, it has the same structure as a simplified version of a signal-detection problem \cite<e.g.>{green1966signal} --- in which humans are known to perform fairly well. Thus, we believe that the stopping policy could be psychologically plausible as such or it could be well approximated by clever heuristic algorithms. Clearly, the human behavior in the task has to be investigated experimentally in the near future.
""" 
