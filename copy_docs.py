# -*- coding: utf-8 -*-
#
# This script updates the docs based on the latest and greatet build.

import shutil

shutil.rmtree('CodeChat/Doc', True)
shutil.copytree('_build/html', 'CodeChat/Doc')