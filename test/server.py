import tempfile
from os.path import join as op_join
import itty
from pkg_resources import resource_filename
from mako.lookup import TemplateLookup

templates = TemplateLookup(directories=[resource_filename(__name__, 'html/')], 
                        module_directory=op_join(tempfile.gettempdir(), '/mako_modules'))

class Input(object):
    def __init__(self, name):
        self.name = name

class Form(object):
    def __init__(self, id_):
        self.id = id_
        self.inputs = [Input("fred")]


@itty.get('/')
def index(request):
    #return 'Hello World!'
    template = templates.get_template('index')
    return template.render(forms=[Form('myform')])

if __name__ == '__main__':
    itty.run_itty()