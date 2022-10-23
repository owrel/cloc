from typing import Any, List
from clingo.ast import *
import clingo
from clingo import Symbol, SymbolType
import math
import types



class UnreferencedSupplierConsumer(Exception):
    pass


class UnreferencedFunction(Exception):
    pass


class WrongKeyWordCall(Exception):
    pass


class WrongPriorityFormat(Exception):
    pass






class Cloc:
    def __init__(self) -> None:
        # Behaviour
        self._convert_unreferenced_supplier_consumer_to_str = True
        self._ignore_key_words = False
        self._skip_on_unreferenced_function = False
        self._skip_on_unreferenced_supplier_consumer = False
        self._use_reference_table_for_procedure = True
        self._use_reference_table_for_function = True

        # Informations/debug info
        self._show_warning_consumer = True
        self._show_warning_procedure = True
        self._show_warning_on_skip = True
        self._warning_on_unreferenced_supplier_conversion = True

        # Properties
        self._reference_table = {}
        self._reference_table_call = {}
        self._keys = ["root", "trace", "priority"]
        self._reference_table_symbol_name_ignore: List[str] = []
        self._delayed_calls: List[DelayedCall] = []

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
                if 'head' in ast.child_keys and 'body' in ast.child_keys:
                    if ast.head and not ast.body:
                        symbol = clingo.symbol.parse_term(
                            str(ast.head.atom.symbol))
                        r = self._execute(obj=self, symbol=symbol, trace=[])
                        if r:
                            ret.append(r)

        self._delayed_calls = sorted(
            self._delayed_calls, key=lambda dcall: dcall.priority, reverse=False)

        for dc, dc_i in zip(self._delayed_calls, range(len(self._delayed_calls))):
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
            new_trace.append(symbol.name)
            if symbol.name in obj._keys and not obj._ignore_key_words:
                if symbol.name == "root":
                    if symbol.arguments:
                        raise WrongKeyWordCall(
                            f"Key `root' should not be call with arguments, expected:  self, found {symbol}")
                    else:
                        return obj

                if symbol.name == "trace":
                    if symbol.arguments:
                        raise WrongKeyWordCall(
                            f"Key `trace' should not be call with arguments, expected:  trace, found {symbol}")
                    else:
                        return new_trace

                if symbol.name == "priority":
                    if not symbol.arguments:
                        raise WrongKeyWordCall(
                            f"Key `priority' should be call with 2 arguments, expected:  priority(int+|\"last\",symbol), found {symbol}")
                    else:

                        d = DelayedCall(
                            obj=obj, symbol=symbol.arguments[1], trace=new_trace, priority=symbol.arguments[0])

                        obj._delayed_calls.append(d)
                        return d

            elif obj._exist(obj, symbol.name):
                if symbol.arguments:
                    args_list = []
                    for arg in symbol.arguments:
                        args_list.append(obj._execute(
                            obj=obj, symbol=arg, trace=new_trace))

                    args_str = obj._args_to_str(args_list, "args_list")
                    call_str = f"obj.{symbol.name}({args_str})"
                    if self._use_reference_table_for_function and not symbol.name in obj._reference_table_symbol_name_ignore:
                        key = obj._get_key_from_symbol(symbol)
                        if key in obj._reference_table:
                            obj._reference_table_call[key] += 1
                            return obj._reference_table[key]
                        else:
                            obj._reference_table[key] = eval(call_str)
                            obj._reference_table_call[key] = 1
                            return obj._reference_table[key]
                    else:
                        return eval(call_str)
                else:
                    bound = eval(f"obj.{symbol.name}")
                    if isinstance(bound, types.MethodType):
                        if obj._use_reference_table_for_procedure and not symbol.name in obj._reference_table_symbol_name_ignore:
                            key = obj._get_key_from_symbol(symbol)
                            if key in obj._reference_table :
                                ret = obj._reference_table[key]
                                obj._reference_table_call[key] += 1
                            else:
                                obj._reference_table[key] = eval(
                                    f"obj.{symbol.name}()")
                                obj._reference_table_call[key] = 1
                                ret = obj._reference_table[key]
                        else:
                            ret = f"obj.{symbol.name}()"
                    else:
                        ret = bound

                    if not ret and obj._show_warning_procedure:
                        print(
                            f"WARNING: procedure {symbol.name} identified")
                    return ret

            else:
                if symbol.arguments:  # unreferenced function case
                    if obj._skip_on_unreferenced_function:
                        print(
                            f"WARNING: Skipping unreferenced symbol {symbol.name}/{len(symbol.arguments)} ")
                        return None
                    else:
                        raise UnreferencedFunction(
                            f"Function {symbol.name}/{len(symbol.arguments)} is not referenced")
                else:  # unreferenced consumer/supplier case
                    if obj._convert_unreferenced_supplier_consumer_to_str:
                        if obj._warning_on_unreferenced_supplier_conversion:
                            print(
                                f"WARNING: converting {symbol.name} to string")
                        return symbol.name
                    else:
                        if obj._skip_on_unreferenced_supplier_consumer:
                            print(
                                f"WARNING: Skipping unreferenced symbol {symbol.name}/{len(symbol.arguments)} ")
                            return None
                        else:
                            raise UnreferencedSupplierConsumer(
                                f"Supplier/consumer {symbol.name}/{len(symbol.arguments)}  is not referenced")

        elif symbol.type == SymbolType.Number:
            return symbol.number
        elif symbol.type == SymbolType.String:
            return symbol.string
        elif symbol.type == SymbolType.Infimum:
            return math.inf
        else:
            print(f"Don't know how to handle {symbol.type}: {symbol}")

    def _get_key_from_symbol(self, symbol: Symbol):
        key = str(symbol)
        return key

    def _args_to_str(self, args: List, var_name: str) -> str:
        args_str = ""
        for index in range(len(args)):
            args_str += f"{var_name}[{index}],"

        return args_str[:-1]

    def _exist(self, obj, fun_name: str) -> bool:
        ret = True
        try:
            eval(f"obj.{fun_name}")
        except:
            ret = False

        return ret



class DelayedCall:
    def __init__(self, obj: Cloc, symbol: Symbol, trace: List, priority: Symbol) -> None:
        self.obj = obj
        self.symbol = symbol
        self.trace = trace
        self._result_computed = False
        if priority.type == SymbolType.Number:
            self.priority = priority.number
        elif priority.type == SymbolType.Function:
            if priority.arguments:
                raise WrongPriorityFormat(
                    f"Priority level symbol format should be: positive integer, \"last\", last. Found {priority}")
            else:
                if priority.name != "last":
                    raise WrongPriorityFormat(
                        f"Priority level symbol name should be: last. Found {priority}")
                else:
                    self.priority = math.inf
        elif priority.type == SymbolType.Number:
            num = priority.number
            if num <= 0:
                raise WrongPriorityFormat(
                    f"Priority level symbol should be positive integer. Found {priority.number}")
            else:
                self.priority = num

        elif priority.type == SymbolType.Infimum:
            self.priority = math.inf

        elif priority.type == SymbolType.String:
            if priority.string != "last":
                raise WrongPriorityFormat(
                    f"Priority level symbol name should be: last. Found {priority.string}")
            else:
                self.priority = math.inf

        else:
            raise WrongPriorityFormat(
                f"Priority symbol type should be: Symbol.String, Symbol.Function, Symbol.Infimum. Found {priority.type}")

    def execute(self):
        ret = self.obj._execute(
            obj=self.obj, symbol=self.symbol, trace=self.trace)
        self.result = ret
        self._result_computed = True
        return ret

    def __call__(self) -> Any:
        if self._result_computed:
            return self.result
        else:
            return self

