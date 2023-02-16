import sys, importlib
sys.modules[__name__] = importlib.import_module('.Config', __name__).Config()
