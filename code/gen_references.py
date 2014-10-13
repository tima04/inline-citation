# def ref_apa(ref):
#     """
#     arg: a reference from json_db, of type dict
#     return: the reference in apa-style, of type str
#     """
#     def ifelse(cond, expr1, expr2):
#         return expr1 if cond else expr2
#     rslt = "{0} ({1}).".format(author_apa(ref.get('author','')), 
#                                ref.get('year',''))
#     ref_type = ref.get('type','')
#     title = ref.get('title', '')
#     if ref_type == 'ARTICLE':
#         vol = ref.get('volume',"")
#         num = '({0})'.format(ref.get('number')) if ref.get('number') else ''
#         pg = '{0}'.format(ref.get('pages')) if ref.get('pages') else ''
#         rslt += " {tit}. \emph{{{jur}}}".format(tit=title, jur=ref.get('journal',''))
#         if not vol: # may be not published yet
#             rslt += "."
#         else:
#             rslt += ", {vol}{num}".format(vol=vol, num=num) +\
#                     ifelse(pg, ", {pg}.".format(pg=pg),".")
#     elif ref_type == 'INPROCEEDINGS':
#         rslt += "{tit}. \textit{{{book}}} ({pp}).".format(tit=title,
#                                                         book=ref.get('booktitle',''),
#                                                         pp=ref.get('pages',''))
#     elif ref_type == 'BOOK':
#         rslt += "\textit{{{tit}}}. {pub}.".format(tit=title,
#                                                 pub=ref.get('publisher',""))
#     else:
#         raise Exception("unknown type {0}".format(ref['title']))
#     return rslt

class Ref_apa():
    """
    given a reference in a json format, return it as a string
    in apa style, gen_ref is a main interface.

    example:
    ref = 
    {'author': [{'first': ' Tom M', 'last': 'Mitchell'}],
    'journal': 'Burr Ridge, IL: McGraw Hill',
    'tag': 'mitchell1997machine',
    'title': 'Machine learning. 1997',
    'type': 'BOOK',
    'volume': '45',
    'year': '1997'}
    
    print Ref_apa(ref).gen_ref() =>
    Mitchell, T. M. (1997).\\textit{Machine learning. 1997}. Burr Ridge, IL: McGraw Hill.
    """

    def __init__(self, ref):
        self.ref = ref
        auth = ref.get('author', '')
        yr = ref.get('year', '')
        self.auth_yr = "{0} ({1}).".format(self._author_apa(auth), yr)
        self.pg = ref.get('pages', '')
        self.tit = ref.get('title', '')
        self.jur = ref.get('journal','')
        self.pub = ref.get('publisher','')
        self.book = ref.get('book', 
                            ref.get('booktitle',''))
        self.tp = ref.get('type','')

    def ifelse(self,cond, expr1, expr2):
        return expr1 if cond else expr2
        
    def _article(self):
        ref = self.ref
        vol = ref.get('volume',"")
        num = '({0})'.format(ref.get('number')) if ref.get('number') else ''
        rslt = self.auth_yr +\
               " {0}. \\textit{{{1}}}".format(self.tit, self.jur)
        if not vol: # may be not published yet
            rslt += "."
        else:
            rslt += ", \\textit{{{vol}}}{num}".format(vol=vol, num=num) +\
                    self.ifelse(self.pg, ", {0}.".format(self.pg), ".")
        return rslt

    def _proceedings(self):
        rslt = self.auth_yr + \
               " {0}. \\textit{{{1}}} (pp. {2}).".format(self.tit, self.book, self.pg)
        return rslt
    
    def _book(self):
        pub_or_jur = self.ifelse(self.pub, self.pub, self.jur)
        rslt = self.auth_yr + \
               " \\textit{{{0}}}. {1}.".format(self.tit, pub_or_jur)
        return rslt

    def gen_ref(self):
        #import pdb; pdb.set_trace()
        if self.tp == 'INPROCEEDINGS':
            return self._proceedings()
        elif self.tp == 'BOOK':
            return self._book()
        else:
            return self._article()

    def _author_apa(self, names):
        """ e.g: 
        [{'last': 'Luan', 'first': 'Shengua'},
        {'last': 'Schooler', 'first': 'Lael J'}, 
        {'last': 'Gigerenzer', 'first': 'Gerd'}]
        => 'Luan, S., Schooler, L. J,, \& Gigerenzer, G.'
        """
        def aux(name):
            if not name: return "" # name is {}
            if name.get('first'):
                rslt = name['last'] + ', ' 
                rslt += reduce(lambda s1,s2: s1 + '. ' + s2,
                               [s[0] for s in name['first'].split()])
            else:
                rslt = 'et al'
            return rslt + '.'

        if len(names) <= 1: return aux(names[0])
        
        rslt = reduce(lambda n1, n2: n1 + ", " + n2,
                      [aux(n) for n in names[:-1]]) +\
            ' \& ' + aux(names[-1])
        return rslt

def get_tags(fl):
    """
    Extract all tags from the tex file fl
    """
    ptrn = re.compile(r"""
    \\cite[^{]* 
    { (?P<tags>[^}]*) } # {tag1,tag2,..}
    """, re.VERBOSE)
    # example pattern: \cite<e.g.>{green1966signal}

    tags_lst = ptrn.findall(open(fl).read())
    # result on example_txt (below) : 
    # ['Rapoport1970choice,Schotter1981economic,Hey1987still,Kogut1990consumer,Sonnemans1998strategies',
    #  'Hey1982search',
    #  'Sonnemans1998strategies',
    #  'green1966signal']
    
    rslt = set()
    for tags in tags_lst:
        rslt |= set(tags.split(",")) # union
    
    return list(rslt)

def gen_refs(infile, outfile, json_db):
    """
    infile: tex file like example_txt
    """
    tags = map(lambda s: s.strip().lower(),
               get_tags(infile)) # remove whitespaces and convert into lower case.
    #import pdb; pdb.set_trace()
    refs = map(lambda tag: Ref_apa(db[tag]).gen_ref(), 
               tags)

    refs.sort(key=lambda s: s.split(",")[0]) # sort\
    # according to the first author.

    flp = open(outfile, "w")
    for ref in refs:
        flp.write(ref)
        flp.write("\n"*2)
    flp.close()

