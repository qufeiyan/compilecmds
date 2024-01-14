"""
ccjson
===================
generate a compilation database for make-based build systems.

features:
1. Support for redundent build systems that use shell scripts to nest make.
2. Simpler to use than similiar tools without losing compilation information.
3. Open source, you can modify it according to the actual build situation.

"""

from src import command, parser, reader, writer
from src.__meta__ import __version__
