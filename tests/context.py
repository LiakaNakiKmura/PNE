# -*- coding: utf-8 -*-

from pathlib import Path
import sys
import os

# call parent folder.

depth_of_parents = 2
'''
This is the parameter of depth of adding path of parents foleder. If this is 
set as 2, add paths of parent and parent's parent folder path.

0 is the folder where file exists. 
'''

module_path = Path(os.path.abspath(__file__))
for i in range(depth_of_parents):
    if not(str(module_path.parents[i]) in sys.path):
        sys.path.insert(0, str(module_path.parents[i]))

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