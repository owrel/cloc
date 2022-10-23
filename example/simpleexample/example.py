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

    def hallo(self,_):
        print('Hallo')



h = HelloWorld()
print(h.from_file("bonjour(1). bonjour(2). bonjour(bonjour). hello('hi')"))

