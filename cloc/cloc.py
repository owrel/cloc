from typing import Any, List, Tuple, Dict, Callable, Optional
from clingo.ast import AST, ProgramBuilder, parse_files, parse_string
import clingo
from clingo import Symbol, SymbolType
import math
import types


class UnreferencedSymbol(Exception):
    pass


class UnreferencedFunction(Exception):
    pass


class WrongKeyWordCall(Exception):
    pass


class WrongPriorityFormat(Exception):
    pass


class UnexpectedBehavior(Exception):
    pass


class Cloc:
    def __init__(self) -> None:
        # Behavior
        self._convert_unreferenced_symbol_to_str = True
        self._ignore_key_words = False
        self._skip_on_unreferenced_function = False
        self._skip_on_unreferenced_symbol = False
        self._use_memoize_for_symbol = True
        self._use_memoize_for_function = True

        self._use_default_on_unreferenced_function = False
        self._use_default_on_unreferenced_symbol = False

        # Information/debug info
        self._warning_on_procedure = True
        self._warning_on_skip_unreferenced_function = True
        self._warning_on_skip_unreferenced_symbol = True
        self._warning_on_unreferenced_symbol_conversion = True

        # Properties
        self._memoize: Dict[str, Any] = {}
        self._memoize_call: Dict[str, int] = {}
        self._keys = ["root", "trace", "priority"]
        self._memoize_symbol_name_ignore: List[str] = []
        self._delayed_calls: List["DelayedCall"] = []

    def from_str(self, str: str):
        ctl = clingo.Control()
        asts = []
        with ProgramBuilder(ctl) as _:
            parse_string(str, asts.append)

        return self._parse(asts)

    def from_file(self, path: str):
        ctl = clingo.Control()
        asts = []
        with ProgramBuilder(ctl) as _:
            parse_files([path], asts.append)

        return self._parse(asts)

    def _parse(self, asts: List[AST]) -> List[Any]:
        ret = []
        for ast in asts:
            if ast.child_keys:
                if "head" in ast.child_keys and "body" in ast.child_keys:
                    if ast.head and not ast.body:
                        symbol = clingo.symbol.parse_term(str(ast.head.atom.symbol))
                        r = self._execute(obj=self, symbol=symbol, trace=[])
                        if r:
                            ret.append(r)

        self._delayed_calls = sorted(
            self._delayed_calls, key=lambda dcall: dcall.priority, reverse=False
        )

        for dc_i, dc in enumerate(self._delayed_calls):
            mem_id = id(dc)
            dc = dc.execute()
            self._delayed_calls[dc_i] = dc
            for index in range(len(ret)):
                if id(ret[index]) == mem_id:
                    ret[index] = dc

        return ret

    def _execute(self, obj, symbol: Symbol, trace: List):
        new_trace = trace.copy()
        if symbol.type == SymbolType.Function:
            # Handle keywords
            if symbol.name in obj._keys and not obj._ignore_key_words:
                if symbol.name == "root":
                    if symbol.arguments:
                        raise WrongKeyWordCall(
                            f"Key `root' should not be call with arguments, expected:  self, found {symbol}"
                        )
                    else:
                        return obj

                if symbol.name == "trace":
                    if symbol.arguments:
                        raise WrongKeyWordCall(
                            f"Key `trace' should not be call with arguments, expected:  trace, found {symbol}"
                        )
                    else:
                        return new_trace

                if symbol.name == "priority":
                    if not symbol.arguments or len(symbol.arguments) != 2:
                        raise WrongKeyWordCall(
                            f'Key `priority\' should be call with 2 arguments, expected:  priority(int+|"last",symbol), found {symbol}'
                        )
                    else:
                        d = DelayedCall(
                            obj=obj,
                            symbol=symbol.arguments[1],
                            trace=new_trace,
                            priority=symbol.arguments[0],
                        )
                        obj._delayed_calls.append(d)
                        return d
            else:
                new_trace.append(symbol.name)
                if hasattr(obj, symbol.name):  # Using hasattr instead of _exist
                    if symbol.arguments:
                        # Build args list
                        args_list = []
                        for arg in symbol.arguments:
                            args_list.append(
                                obj._execute(obj=obj, symbol=arg, trace=new_trace)
                            )

                        # Check if we should memoize
                        if (
                            self._use_memoize_for_function
                            and symbol.name not in obj._memoize_symbol_name_ignore
                        ):
                            key = obj._get_key_from_symbol(symbol)
                            if key in obj._memoize:
                                obj._memoize_call[key] += 1
                                return obj._memoize[key]
                            else:
                                # Direct method call instead of eval
                                method = getattr(obj, symbol.name)
                                result = method(*args_list)
                                obj._memoize[key] = result
                                obj._memoize_call[key] = 1
                                return result
                        else:
                            # Direct method call without memoization
                            method = getattr(obj, symbol.name)
                            return method(*args_list)
                    else:
                        # No arguments case
                        attr = getattr(obj, symbol.name)
                        if isinstance(attr, types.MethodType):
                            if (
                                obj._use_memoize_for_symbol
                                and symbol.name not in obj._memoize_symbol_name_ignore
                            ):
                                key = obj._get_key_from_symbol(symbol)
                                if key in obj._memoize:
                                    ret = obj._memoize[key]
                                    obj._memoize_call[key] += 1
                                else:
                                    method = getattr(obj, symbol.name)
                                    ret = method()
                                    obj._memoize[key] = ret
                                    obj._memoize_call[key] = 1
                            else:
                                method = getattr(obj, symbol.name)
                                ret = method()
                        else:
                            ret = attr

                        if not ret and obj._warning_on_procedure:
                            print(
                                f"WARNING: procedure {symbol.name} (no return) identified"
                            )
                        return ret
                else:  # If unreferenced
                    if (
                        obj._skip_on_unreferenced_function
                        and obj._use_default_on_unreferenced_function
                    ):
                        print(
                            "WARNING: Incompatible behavior detected, <_skip_on_unreferenced_function = True> and <_use_default_on_unreferenced_function = True>, skipping..."
                        )
                    if symbol.arguments:  # unreferenced function case
                        if obj._skip_on_unreferenced_function:
                            if obj._warning_on_skip_unreferenced_function:
                                print(
                                    f"WARNING: Skipping unreferenced symbol {symbol.name}/{len(symbol.arguments)} (not recommended)"
                                )
                            return None
                        else:
                            if obj._use_default_on_unreferenced_function:
                                args_list = [symbol.name]
                                new_trace.append("default")
                                for arg in symbol.arguments:
                                    args_list.append(
                                        obj._execute(
                                            obj=obj, symbol=arg, trace=new_trace
                                        )
                                    )

                                # Check for memoization
                                if (
                                    self._use_memoize_for_function
                                    and symbol.name
                                    not in obj._memoize_symbol_name_ignore
                                ):
                                    key = f"default({str(args_list)})"
                                    if key in obj._memoize:
                                        obj._memoize_call[key] += 1
                                        return obj._memoize[key]
                                    else:
                                        result = obj.default(*args_list)
                                        obj._memoize[key] = result
                                        obj._memoize_call[key] = 1
                                        return result
                                else:
                                    return obj.default(*args_list)
                            raise UnreferencedFunction(
                                f"Function {symbol.name}/{len(symbol.arguments)} is not referenced"
                            )
                    else:  # unreferenced symbol/symbol case
                        if (
                            obj._skip_on_unreferenced_symbol
                            and obj._use_default_on_unreferenced_symbol
                        ):
                            print(
                                "WARNING: Incompatible behavior detected, <_skip_on_unreferenced_symbol = True> and <_use_default_on_unreferenced_symbol = True>, skipping..."
                            )

                        if (
                            obj._convert_unreferenced_symbol_to_str
                            and obj._use_default_on_unreferenced_symbol
                        ):
                            print(
                                "WARNING: Incompatible behavior detected, <_convert_unreferenced_symbol_to_str = True> and <_use_default_on_unreferenced_symbol = True>, skipping..."
                            )

                        if obj._convert_unreferenced_symbol_to_str:
                            if obj._warning_on_unreferenced_symbol_conversion:
                                print(f"WARNING: converting {symbol.name} to string")
                            return symbol.name
                        else:
                            if obj._skip_on_unreferenced_symbol:
                                if obj._warning_on_skip_unreferenced_symbol:
                                    print(
                                        f"WARNING: Skipping unreferenced symbol {symbol.name}/{len(symbol.arguments)}"
                                    )
                                return None
                            else:
                                if obj._use_default_on_unreferenced_symbol:
                                    new_trace.append("default")
                                    # Check for memoization
                                    if (
                                        self._use_memoize_for_function
                                        and symbol.name
                                        not in obj._memoize_symbol_name_ignore
                                    ):
                                        key = f"default('{symbol.name}')"
                                        if key in obj._memoize:
                                            obj._memoize_call[key] += 1
                                            return obj._memoize[key]
                                        else:
                                            result = obj.default(symbol.name)
                                            obj._memoize[key] = result
                                            obj._memoize_call[key] = 1
                                            return result
                                    else:
                                        return obj.default(symbol.name)

                                raise UnreferencedSymbol(
                                    f"symbol/symbol {symbol.name}/{len(symbol.arguments)}  is not referenced"
                                )

        elif symbol.type == SymbolType.Number:
            return symbol.number
        elif symbol.type == SymbolType.String:
            return symbol.string
        elif symbol.type == SymbolType.Infimum:
            return math.inf
        else:
            raise UnexpectedBehavior(
                f"""Don't know how to handle {symbol.type}: {symbol}, please report the the message on github issues:
            trace : {new_trace},
            symbol : {symbol}
            """
            )

    def _get_key_from_symbol(self, symbol: Symbol):
        # More efficient key generation
        if symbol.arguments:
            return f"{symbol.name}({','.join(str(arg) for arg in symbol.arguments)})"
        return symbol.name

    def _args_to_str(self, args: List, var_name: str) -> str:
        # Using join instead of string concatenation
        return ",".join(f"{var_name}[{i}]" for i in range(len(args)))

    def _exist(self, obj, fun_name: str) -> bool:
        # More efficient existence check
        return hasattr(obj, fun_name)

    def default(self, *args: Any, **kwds: Any):
        raise NotImplementedError("Should be override :)")


class DelayedCall:
    def __init__(
        self, obj: Cloc, symbol: Symbol, trace: List, priority: Symbol
    ) -> None:
        self.obj = obj
        self.symbol = symbol
        self.trace = trace
        self._result_computed = False

        # Handle priority determination
        if priority.type == SymbolType.Number:
            self.priority = priority.number
        elif priority.type == SymbolType.Function:
            if priority.arguments:
                raise WrongPriorityFormat(
                    f'Priority level symbol format should be: positive integer, "last", last. Found {priority}'
                )
            elif priority.name != "last":
                raise WrongPriorityFormat(
                    f"Priority level symbol name should be: last. Found {priority}"
                )
            else:
                self.priority = math.inf
        elif priority.type == SymbolType.Infimum:
            self.priority = math.inf
        elif priority.type == SymbolType.String:
            if priority.string != "last":
                raise WrongPriorityFormat(
                    f"Priority level symbol name should be: last. Found {priority.string}"
                )
            else:
                self.priority = math.inf
        else:
            raise WrongPriorityFormat(
                f"Priority symbol type should be: Symbol.String, Symbol.Function, Symbol.Infimum. Found {priority.type}"
            )

    def execute(self):
        ret = self.obj._execute(obj=self.obj, symbol=self.symbol, trace=self.trace)
        self.result = ret
        self._result_computed = True
        return ret

    def __call__(self) -> Any:
        if self._result_computed:
            return self.result
        else:
            return self
