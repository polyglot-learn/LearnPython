"""`importlib` — loading modules by name, at runtime.

`import x` is compiled into a call to the import machinery. `importlib` exposes
that machinery, which is what plugin systems, lazy imports of heavy
dependencies, and optional-feature detection are built on.

`import_module` respects `sys.modules`, so a second call is free. `reload` is
for development only: existing references still point at the old objects.
"""

import importlib
import importlib.util
import sys
import types


def optional(name: str):
    """Import a module if present, otherwise return None."""
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError:
        return None


def is_available(name: str) -> bool:
    """Check without importing — find_spec only locates the module."""
    return importlib.util.find_spec(name) is not None


def make_module(name: str, source: str) -> types.ModuleType:
    """Build a module object from source text, no file involved."""
    module = types.ModuleType(name)
    module.__dict__["__name__"] = name
    exec(compile(source, f"<{name}>", "exec"), module.__dict__)
    sys.modules[name] = module
    return module


def main() -> None:
    math_mod = importlib.import_module("math")
    print(f"import_module('math').sqrt(81) = {math_mod.sqrt(81)}")

    # Import a submodule and pull one name out of it, by string.
    path_mod = importlib.import_module("os.path")
    print(f"os.path.join via string import: {path_mod.join('a', 'b')}")

    print(f"is_available('json')     -> {is_available('json')}")
    print(f"is_available('numpy')    -> {is_available('numpy')}")
    print(f"optional('nonexistent')  -> {optional('nonexistent_module_xyz')}")

    # A module built at runtime behaves like any other.
    plugin = make_module(
        "runtime_plugin",
        "NAME = 'runtime'\n"
        "def run(x):\n"
        "    return x * 3\n",
    )
    print(f"generated module: {plugin.NAME}, run(7) = {plugin.run(7)}")
    print(f"importable by name now: {importlib.import_module('runtime_plugin') is plugin}")

    # The cache is what makes repeat imports free.
    print(f"'math' cached: {'math' in sys.modules}")
    print(f"same object every time: {importlib.import_module('math') is math_mod}")

    # Plugin dispatch: map a config string to a callable.
    registry = {"upper": "str.upper", "strip": "str.strip"}

    def resolve(dotted: str):
        module_name, _, attr = dotted.rpartition(".")
        owner = importlib.import_module("builtins") if module_name == "str" else None
        target = getattr(owner, "str") if owner else importlib.import_module(module_name)
        return getattr(target, attr)

    print(f"resolved 'str.upper'('hi') -> {resolve(registry['upper'])('hi')}")

    print(f"loaded modules: {len(sys.modules)}")


if __name__ == "__main__":
    main()
