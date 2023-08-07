from .logging import basicConfig, getLogger, INFO

"""
Setup basic log configuration.
"""
basicConfig(level=INFO)
log = getLogger("test")
