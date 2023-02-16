import os, pkgutil, importlib

__all__ = list(module for _, module, _ in pkgutil.iter_modules([os.path.dirname(__file__)]))
Generators = {}
for _generator_name in __all__:
    # Generators[_generator_name] = __import__(_generator_name, locals(), globals(), level=1)
    Generators[_generator_name] = importlib.import_module('.' + _generator_name, __name__) #, locals(), globals(), level=1)
