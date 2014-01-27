
    def walk(self):
        remainder = [self]
        while remainder:
            print "REM:", remainder
            elem = remainder.pop()
            yield elem
            remainder.extend(elem.children)
            print "REM2:", remainder


class Root(Parent):
    @property
    def element(self):
        if self.children:
            (child,) = self.children
            return child


class Element(Parent):

    @classmethod
    def create_element_class(cls, tag):
        return type(tag, (cls,), {})

    def __init__(self, parent):
        super(Element, self).__init__()
        self.parent = parent
        self.parent.append(self)