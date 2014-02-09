#! /usr/bin/env python
# -*- coding: utf-8 -*-

#===============================================================================
# logging
#===============================================================================

from django.conf import settings
from logging import getLogger

logger = getLogger()

def debug(msg = '', *largs, **kwargs):
    ''' Helper para log.log( logging.DEBUG , msg)
    inspirado en console.log de Firebug :) '''

    if type(msg) == str and msg.count('%s') and largs:
        msg = msg % tuple(largs)
        # Impresion de vars
    elif largs or kwargs:
        if largs:
            msg = msg and u'%s, ' % msg or ''
            msg = u'%s%s' % (msg, u', '.join(map(unicode, largs)))

        if kwargs:
            msg = msg and u'%s, ' % msg or u''
            msg = u'%s%s' % (msg, u', '.join(map( lambda k_v: u'%s = %s' % k_v,
                                       kwargs.items())))

    logger.log(logging.DEBUG, msg)

