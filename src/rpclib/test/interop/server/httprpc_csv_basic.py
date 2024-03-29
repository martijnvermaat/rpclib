#!/usr/bin/env python
#
# rpclib - Copyright (C) Rpclib contributors.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('rpclib.protocol.xml')
logger.setLevel(logging.DEBUG)

from rpclib.application import Application
from rpclib.interface.wsdl import Wsdl11
from rpclib.protocol.csv import OutCsv
from rpclib.protocol.http import HttpRpc
from rpclib.server.wsgi import WsgiApplication
from rpclib.test.interop.server._service import services

httprpc_csv_application = Application(services,
        'rpclib.test.interop.server.httprpc.csv', HttpRpc(), OutCsv(), Wsdl11())

if __name__ == '__main__':
    try:
        from wsgiref.simple_server import make_server
        from wsgiref.validate import validator

        wsgi_application = WsgiApplication(httprpc_csv_application)
        server = make_server('0.0.0.0', 9755, validator(wsgi_application))

        logger.info('Starting interop server at %s:%s.' % ('0.0.0.0', 9755))
        logger.info('WSDL is at: /?wsdl')
        server.serve_forever()

    except ImportError:
        print("Error: example server code requires Python >= 2.5")
