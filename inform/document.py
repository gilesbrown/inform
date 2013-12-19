import urllib2
import logging
from tokenize import generate_tokens
from StringIO import StringIO
#from lxml.etree import _ElementTree, Element
#from lxml.html import html_parser
#from inform.form import Form

log = logging.getLogger(__name__)
#UNPARSEABLE = Element('_unparseable')


class Document(object):
    """ An InformDocument is a parsed HTML page.

    An inform Document contains zero or more HTML forms.
    Each of these forms becomes an attribute of the document.

    Each form is a potential ReST "state transfer" and can be called.

    Calling a Form makes the HTTP requests specified and generates
    a new document describing the result of the requests.
    """

    def __init__(self):
        pass

    #def __getattr__(self, attr):
    #    """ Generate a (hopefully) more relevant error message. """
    #    raise AttributeError("%r has no <form name='%s' ...>" % (self, attr))

    #def __repr__(self):
    #    return 'WOOF!'
#        parser = InformParser()
#        parser.parse(response, self, opener)
#        response = self.opener.open(url_or_request)
#        self.parse(response)
#        
#    def pars
#        #self.parse(response, parser=html_parser, base_url=response.geturl())
#        if self.getroot() is None:
#            # Setting a root here ensures that we can *always*
#            # run selectors against this document.
#            # If you need to test if we set the root you can use:
#            #    if doc.getroot() is UNPARSEABLE: ...
#            self.setroot(UNPARSEABLE)
#        forms = getattr(self.getroot(), 'forms', [])
#        for form in forms:
#            form_name = form.attrib.get('name')
#            if form_name and is_valid_name(form_name):
#                setattr(self, form_name, Form(form, self.__class__, opener))
#            else:
#                log.warning("ignoring form with invalid name %r", form_name)
#        self._response = response

#
#def is_valid_name(s):
#    """ Return True if 's' is a valid ``Inform`` <form> or <input> name. """
#    if s.startswith('_'):
#        return False
#    tokens = generate_tokens(StringIO(s).readline)
#    return tuple(token[:2] for token in tokens) == ((token.NAME, s),
#                                                    (token.ENDMARKER, ''))
