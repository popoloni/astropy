"""
ULTRA-AGGRESSIVE DEBUG message suppression module.
This module completely blocks ALL debug/info/warning messages at the source.
Import this FIRST before any other modules.
"""

import logging
import os
import sys

# Set environment variables BEFORE any imports
os.environ['KIVY_LOG_LEVEL'] = 'critical'
os.environ['MPLBACKEND'] = 'Agg'  # Use non-interactive matplotlib backend
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['MPLCONFIGDIR'] = '/tmp'  # Prevent matplotlib config issues

# Completely disable matplotlib logging BEFORE it gets imported
import matplotlib
matplotlib.set_loglevel('CRITICAL')

# Also set matplotlib rcParams to prevent font manager debug messages
matplotlib.rcParams['font.family'] = 'DejaVu Sans'  # Use a common font to avoid searches
matplotlib.rcParams['font.serif'] = 'DejaVu Serif'
matplotlib.rcParams['font.sans-serif'] = 'DejaVu Sans'
matplotlib.rcParams['font.monospace'] = 'DejaVu Sans Mono'

# Disable verbose font searching
matplotlib.rcParams['font.size'] = 10
matplotlib.rcParams['axes.unicode_minus'] = False

# Override matplotlib's font manager to disable debug output completely
import matplotlib.font_manager as fm
original_findfont = fm.findfont

def silent_findfont(*args, **kwargs):
    # Completely disable all logging during font finding
    old_loggers = {}
    logger_names = ['matplotlib.font_manager', 'matplotlib.findfont', 'matplotlib']
    
    for name in logger_names:
        logger = logging.getLogger(name)
        old_loggers[name] = logger.level
        logger.setLevel(logging.CRITICAL)
        logger.disabled = True
    
    try:
        result = original_findfont(*args, **kwargs)
    finally:
        # Keep them disabled
        for name in logger_names:
            logger = logging.getLogger(name)
            logger.setLevel(logging.CRITICAL)
            logger.disabled = True
    return result

fm.findfont = silent_findfont

# Also disable font manager's internal debugging
try:
    fm._log.setLevel(logging.CRITICAL)
    fm._log.disabled = True
except:
    pass

# Create a null handler that discards everything
class NullHandler(logging.Handler):
    def emit(self, record):
        pass  # Discard all messages

# Create an error-only handler
class ErrorOnlyHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            print(f"{record.levelname}: {record.getMessage()}")

# Completely override the root logger
root_logger = logging.getLogger()
root_logger.handlers.clear()
root_logger.addHandler(ErrorOnlyHandler())
root_logger.setLevel(logging.ERROR)

# Disable basicConfig to prevent any other logging configuration
def disabled_basicConfig(*args, **kwargs):
    pass

logging.basicConfig = disabled_basicConfig

# Override all logging methods at the module level
def null_function(*args, **kwargs):
    pass

logging.debug = null_function
logging.info = null_function
logging.warning = null_function

# Override all logging methods at the Logger class level
logging.Logger.debug = null_function
logging.Logger.info = null_function
logging.Logger.warning = null_function

# List of all loggers to completely disable
DISABLE_LOGGERS = [
    'matplotlib',
    'matplotlib.font_manager',
    'matplotlib.findfont', 
    'matplotlib.backends',
    'matplotlib.pyplot',
    'matplotlib.figure',
    'matplotlib.axes',
    'matplotlib.fontmanager',
    'matplotlib.ticker',
    'matplotlib.patches',
    'PIL',
    'PIL.Image',
    'PIL.PngImagePlugin',
    'kivy',
    'kivy.logger',
    'kivy.factory',
    'kivy.graphics',
    'kivy.core',
    'kivy.clock',
    'fontTools',
    'fontTools.subset',
    'asyncio'
]

# Completely disable these loggers
for logger_name in DISABLE_LOGGERS:
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()
    logger.addHandler(NullHandler())
    logger.setLevel(logging.CRITICAL)
    logger.disabled = True
    logger.propagate = False

# Override the getLogger function to return neutered loggers for specific names
original_getLogger = logging.getLogger

def neutered_getLogger(name=None):
    logger = original_getLogger(name)
    if name and any(suppress in name for suppress in DISABLE_LOGGERS):
        logger.handlers.clear()
        logger.addHandler(NullHandler())
        logger.setLevel(logging.CRITICAL)
        logger.disabled = True
        logger.propagate = False
    return logger

logging.getLogger = neutered_getLogger

print("ULTRA-AGGRESSIVE DEBUG suppression activated - only ERROR+ messages allowed") 