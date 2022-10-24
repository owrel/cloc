import cloc

class Greeting:
    def __init__(self,greets) -> None:
        self.greets = greets


class HelloWorld(cloc.Cloc):
    def __init__(self) -> None:
        super().__init__()
        
    def bonjour(self,arg1):
        return arg1

    def hello(self,greets):
        print("Greetings with object Greeting")
        return Greeting(greets)

    def hallo(self,arg1,arg2):
        print('Hallo')



h = HelloWorld()
print(h.from_str("bonjour(1). bonjour(2). bonjour(hi). hello('hi'). hallo(1,2)."))


# Output
# Greetings with object Greeting
# Hallo
# [1, 2, 'hi', <__main__.Greeting object at 0x7f1719b6d840>]