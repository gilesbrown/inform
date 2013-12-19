from inform.rest import StateTransfer
from inform.request import GET
from inform.parser import InformParser


def get(url, session=None):
    if session is None:
        session = create_session()
    return ReST(session.get(url), session)


class ReST(object):
    """ A Representational State Transfer. """
    def __init__(self):
    def transfer(self, request):
        
