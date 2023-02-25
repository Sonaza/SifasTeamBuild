import os, pkgutil, importlib

__all__ = list(module for _, module, _ in pkgutil.iter_modules([os.path.dirname(__file__)]))

FileProcessors = {}
for _processor_name in __all__:
	FileProcessors[_processor_name] = importlib.import_module('.' + _processor_name, __name__)
	locals()[_processor_name] = getattr(FileProcessors[_processor_name], _processor_name)
