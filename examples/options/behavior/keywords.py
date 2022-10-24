import cloc

class Keywords(cloc.Cloc):
    def __init__(self) -> None:
        super().__init__()
        self.count = 0

    def show(self,arg):
        print(arg)

    def pass_arg(self,arg):
        print("Call level", self.count)
        self.count += 1
        return arg

    def __str__(self) -> str:
        return "Magic function __str__, the keyword root, allows to refer to the object (here an instance of Keywords)"

Keywords().from_str("""
priority(1,show("priority/2 is a keywords allowing to add an order, the higher the priority,")).
show("hello").
show(root).
show(pass_arg(pass_arg(trace))).
""")

print()
class Keywords(cloc.Cloc):
    def __init__(self) -> None:
        super().__init__()
        self.count = 0
        self._ignore_key_words = True

    def show(self,arg):
        return arg

    def priority(self,n,other):
        print(f"Arg {n} has nothing to do with the priority keyword, neither for")
        print(other)

# With the self._ignore_key_words parameters set to true, keywords will be ignored 
Keywords().from_str("""
priority(1,show(root)).
""")

print()
class Keywords(cloc.Cloc):
    def __init__(self) -> None:
        super().__init__()
        self.count = 0
        self._ignore_key_words = False
        self._keys.remove("priority")


    def show(self,arg):
        return arg

    def priority(self,n,other):
        print(f"Arg {n} has nothing to do with the priority keyword, BUT ")
        print(other)

# You can ignore specific keywords by using self._keys.remove(<keywords>)
Keywords().from_str("""
priority(1,show(root)).
""")