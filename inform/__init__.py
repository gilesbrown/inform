import requests
from .parser import InformParser

session_factory = requests.session
parser_factory = InformParser

def get(url, parser=None, session=None):
    if session is None:
        session = session_factory()
    if parser is None:
        parser = parser_factory(session)
    link = parser.create_link('get', url)
    return link()