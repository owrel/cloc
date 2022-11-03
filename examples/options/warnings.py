import cloc

class Warnings(cloc.Cloc):
    def __init__(self) -> None:
        super().__init__()
        self._warning_on_procedure                              = True # Default = True
        self._warning_on_unreferenced_symbol_conversion       = True # Default = True

    def warning_procedure(self):
        print("I return nothing")


Warnings().from_str("""
warning_procedure().
warning_symbol_conversion.
""")


print()

class Warnings(cloc.Cloc):
    def __init__(self) -> None:
        super().__init__()
        self._skip_on_unreferenced_function                     = True  # Default = False
        self._skip_on_unreferenced_symbol            = True  # Default = False
        self._convert_unreferenced_symbol_to_str     = False # Default = True

        self._warning_on_skip_unreferenced_function             = True  # Default = False
        self._warning_on_skip_unreferenced_symbol    = True  # Default = False



Warnings().from_str("""
warning_unreferenced_function(hello).
warning_symbol_conversion.
""")