# -*- coding: utf-8 -*-

import sys
import os
# call parent folder.
parent_paths = [__file__]
for _ in range(2):
    parent_paths.append(os.path.abspath(
            os.path.join(os.path.dirname(parent_paths[-1]), '..')))
    if not(parent_paths[-1] in sys.path):
        sys.path.insert(0, parent_paths[-1])


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