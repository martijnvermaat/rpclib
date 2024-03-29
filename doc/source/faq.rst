
**********
Rpclib FAQ
**********

Frequently asked questions about rpclib and related libraries.

Does rpclib support the SOAP 1.2 standard?
==========================================

**Short answer:** No.

**Long answer:** Nope.

Patches are welcome.

How do I implement a predefined WSDL?
=====================================

**Short answer:** By hand.

**Long answer:** This is not a strength of rpclib, which is more oriented toward
implementing services from scratch. It does not have any functionality to parse
an existing WSDL document to produce the necessary Python classes and method
stubs.

Patches are welcome. You can start by adapting the WSDL parser from
`RSL <http://rsl.sf.net>`_.

Is it possible to use other decorators with @rpc/@srpc?
=======================================================

**Short answer:** Yes, but just use events. See the :ref:`manual-user-manager`
tutorial and the `events example <http://github.com/arskom/rpclib/blob/master/examples/user_manager/server_basic.py>`_
to learn how to do so. They work almost the same, except for the syntax.

**Long Answer:** Here's the magic from the :mod:`rpclib.decorator`: ::

    argcount = f.func_code.co_argcount
    param_names = f.func_code.co_varnames[arg_start:argcount]

So if ``f`` is your decorator, its signature should be the same as the user method,
otherwise the parameter names and numbers in the interface are going to be wrong,
which will cause weird errors.

Please note that if you just intend to have a convenient way to set additional
method metadata, you can use the ``_udp`` argument to the :func:`rpclib.decorator.srpc`
to your liking.

So if you're hell bent on using decorators, you should use the `decorator package <http://pypi.python.org/pypi/decorator/>`_.
Here's an example: ::

    from decorator import decorator

    def _do_something(func, *args, **kw):
        print "before call"
        result = func(*args, **kw)
        print "after call"
        return result

    def my_decor(f):
        return decorator(_do_something, f)

    class tests(ServiceBase):
        @my_decor
        @srpc(ComplexTypes.Integer, _returns=ComplexTypes.Integer)
        def testf(first):
            return first

Note that the place of the decorator matters. Putting it before ``@srpc`` will
make it run once, on service initialization. Putting it after will make it run
every time the method is called, but not on initialization.

Original thread: http://mail.python.org/pipermail/soap/2011-September/000565.html

PS: The next faq entry is also probably relevant to you.

How do I alter the behaviour of a user method without using decorators?
=======================================================================

``ctx.function`` contains the handle to the original function. You
can set that attribute to arbitrary callables to prevent the original user
method from running. This property is initiallized from
``ctx.descriptor.function`` every time a new context is initialized.

If for some reason you need to alter the ``ctx.descriptor.function``,
you can call :func:`ctx.descriptor.reset_function()` to restore it to its
original value.

Also consider thread-safety issues when altering global state.

How do I use variable names that are also python keywords?
==========================================================

Due to restrictions of the python language, you can't do this:

    class SomeClass(ComplexModel):
        and = String
        or = Integer
        import = Datetime

The workaround is as follows:

    class SomeClass(ComplexModel):
        _type_info = {
            'and': String
            'or': Integer
            'import': Datetime
        }

You also can't do this:

    @rpc(String, String, String, _returns=String)
    def f(ctx, from, import):
        return '1234'

The workaround is as follows:

    @rpc(String, String, String, _returns=String,
        _in_variable_names={'_from': 'from',
            '_import': 'import'},
        _out_variable_name="return"
    def f(ctx, _from, _import):
        return '1234'

See here: https://github.com/arskom/rpclib/blob/rpclib-2.5.0-beta/src/rpclib/test/test_service.py#L114

How does rpclib behave in a multi-threaded environment?
=======================================================

Rpclib code is re-entrant, thus mostly thread safe. (A notable exception to
this rule is the Interface clasess which cache the document string once
generated.) Whatever global state that is accessed is initialized and frozen
(by convention) before any rpc processing is performed.

The transport implementations (i.e. the code in client and server packages) or
the user code are responsible for assuring thread-safety when accessing any
out-of-thread data. No other parts of rpclib should be made aware of threads.

What implications does Rpclib's license (LGPL) have for proprietary projects that use it?
========================================================================================

DISCLAIMER: This is not legal advice, but just how we think things should work.

**Short Answer:** As long as you don't modify Rpclib itself, you can freely use
Rpclib in your commercial projects, without any additional obligations.

**Long Answer:** If you do modifications to Rpclib, the best thing to do is to
put them on github and just send a pull request upstream. Even if your patch
is not accepted, you've done everything the license requires you to do.

If you make modifications to Rpclib and deploy a modified version to your
client's site, the minimum you should do is to pass along the source code for
the modified Rpclib to your clients. Again, you can just put your modifications
up somewhere, or better, send them to the Rpclib maintainers, but if for some
reason (we can't imagine any, to be honest) you can't do this, your obligation
is to have your client have the source code with your modifications.

The thing to watch out for when distributing a modified Rpclib version as
part of your proprieatry solution is to make sure that Rpclib runs just fine by
itself without needing your code. Again, this will be the case if you did not
touch Rpclib code itself.

If your modifications to Rpclib make it somehow dependant on your software, you
must pass your modifications as well as the code that Rpclib needs to the
people who deploy your solution. In other words, if your code and Rpclib is
tightly coupled, the license of Rpclib propagates to your code as well.

Rpclib is a descendant of Soaplib, which was published by its author initially
under LGPL. When he quit, the people who took over contemplated re-licensing it
under the three-clause BSD license, but were not able to reach the original
author. A re-licensing is now even less probable today because of the number of
people who've contributed code in the past years as we'd need to get the
approval of every single person in order to re-license Rpclib.

It's also not possible to offer Rpclib under a dual license model for the same
reason -- everybody would have to approve the new licensing terms.
