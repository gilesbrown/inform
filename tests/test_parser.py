from StringIO import StringIO
from nose.tools import eq_
from inform.parser import InformParser

parser = InformParser()

class Namespace(object):
    def __init__(self, response):
        self.__names__ =[]
    def __setattr__(self, name, value):
        assert not name.startswith('__')
    

def names(namespace):
    return [name for name in dir(namespace) if not name.startswith('__')]
    

def test_empty():
    ns = InformParser.parse(StringIO(''))
    eq_(names(ns), [])


def test_minimal_form():
    ns = InformParser.parse(StringIO('<form id="name" />'))
    eq_(names(ns), ['name'])
    
    
example = """    
<html>
  <body>
    <form id="name"></form>
  </body>
</html>
"""
    
def test_example():
    d = InformParser.parse(StringIO(example))
    #print list(d.walk())