#!/usr/bin/env python
# encoding: utf-8
"""
Tests for IPython.utils.traitlets.

Authors:

* Brian Granger
* Enthought, Inc.  Some of the code in this file comes from enthought.traits
  and is licensed under the BSD license.  Also, many of the ideas also come
  from enthought.traits even though our implementation is very different.
"""

#-----------------------------------------------------------------------------
#  Copyright (C) 2008-2009  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

from unittest import TestCase

from IPython.utils.traitlets import (
    HasTraits, MetaHasTraits, TraitType, Any,
    Int, Float, Complex, Str, TraitError,
    Undefined, Type, This, Instance, TCPAddress
)


#-----------------------------------------------------------------------------
# Helper classes for testing
#-----------------------------------------------------------------------------


class HasTraitsStub(HasTraits):

    def _notify_trait(self, name, old, new):
        self._notify_name = name
        self._notify_old = old
        self._notify_new = new


#-----------------------------------------------------------------------------
# Test classes
#-----------------------------------------------------------------------------


class TestTraitType(TestCase):

    def test_get_undefined(self):
        class A(HasTraits):
            a = TraitType
        a = A()
        self.assertEquals(a.a, Undefined)

    def test_set(self):
        class A(HasTraitsStub):
            a = TraitType

        a = A()
        a.a = 10
        self.assertEquals(a.a, 10)
        self.assertEquals(a._notify_name, 'a')
        self.assertEquals(a._notify_old, Undefined)
        self.assertEquals(a._notify_new, 10)

    def test_validate(self):
        class MyTT(TraitType):
            def validate(self, inst, value):
                return -1
        class A(HasTraitsStub):
            tt = MyTT
        
        a = A()
        a.tt = 10
        self.assertEquals(a.tt, -1)

    def test_default_validate(self):
        class MyIntTT(TraitType):
            def validate(self, obj, value):
                if isinstance(value, int):
                    return value
                self.error(obj, value)
        class A(HasTraits):
            tt = MyIntTT(10)
        a = A()
        self.assertEquals(a.tt, 10)

        # Defaults are validated when the HasTraits is instantiated
        class B(HasTraits):
            tt = MyIntTT('bad default')
        self.assertRaises(TraitError, B)

    def test_is_valid_for(self):
        class MyTT(TraitType):
            def is_valid_for(self, value):
                return True
        class A(HasTraits):
            tt = MyTT

        a = A()
        a.tt = 10
        self.assertEquals(a.tt, 10)

    def test_value_for(self):
        class MyTT(TraitType):
            def value_for(self, value):
                return 20
        class A(HasTraits):
            tt = MyTT

        a = A()
        a.tt = 10
        self.assertEquals(a.tt, 20)

    def test_info(self):
        class A(HasTraits):
            tt = TraitType
        a = A()
        self.assertEquals(A.tt.info(), 'any value')

    def test_error(self):
        class A(HasTraits):
            tt = TraitType
        a = A()
        self.assertRaises(TraitError, A.tt.error, a, 10)

    def test_dynamic_initializer(self):
        class A(HasTraits):
            x = Int(10)
            def _x_default(self):
                return 11
        class B(A):
            x = Int(20)
        class C(A):
            def _x_default(self):
                return 21

        a = A()
        self.assertEquals(a._trait_values, {})
        self.assertEquals(list(a._trait_dyn_inits.keys()), ['x'])
        self.assertEquals(a.x, 11)
        self.assertEquals(a._trait_values, {'x': 11})
        b = B()
        self.assertEquals(b._trait_values, {'x': 20})
        self.assertEquals(list(a._trait_dyn_inits.keys()), ['x'])
        self.assertEquals(b.x, 20)
        c = C()
        self.assertEquals(c._trait_values, {})
        self.assertEquals(list(a._trait_dyn_inits.keys()), ['x'])
        self.assertEquals(c.x, 21)
        self.assertEquals(c._trait_values, {'x': 21})
        # Ensure that the base class remains unmolested when the _default
        # initializer gets overridden in a subclass.
        a = A()
        c = C()
        self.assertEquals(a._trait_values, {})
        self.assertEquals(list(a._trait_dyn_inits.keys()), ['x'])
        self.assertEquals(a.x, 11)
        self.assertEquals(a._trait_values, {'x': 11})



class TestHasTraitsMeta(TestCase):

    def test_metaclass(self):
        self.assertEquals(type(HasTraits), MetaHasTraits)

        class A(HasTraits):
            a = Int

        a = A()
        self.assertEquals(type(a.__class__), MetaHasTraits)
        self.assertEquals(a.a,0)
        a.a = 10
        self.assertEquals(a.a,10)

        class B(HasTraits):
            b = Int()

        b = B()
        self.assertEquals(b.b,0)
        b.b = 10
        self.assertEquals(b.b,10)

        class C(HasTraits):
            c = Int(30)

        c = C()
        self.assertEquals(c.c,30)
        c.c = 10
        self.assertEquals(c.c,10)

    def test_this_class(self):
        class A(HasTraits):
            t = This()
            tt = This()
        class B(A):
            tt = This()
            ttt = This()
        self.assertEquals(A.t.this_class, A)
        self.assertEquals(B.t.this_class, A)
        self.assertEquals(B.tt.this_class, B)
        self.assertEquals(B.ttt.this_class, B)

class TestHasTraitsNotify(TestCase):

    def setUp(self):
        self._notify1 = []
        self._notify2 = []

    def notify1(self, name, old, new):
        self._notify1.append((name, old, new))

    def notify2(self, name, old, new):
        self._notify2.append((name, old, new))

    def test_notify_all(self):

        class A(HasTraits):
            a = Int
            b = Float

        a = A()
        a.on_trait_change(self.notify1)
        a.a = 0
        self.assertEquals(len(self._notify1),0)
        a.b = 0.0
        self.assertEquals(len(self._notify1),0)
        a.a = 10
        self.assert_(('a',0,10) in self._notify1)
        a.b = 10.0
        self.assert_(('b',0.0,10.0) in self._notify1)
        self.assertRaises(TraitError,setattr,a,'a','bad string')
        self.assertRaises(TraitError,setattr,a,'b','bad string')
        self._notify1 = []
        a.on_trait_change(self.notify1,remove=True)
        a.a = 20
        a.b = 20.0
        self.assertEquals(len(self._notify1),0)

    def test_notify_one(self):

        class A(HasTraits):
            a = Int
            b = Float

        a = A()
        a.on_trait_change(self.notify1, 'a')
        a.a = 0
        self.assertEquals(len(self._notify1),0)
        a.a = 10
        self.assert_(('a',0,10) in self._notify1)
        self.assertRaises(TraitError,setattr,a,'a','bad string')

    def test_subclass(self):

        class A(HasTraits):
            a = Int

        class B(A):
            b = Float

        b = B()
        self.assertEquals(b.a,0)
        self.assertEquals(b.b,0.0)
        b.a = 100
        b.b = 100.0
        self.assertEquals(b.a,100)
        self.assertEquals(b.b,100.0)

    def test_notify_subclass(self):

        class A(HasTraits):
            a = Int

        class B(A):
            b = Float

        b = B()
        b.on_trait_change(self.notify1, 'a')
        b.on_trait_change(self.notify2, 'b')
        b.a = 0
        b.b = 0.0
        self.assertEquals(len(self._notify1),0)
        self.assertEquals(len(self._notify2),0)
        b.a = 10
        b.b = 10.0
        self.assert_(('a',0,10) in self._notify1)
        self.assert_(('b',0.0,10.0) in self._notify2)

    def test_static_notify(self):

        class A(HasTraits):
            a = Int
            _notify1 = []
            def _a_changed(self, name, old, new):
                self._notify1.append((name, old, new))

        a = A()
        a.a = 0
        # This is broken!!!
        self.assertEquals(len(a._notify1),0)
        a.a = 10
        self.assert_(('a',0,10) in a._notify1)

        class B(A):
            b = Float
            _notify2 = []
            def _b_changed(self, name, old, new):
                self._notify2.append((name, old, new))

        b = B()
        b.a = 10
        b.b = 10.0
        self.assert_(('a',0,10) in b._notify1)
        self.assert_(('b',0.0,10.0) in b._notify2)

    def test_notify_args(self):

        def callback0():
            self.cb = ()
        def callback1(name):
            self.cb = (name,)
        def callback2(name, new):
            self.cb = (name, new)
        def callback3(name, old, new):
            self.cb = (name, old, new)

        class A(HasTraits):
            a = Int

        a = A()
        a.on_trait_change(callback0, 'a')
        a.a = 10
        self.assertEquals(self.cb,())
        a.on_trait_change(callback0, 'a', remove=True)

        a.on_trait_change(callback1, 'a')
        a.a = 100
        self.assertEquals(self.cb,('a',))
        a.on_trait_change(callback1, 'a', remove=True)

        a.on_trait_change(callback2, 'a')
        a.a = 1000
        self.assertEquals(self.cb,('a',1000))
        a.on_trait_change(callback2, 'a', remove=True)

        a.on_trait_change(callback3, 'a')
        a.a = 10000
        self.assertEquals(self.cb,('a',1000,10000))
        a.on_trait_change(callback3, 'a', remove=True)

        self.assertEquals(len(a._trait_notifiers['a']),0)


class TestHasTraits(TestCase):

    def test_trait_names(self):
        class A(HasTraits):
            i = Int
            f = Float
        a = A()
        self.assertEquals(a.trait_names(),['i','f'])

    def test_trait_metadata(self):
        class A(HasTraits):
            i = Int(config_key='MY_VALUE')
        a = A()
        self.assertEquals(a.trait_metadata('i','config_key'), 'MY_VALUE')

    def test_traits(self):
        class A(HasTraits):
            i = Int
            f = Float
        a = A()
        self.assertEquals(a.traits(), dict(i=A.i, f=A.f))

    def test_traits_metadata(self):
        class A(HasTraits):
            i = Int(config_key='VALUE1', other_thing='VALUE2')
            f = Float(config_key='VALUE3', other_thing='VALUE2')
            j = Int(0)
        a = A()
        self.assertEquals(a.traits(), dict(i=A.i, f=A.f, j=A.j))
        traits = a.traits(config_key='VALUE1', other_thing='VALUE2')
        self.assertEquals(traits, dict(i=A.i))

        # This passes, but it shouldn't because I am replicating a bug in 
        # traits.
        traits = a.traits(config_key=lambda v: True)
        self.assertEquals(traits, dict(i=A.i, f=A.f, j=A.j))

    def test_init(self):
        class A(HasTraits):
            i = Int()
            x = Float()
        a = A(i=1, x=10.0)
        self.assertEquals(a.i, 1)
        self.assertEquals(a.x, 10.0)

#-----------------------------------------------------------------------------
# Tests for specific trait types
#-----------------------------------------------------------------------------


class TestType(TestCase):

    def test_default(self):

        class B(object): pass
        class A(HasTraits):
            klass = Type

        a = A()
        self.assertEquals(a.klass, None)

        a.klass = B
        self.assertEquals(a.klass, B)
        self.assertRaises(TraitError, setattr, a, 'klass', 10)

    def test_value(self):

        class B(object): pass
        class C(object): pass
        class A(HasTraits):
            klass = Type(B)
        
        a = A()
        self.assertEquals(a.klass, B)
        self.assertRaises(TraitError, setattr, a, 'klass', C)
        self.assertRaises(TraitError, setattr, a, 'klass', object)
        a.klass = B

    def test_allow_none(self):

        class B(object): pass
        class C(B): pass
        class A(HasTraits):
            klass = Type(B, allow_none=False)

        a = A()
        self.assertEquals(a.klass, B)
        self.assertRaises(TraitError, setattr, a, 'klass', None)
        a.klass = C
        self.assertEquals(a.klass, C)

    def test_validate_klass(self):

        class A(HasTraits):
            klass = Type('no strings allowed')

        self.assertRaises(ImportError, A)

        class A(HasTraits):
            klass = Type('rub.adub.Duck')

        self.assertRaises(ImportError, A)

    def test_validate_default(self):

        class B(object): pass
        class A(HasTraits):
            klass = Type('bad default', B)

        self.assertRaises(ImportError, A)

        class C(HasTraits):
            klass = Type(None, B, allow_none=False)

        self.assertRaises(TraitError, C)

    def test_str_klass(self):

        class A(HasTraits):
            klass = Type('IPython.utils.ipstruct.Struct')

        from IPython.utils.ipstruct import Struct
        a = A()
        a.klass = Struct
        self.assertEquals(a.klass, Struct)
        
        self.assertRaises(TraitError, setattr, a, 'klass', 10)

class TestInstance(TestCase):

    def test_basic(self):
        class Foo(object): pass
        class Bar(Foo): pass
        class Bah(object): pass
        
        class A(HasTraits):
            inst = Instance(Foo)

        a = A()
        self.assert_(a.inst is None)
        a.inst = Foo()
        self.assert_(isinstance(a.inst, Foo))
        a.inst = Bar()
        self.assert_(isinstance(a.inst, Foo))
        self.assertRaises(TraitError, setattr, a, 'inst', Foo)
        self.assertRaises(TraitError, setattr, a, 'inst', Bar)
        self.assertRaises(TraitError, setattr, a, 'inst', Bah())

    def test_unique_default_value(self):
        class Foo(object): pass
        class A(HasTraits):
            inst = Instance(Foo,(),{})

        a = A()
        b = A()
        self.assert_(a.inst is not b.inst)

    def test_args_kw(self):
        class Foo(object):
            def __init__(self, c): self.c = c
        class Bar(object): pass
        class Bah(object):
            def __init__(self, c, d):
                self.c = c; self.d = d

        class A(HasTraits):
            inst = Instance(Foo, (10,))
        a = A()
        self.assertEquals(a.inst.c, 10)

        class B(HasTraits):
            inst = Instance(Bah, args=(10,), kw=dict(d=20))
        b = B()
        self.assertEquals(b.inst.c, 10)
        self.assertEquals(b.inst.d, 20)

        class C(HasTraits):
            inst = Instance(Foo)
        c = C()
        self.assert_(c.inst is None)

    def test_bad_default(self):
        class Foo(object): pass

        class A(HasTraits):
            inst = Instance(Foo, allow_none=False)
        
        self.assertRaises(TraitError, A)

    def test_instance(self):
        class Foo(object): pass

        def inner():
            class A(HasTraits):
                inst = Instance(Foo())
        
        self.assertRaises(TraitError, inner)


class TestThis(TestCase):

    def test_this_class(self):
        class Foo(HasTraits):
            this = This

        f = Foo()
        self.assertEquals(f.this, None)
        g = Foo()
        f.this = g
        self.assertEquals(f.this, g)
        self.assertRaises(TraitError, setattr, f, 'this', 10)

    def test_this_inst(self):
        class Foo(HasTraits):
            this = This()
        
        f = Foo()
        f.this = Foo()
        self.assert_(isinstance(f.this, Foo))

    def test_subclass(self):
        class Foo(HasTraits):
            t = This()
        class Bar(Foo):
            pass
        f = Foo()
        b = Bar()
        f.t = b
        b.t = f
        self.assertEquals(f.t, b)
        self.assertEquals(b.t, f)

    def test_subclass_override(self):
        class Foo(HasTraits):
            t = This()
        class Bar(Foo):
            t = This()
        f = Foo()
        b = Bar()
        f.t = b
        self.assertEquals(f.t, b)
        self.assertRaises(TraitError, setattr, b, 't', f)

class TraitTestBase(TestCase):
    """A best testing class for basic trait types."""

    def assign(self, value):
        self.obj.value = value

    def coerce(self, value):
        return value

    def test_good_values(self):
        if hasattr(self, '_good_values'):
            for value in self._good_values:
                self.assign(value)
                self.assertEquals(self.obj.value, self.coerce(value))

    def test_bad_values(self):
        if hasattr(self, '_bad_values'):
            for value in self._bad_values:
                self.assertRaises(TraitError, self.assign, value)

    def test_default_value(self):
        if hasattr(self, '_default_value'):
            self.assertEquals(self._default_value, self.obj.value)


class AnyTrait(HasTraits):

    value = Any

class AnyTraitTest(TraitTestBase):

    obj = AnyTrait()

    _default_value = None
    _good_values   = [10.0, 'ten', 'ten', [10], {'ten': 10},(10,), None, 1j]
    _bad_values    = []


class IntTrait(HasTraits):

    value = Int(99)

class TestInt(TraitTestBase):

    obj = IntTrait()
    _default_value = 99
    _good_values   = [10, -10]
    _bad_values    = ['ten', 'ten', [10], {'ten': 10},(10,), None, 1j,
                      10.1, -10.1, '10L', '-10L', '10.1', '-10.1', '10L',
                      '-10L', '10.1', '-10.1',  '10', '-10', '10', '-10']


class FloatTrait(HasTraits):

    value = Float(99.0)

class TestFloat(TraitTestBase):

    obj = FloatTrait()

    _default_value = 99.0
    _good_values   = [10, -10, 10.1, -10.1]
    _bad_values    = ['ten', [10], {'ten': 10},(10,), None,
                      1j, '10', '-10', '10L', '-10L', '10.1', '-10.1', '10',
                      '-10', '10L', '-10L', '10.1', '-10.1']


class ComplexTrait(HasTraits):

    value = Complex(99.0-99.0j)

class TestComplex(TraitTestBase):

    obj = ComplexTrait()

    _default_value = 99.0-99.0j
    _good_values   = [10, -10, 10.1, -10.1, 10j, 10+10j, 10-10j, 
                      10.1j, 10.1+10.1j, 10.1-10.1j]
    _bad_values    = ['10L', '-10L', 'ten', [10], {'ten': 10},(10,), None]


class StringTrait(HasTraits):

    value = Str('string')

class TestString(TraitTestBase):

    obj = StringTrait()

    _default_value = 'string'
    _good_values   = ['10', '-10', '10L',
                      '-10L', '10.1', '-10.1', 'string']
    _bad_values    = [10, -10, 10.1, -10.1, 1j, [10],
                      ['ten'],{'ten': 10},(10,), None]


class TCPAddressTrait(HasTraits):

    value = TCPAddress()

class TestTCPAddress(TraitTestBase):

    obj = TCPAddressTrait()

    _default_value = ('127.0.0.1',0)
    _good_values = [('localhost',0),('192.168.0.1',1000),('www.google.com',80)]
    _bad_values = [(0,0),('localhost',10.0),('localhost',-1)]
