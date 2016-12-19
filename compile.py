# -*- coding: utf-8 -*-
try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension

from Cython.Distutils import build_ext


ext_modules = [
    Extension("config", ["config.py"]),
    #     Extension("utils", ["utils.py"]),
    #     Extension("logger", ["logger.py"]),
    #     Extension("services.screenshoter", ["services/screenshoter.py"]),
    #     Extension("services.collector", ["services/collector.py"]),
    #     Extension("services.scripter", ["services/scripter.py"]),
    #     Extension("services.uploader", ["services/uploader.py"]),
]

setup(
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules
)
