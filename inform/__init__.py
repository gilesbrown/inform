import requests
from .parser import InformParser

session_factory = requests.session
parser_factory = InformParser


def get(url, parser=None, session=None):
    if session is None:
        session = session_factory()
    if parser is None:
        parser = parser_factory(session)
    return parser.request('GET', url)