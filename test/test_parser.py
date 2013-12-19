from StringIO import StringIO
from inform.parser import InformParser

def Xtest_empty():
    d = InformParser.parse(StringIO(''))


def test_minimal():
    d = InformParser.parse(StringIO('<html />'))
    print d
    
example = """    
<html>
  <body>
    <form />
    <form />
  </body>
</html>
"""
    
def test_example():
    d = InformParser.parse(StringIO(example))
    print list(d.walk())