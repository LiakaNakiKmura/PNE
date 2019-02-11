# -*- coding: utf-8 -*-

from pathlib import Path
import sys

# call parent folder.

depth_of_parents = 2
'''
This is the parameter of depth of adding path of parents foleder. If this is 
set as 2, add paths of parent and parent's parent folder path.
'''

adding_path = Path(__file__)
for _ in range(depth_of_parents):
    adding_path=adding_path.parent
    if not(str(adding_path) in sys.path):
        sys.path.insert(0, str(adding_path))

import src

'''
This is needed when test module import files in the "src" folder placed parent
folder.

Ex.
if test module improted this file as following way.
      from .context import src

Then the src folder is called and sub files can be accessed in importing test
file.
'''