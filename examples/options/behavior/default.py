import cloc

class Default(cloc.Cloc):
    def __init__(self) -> None:
        super().__init__()
        self._use_default_on_unreferenced_function = True
        self._skip_on_unreferenced_function = False

        self._convert_unreferenced_symbol_to_str = False
        self._use_default_on_unreferenced_symbol = True

    def default(self, *args, **kwds):
        print('default',args)
        return args[0]

    def show(self,arg):
        print('show',arg)


d = Default()
d.from_str("""
show(createAny(her)).
createAny("You").
""")
print(d._memoize)
print(d._memoize_call)
