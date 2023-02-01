# Copyright (c) 2010-2022 Emmanuel Blot <emmanuel.blot@free.fr>
# Copyright (c) 2010-2016, Neotion
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

#pylint: disable-msg=missing-docstring

__version__ = '0.54.01'
__title__ = 'PyFtdi_mode'
__description__ = 'Askar.Liu modified FTDI device driver (pure Python)'
__uri__ = 'http://github.com/eblot/pyftdi'
__doc__ = __description__ + ' <' + __uri__ + '>'
__author__ = 'Askar.Liu, ori: Emmanuel Blot'
# For all support requests, please open a new issue on GitHub
__email__ = 'ori:emmanuel.blot@free.fr'
__license__ = 'Modified BSD'
__copyright__ = 'ori: Copyright (c) 2011-2021 Emmanuel Blot'


from logging import WARNING, NullHandler, getLogger


class FtdiLogger:

    log = getLogger('pyftdi')
    log.addHandler(NullHandler())
    log.setLevel(level=WARNING)

    @classmethod
    def set_formatter(cls, formatter):
        handlers = list(cls.log.handlers)
        for handler in handlers:
            handler.setFormatter(formatter)

    @classmethod
    def get_level(cls):
        return cls.log.getEffectiveLevel()

    @classmethod
    def set_level(cls, level):
        cls.log.setLevel(level=level)
