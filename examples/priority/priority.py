import cloc


class Priority(cloc.Cloc):
    def __init__(self) -> None:
        super().__init__()

    def show(self,arg):
        print(arg)




p = Priority()

p.from_str("""
priority(#inf,show("First in the file, but last in computing")).
priority(last,show("last or 'last', put it on last priority")).
priority(4,show("Not first in the file, but also last in computing")).
priority(1, show("Priority can be used to start process after others, for instance printing a graph after getting all of the data")).
show("Last in file but first in output").
""")

