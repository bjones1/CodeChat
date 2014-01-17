# **********************************************************
# rthook_pyqt4.py - PyInstaller run-time hook file for PyQt4
# **********************************************************
# CodeChat uses the `v2 api <spi_api_2>`_. Tell PyInstaller about that, following
# the `recipe <http://www.pyinstaller.org/wiki/Recipe/PyQtChangeApiVersion>`_.

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
