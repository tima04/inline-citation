import re

def gen_refs(infile, json_db):
    """
    infile: tex file 
    return the list of references in the apa style, if any
    error just return empty list.
    """
    tags = map(lambda s: s.strip().lower(),
               get_tags(infile)) # remove whitespaces and convert into lower case.
    refs = map(lambda tag: Ref_apa(json_db.get(tag,{})).gen_ref(), 
               tags)
    refs.sort(key=lambda s: s.split(",")[0]) # sort according to the first author
    return refs

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
        
        if not names: # names is []
            return ""
            
        if len(names) == 1: return aux(names[0])
        
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
    # result on example above : ['green1966signal']
    rslt = set()
    for tags in tags_lst:
        rslt |= set(tags.split(",")) # union
    return list(rslt)
