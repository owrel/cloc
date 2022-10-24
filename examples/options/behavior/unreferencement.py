#TODO:
#   - Converting unreferenced /0 to str
#   - Ignore key words
#   - Skip unreferencement
#   - Table reference

import cloc

class Unreferencement(cloc.Cloc):
    def __init__(self) -> None:
        super().__init__()
        self._warning_on_unreferenced_supplier_conversion = False

    def instance(self,arg):
        print('Arg:', arg)
        print('Type:',type(arg))


# Whenever a function of arity 0 is found (e.g. fun in  "instance(fun).") is not declared in the object, Cloc can or ignore them, or converting them into string, or raise an error
Unreferencement().from_str("""
instance(fun).
""")
# Output:
# fun
# <class 'str'>
print()

class Unreferencement(cloc.Cloc):
    def __init__(self) -> None:
        super().__init__()
try:
    Unreferencement().from_str("""
    instance(fun).
    """)
except Exception as e:
    print("Exception:",e)

# Output: error cloc.cloc.UnreferencedFunction: Function instance/1 is not referenced
print()



class Unreferencement(cloc.Cloc):
    def __init__(self) -> None:
        super().__init__()
        self._convert_unreferenced_supplier_consumer_to_str = False
    def instance(self,arg):
        print(arg)
        print(type(arg))
try:
    Unreferencement().from_str("""
    instance(fun).
    """)
except Exception as e:
    print("Exception:",e)
# Output: error cloc.cloc.UnreferencedFunction: Function instance/1 is not referenced
print()


class Unreferencement(cloc.Cloc):
    def __init__(self) -> None:
        super().__init__()
        self._convert_unreferenced_supplier_consumer_to_str = False
        self._skip_on_unreferenced_supplier_consumer = True
    def instance(self,arg):
        print(arg)
        print(type(arg))

Unreferencement().from_str("""
instance(fun).
""")

# Output:
# None
# <class 'NoneType'>
print()