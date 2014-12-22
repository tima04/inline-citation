"""
convert the database from the bibtex format to the json format.
"""

import re

def bib2json(bib_file):
    """
    Args
    ----
    bib_file: bibtex file
    
    Return
    ------
    dictionary with key equals citaion-tag, and value
    is a dictionary of bib item.
    example: 
{'katsikopoulos2011herbert':
    {'author': [{'first': ' Konstantinos V', 'last': 'Katsikopoulos'},
    {'first': ' Cherng-Horng Dan', 'last': 'Lan'}],
    'journal': 'Judgment \\& Decision Making',
    'number': '8',
    'tag': 'katsikopoulos2011herbert',
    'title': "Herbert Simon's spell on judgment and decision making.",
    'type': 'ARTICLE',
    'volume': '6',
    'year': '2011'},
 'mitchell1997machine':
    {'author': [{'first': ' Tom M', 'last': 'Mitchell'}],
    'journal': 'Burr Ridge, IL: McGraw Hill',
    'tag': 'mitchell1997machine',
    'title': 'Machine learning. 1997',
    'type': 'BOOK',
    'volume': '45',
    'year': '1997'}
 }
  
    """
    def aux(bib):
        d = parse_bibitem(bib)
        return (d['tag'], d)
    return dict(map(aux, get_bibitems(bib_file)))
    
def get_bibitems(bib_file):
    """
    Args:
    ----
    bib_file: bibtex file
    
    Return:
    --------
    List of bibitems.
    """
    # bibitem begins with @X (X is in the set {AUTHOR, BOOK, INPROCEEDINGS})
    # uses this observation to separate them.
    improbable_str = "&%$" # this is improbable to occur in the text
    text = open(bib_file,"U").read()
    return re.sub("\n@", improbable_str + "\n@", 
                  text).split(improbable_str)[1:]

# ToDo: regex to capture 'x = {y}' pattern should
# be refined in this function
def parse_bibitem(bibitem):
    """
    convert the bibitem from bibtex format to json format
    eg:
    >>> bibitem = '@ARTICLE{rapoport1970choice,' + '\n' + \
    'author = {Rapoport, Amnon and Tversky, Amos},' + '\n' + \
    'title = {Choice behavior in an optional stopping task},' + '\n' + \
    'journal = {Organizational Behavior and Human Performance},' + '\n' + \
    'year = {1970},' + '\n' + \
    'volume = {5},' + '\n' + \
    'pages = {105--120},' + '\n' + \
    'number = {2},' + '\n' + \
    'publisher = {Elsevier}' + '\n' +\
    '}'
    >>> parse_bibitem(bibitem)
    {'author': [{'first': 'Amnon', 'last': 'Rapoport', 'middle': ''},
    {'first': 'Amos', 'last': 'Tversky', 'middle': ''}],
    'journal': 'Organizational Behavior and Human Performance',
    'number': '2',
    'pages': '105--120',
    'publisher': 'Elsevier}',
    'tag': 'rapoport1970choice',
    'title': 'Choice behavior in an optional stopping task',
    'type': 'ARTICLE',
    'volume': '5',
    'year': '1970'}
    """
    rslt = {}
    bibitem = bibitem.strip()
    # from '..\n name_i = {value_i} \n,..', in the bibitem
    # get the list [(name_1, value_1),..]
    # and convert it into dictionary
    rxp = re.compile(r"""
    ^[\W]*(\w+) #lhs starts at a newline, separated by one or more non-alphanumeric character (most likely space)
    [\W]*[=][\W]* # = is a separator
    \{(.*?)\},?$ # rhs starts with '{' and ends with '},' or '}'
    # best is to do the paren match '{' '}', for later
    """,re.VERBOSE|re.MULTILINE|re.DOTALL)
    rslt = keys2lower(dict(rxp.findall(bibitem))) # Author should become author \
           # and so on
    try: 
        rslt['author'] = parse_authors(rslt['author'])
    except KeyError:
        #import pdb; pdb.set_trace()
        print """Warning: Could not parse author(s) from the following bibitem. Are the
        first and last name of the author(s) comma separated 
        for e.g 'Rapoport, Amnon and Tversky, Amos'?\n""", bibitem
        pass
    # get 'type' and 'tag' field from the first line of the
    # bibitem '@X{y,'
    try:
        dict_ = re.match("@(?P<type>\w+)\{(?P<tag>\w+),", bibitem).groupdict()
    except AttributeError:
        dict_ = {'type': 'none', 'tag': 'none'}
    rslt['type'] = dict_.get('type', "").lower()
    rslt['tag'] = dict_['tag']
    return rslt

def parse_authors(authors):
    """
    eg: 
    parse_authors('Rapoport, Amnon and Tversky, Amos')
    [{'first': Amnon, 'last': Rapoport},
    {'first': Amos, 'last': Tversky}
    ]
    """
    rslt = []
    for author in authors.split(' and '):
        try:
            last, first = author.split(',')
        except ValueError:
            last, first = author, "" # empty first name
        rslt.append({'first':first, 'last':last})
    return rslt

def keys2lower(dict_):
    """For all those keys in dict_ which are string
    change them to lower case and remove whitespaces from
    them."""
    lower = lambda x: x.lower() if type(x) == str else x
    rslt = {}
    for key in dict_:
        if type(key) != str:
            rslt[key] = dict_[key]
        else:
            k = re.sub('\s', "", key.lower())
            rslt[k] = dict_[key]
    return rslt

## examples for testing
b1 = """
@ARTICLE{rapoport1970choice,
author = {Rapoport, Amnon and Tversky, Amos},
title = {Choice behavior in an optional stopping task},
journal = {Organizational Behavior and Human Performance},
year = {1970},
volume = {5},
pages = {105--120},
number = {2},
publisher = {Elsevier}
}
"""

b2 = '\n' + \
           '@ARTICLE{rapoport1970choice,' + '\n' + \
           'author = {Rapoport, Amnon and Tversky, Amos},' + '\n' + \
           'title = {Choice behavior in an optional stopping task},' + '\n' + \
           'journal = {Organizational Behavior and Human Performance},' + '\n' + \
           'year = {1970},' + '\n' + \
           'volume = {5},' + '\n' + \
           'pages = {105--120},' + '\n' + \
           'number = {2},' + '\n' + \
           'publisher = {Elsevier}' + '\n' +\
           '}'

b3 = """
@ARTICLE{andrews1995studying,
  author = {Andrews, Rick L and Srinivasan, TC},
  title = {Studying consideration effects in empirical choice models using scanner
	panel data},
  journal = {Journal of Marketing Research},
  year = {1995},
  pages = {30--41},
  publisher = {JSTOR}
}
"""
b4 = r"""
@INPROCEEDINGS{dieckmann2004simple,
  author = {Dieckmann, Anja and Todd, Peter M and Forbus, K and Gentner, D and
	Regier, T},
  title = {Simple ways to construct search orders},
  booktitle = {Proceedings of the 26th annual conference of the cognitive science
	society},
  year = {2004},
  pages = {309--314}
}
"""
b5 = r"""
@ARTICLE{schotter1981economic,
  author = {Schotter, Andrew and Braunstein, Yale M},
  title = {Economic search: An experimental study},
  journal = {Economic Inquiry},
  year = {1981},
  volume = {19},
  pages = {1--25},
  number = {1},
  publisher = {Wiley Online Library}
}
"""
