from operator import itemgetter, methodcaller
from inspect import getargspec
from copy import deepcopy
from collections import OrderedDict


    


class Controller(object):
    
    def __init__(self, func):    
        self.func = func
        self.args, self.getters = self.inspect_func(func)
       
    @staticmethod 
    def inspect_func(func):
        getters = OrderedDict()
        argspec = getargspec(func)
        if argspec.defaults:
            args = argspec.args[:-len(argspec.defaults)]
        #for arg, default in args_with_defaults:
        #    getters[arg] = methodcaller('get', arg, default)
        return getters

    def __get__(self, obj, objtype):
        print "OBJ: %r" % obj
        print "OBJTYPE: %r" % objtype
        
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
    
    def apply_multidict(self, multidict):
        args = []
        for arg in self.args:
            if arg not in multidict:
                break
            args.append(self.getters[arg](multidict))
        kwargs = {}
        
        kwargs = {}
        #kwargs = {k: kwgetters[k](multidict, k) for kget in self.getters}
        #kwargs = {k: get_kwarg(multidict) for k, getarg in self.kwarg_getters}
        return self.func(*args, **kwargs)


def controller(func):
    return Controller(func)