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

from rpclib.server.wsgi import WsgiApplication
import logging
logging.basicConfig(level=logging.DEBUG)

import unittest

from rpclib.application import Application
from rpclib.decorator import srpc
from rpclib.model.primitive import Integer
from rpclib.model.primitive import String
from rpclib.model.complex import ComplexModel
from rpclib.interface.wsdl import Wsdl11
from rpclib.protocol.http import HttpRpc
from rpclib.service import ServiceBase
from rpclib.server.wsgi import WsgiApplication
from rpclib.server.wsgi import WsgiMethodContext

class Test(unittest.TestCase):
    '''Most of the service tests are performed through the interop tests.'''

    def test_multiple_return(self):
        class SomeNotSoComplexModel(ComplexModel):
            s = String

        class SomeService(ServiceBase):
            @srpc(_returns=[Integer, String])
            def some_call():
                return 1, 's'

        app = Application([SomeService], 'tns', HttpRpc(), HttpRpc(), Wsdl11())
        server = WsgiApplication(app)

        initial_ctx = WsgiMethodContext(server, {
            'QUERY_STRING': '',
            'PATH_INFO': '/some_call',
            'QUERY_STRING': '?s=a',
            'REQUEST_METHOD': 'GET',
        }, 'some-content-type')

        try:
            ctx, = server.generate_contexts(initial_ctx)
            server.get_in_object(ctx)
            server.get_out_object(ctx)
            server.get_out_string(ctx)
        except ValueError:
            pass
        else:
            raise Exception("Must fail with: HttpRpc does not support complex "
                "return types.")

    def test_primitive_only(self):
        class SomeComplexModel(ComplexModel):
            i = Integer
            s = String

        class SomeService(ServiceBase):
            @srpc(SomeComplexModel, _returns=SomeComplexModel)
            def some_call(scm):
                return SomeComplexModel(i=5, s='5x')

        app = Application([SomeService], 'tns', HttpRpc(), HttpRpc(), Wsdl11())
        server = WsgiApplication(app)

        initial_ctx = WsgiMethodContext(server, {
            'QUERY_STRING': '',
            'PATH_INFO': '/some_call',
            'REQUEST_METHOD': 'GET',
        }, 'some-content-type')
        ctx, = server.generate_contexts(initial_ctx)

        server.get_in_object(ctx)
        server.get_out_object(ctx)
        try:
            server.get_out_string(ctx)
        except:
            pass
        else:
            raise Exception("Must fail with: HttpRpc does not support complex "
                "return types.")

    def test_complex(self):
        class CM(ComplexModel):
            i = Integer
            s = String

        class CCM(ComplexModel):
            c = CM
            i = Integer
            s = String

        class SomeService(ServiceBase):
            @srpc(CCM, _returns=CCM)
            def some_call(ccm):
                return CCM(c=ccm.c, i=ccm.i, s=ccm.s)

        app = Application([SomeService], 'tns', HttpRpc(), HttpRpc(), Wsdl11())
        server = WsgiApplication(app)
        initial_ctx = WsgiMethodContext(server, {
            'QUERY_STRING': '',
            'PATH_INFO': '/some_call',
            'REQUEST_METHOD': 'GET',
        }, 'some-content-type')
        ctx, = server.generate_contexts(initial_ctx)
        server.get_in_object(ctx)
        server.get_out_object(ctx)
        server.get_out_string(ctx)

    def test_multiple(self):
        class SomeService(ServiceBase):
            @srpc(String(max_occurs='unbounded'), _returns=String)
            def some_call(s):
                return '\n'.join(s)

        app = Application([SomeService], 'tns', HttpRpc(), HttpRpc(), Wsdl11())
        server = WsgiApplication(app)

        initial_ctx = WsgiMethodContext(server, {
            'QUERY_STRING': 's=1&s=2',
            'PATH_INFO': '/some_call',
            'REQUEST_METHOD': 'GET',
        }, 'some-content-type')

        ctx, = server.generate_contexts(initial_ctx)
        server.get_in_object(ctx)
        server.get_out_object(ctx)
        server.get_out_string(ctx)

        assert ctx.out_string == ['1\n2']

    def test_nested_flatten(self):
        class CM(ComplexModel):
            i = Integer
            s = String

        class CCM(ComplexModel):
            c = CM
            i = Integer
            s = String

        class SomeService(ServiceBase):
            @srpc(CCM, _returns=String)
            def some_call(ccm):
                return repr(ccm)

        app = Application([SomeService], 'tns', HttpRpc(), HttpRpc(), Wsdl11())
        server = WsgiApplication(app)

        initial_ctx = WsgiMethodContext(server, {
            'QUERY_STRING': 'ccm_i=1&ccm_s=s&ccm_c_i=3&ccm_c_s=cs',
            'PATH_INFO': '/some_call',
            'REQUEST_METHOD': 'GET',
        }, 'some-content-type')

        ctx, = server.generate_contexts(initial_ctx)

        server.get_in_object(ctx)
        assert ctx.in_error is None

        server.get_out_object(ctx)
        assert ctx.out_error is None

        server.get_out_string(ctx)

        print ctx.out_string
        assert ctx.out_string == ["CCM(i=1, c=CM(i=3, s='cs'), s='s')"]

    def test_nested_flatten_with_multiple_values_1(self):
        class CM(ComplexModel):
            i = Integer
            s = String

        class CCM(ComplexModel):
            c = CM
            i = Integer
            s = String

        class SomeService(ServiceBase):
            @srpc(CCM.customize(max_occurs=2), _returns=String)
            def some_call(ccm):
                return repr(ccm)

        app = Application([SomeService], 'tns', HttpRpc(), HttpRpc(), Wsdl11())
        server = WsgiApplication(app)

        initial_ctx = WsgiMethodContext(server, {
            'QUERY_STRING': 'ccm_i=1&ccm_s=s&ccm_c_i=3&ccm_c_s=cs',
            'PATH_INFO': '/some_call',
            'REQUEST_METHOD': 'GET',
        }, 'some-content-type')

        ctx, = server.generate_contexts(initial_ctx)

        try:
            server.get_in_object(ctx)
        except:
            pass
        else:
            raise Exception("Must fail with: Exception: HttpRpc deserializer "
                        "does not support non-primitives with max_occurs > 1")

    def test_nested_flatten_with_multiple_values_2(self):
        class CM(ComplexModel):
            i = Integer
            s = String

        class CCM(ComplexModel):
            c = CM.customize(max_occurs=2)
            i = Integer
            s = String

        class SomeService(ServiceBase):
            @srpc(CCM, _returns=String)
            def some_call(ccm):
                return repr(ccm)

        app = Application([SomeService], 'tns', HttpRpc(), HttpRpc(), Wsdl11())
        server = WsgiApplication(app)

        initial_ctx = WsgiMethodContext(server, {
            'QUERY_STRING': 'ccm_i=1&ccm_s=s&ccm_c_i=3&ccm_c_s=cs',
            'PATH_INFO': '/some_call',
            'REQUEST_METHOD': 'GET',
        }, 'some-content-type')

        ctx, = server.generate_contexts(initial_ctx)

        try:
            server.get_in_object(ctx)
        except:
            pass
        else:
            raise Exception("Must fail with: Exception: HttpRpc deserializer "
                        "does not support non-primitives with max_occurs > 1")

if __name__ == '__main__':
    unittest.main()
