# Cloc

Cloc (CLingo Object Caller) is a Python library for converting ASP facts, that can come from a [Clingo](https://github.com/potassco/clingo) output into Python call(s). It can help build workflow tools. For large project, [CLORM](https://github.com/potassco/clorm) might be a more featured/reliable library.

## Installation

Import the Github [repository](https://github.com/Owrel/cloc.git)

```bash
git clone https://github.com/Owrel/cloc.gits
```

In the project folder, install Cloc with pip:
```bash
pip install .
```
## Usage
```python
import cloc

class HelloWorld(cloc.Cloc):
    def __init__(self) -> None:
        super().__init__()
    def hello(self):
        print("HelloWorld")

h = HelloWorld()
h.from_str("hello.")
# Output: HelloWorld
```

More examples available [here](https://github.com/Owrel/cloc/tree/master/examples)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

