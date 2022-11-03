import cloc

class AnyObject:
    object_instance_count = 0
    def __init__(self,any_parameter) -> None:
        AnyObject.object_instance_count +=1
        self.id = AnyObject.object_instance_count
        self.parameter = any_parameter



class ReferenceTable(cloc.Cloc):
    def __init__(self) -> None:
        super().__init__()


    def createAny(self,arg):
        return AnyObject(arg)


    def show(self, ao):
        print("Parameter:", ao.parameter)


rt = ReferenceTable()
rt.from_str("""
show(createAny("You")).
createAny("Me").
createAny("You").
createAny("You").
""")


print(rt._memoize_call)
print(AnyObject.object_instance_count)
print()
AnyObject.object_instance_count = 0

class ReferenceTable(cloc.Cloc):
    def __init__(self) -> None:
        super().__init__()
        self._use_memoize_for_function = False


    def createAny(self,arg):
        return AnyObject(arg)


    def show(self, ao):
        print("Parameter:", ao.parameter)


rt = ReferenceTable()
rt.from_str("""
createAny("Me").
createAny("You").
createAny("You").
show(createAny("You")).
""")

print(rt._memoize_call)
print(AnyObject.object_instance_count)
print()