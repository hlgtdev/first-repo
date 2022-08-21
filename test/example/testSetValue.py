#!/usr/bin/python3
import os
XMPG_HOME = os.getenv('XMPG_HOME')

import sys
sys.path.append('%s/xmprog/core' % XMPG_HOME)

from Example import *

import unittest

class SetValueTest(unittest.TestCase):

    def setUp(self):

        self.maxDiff = None

        self.xmp = Example()
    #___________________________________________________________________________
    #
    def test_setValue_ref_None_accessor_default_value_None(self):

        newRef = self.xmp.setValue()

        self.assertTrue(newRef.startswith('REF_'))
        self.assertEqual(
            {
                newRef : None
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_default_accessor_dot_slash_idValue_value_None(self):

        accessor    = './idValue'

        newRef = self.xmp.setValue(accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : None
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_default_accessor_idValue_value_None(self):

        accessor    = '/idValue'

        newRef = self.xmp.setValue(accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : None
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_idValue_accessor_default_value_None(self):

        ref         = 'idValue'

        returnedRef = self.xmp.setValue(ref=ref)

        self.assertEqual(ref, returnedRef)
        self.assertEqual(
            {
                'idValue' : None
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_default_accessor_idValue_slash_a_value_None(self):

        accessor    = '/idValue/a'

        newRef = self.xmp.setValue(accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : {
                    'a' : None
                }
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_idValue_accessor_dot_slash_a_value_None(self):

        ref         = 'idValue'
        accessor    = './a'

        newRef = self.xmp.setValue(ref=ref, accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : {
                    'a' : None
                }
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_idValue_accessor_slash_a_value_None(self):

        ref         = 'idValue'
        accessor    = '/a'

        newRef = self.xmp.setValue(ref=ref, accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : {
                    'a' : None
                }
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_idValue_accessor_a_value_None(self):

        ref         = 'idValue'
        accessor    = 'a'

        newRef = self.xmp.setValue(ref=ref, accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : {
                    'a' : None
                }
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_default_accessor_idValue_slash_a_slash_b_value_None(self):

        accessor    = '/idValue/a/b'

        newRef = self.xmp.setValue(accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : {
                    'a' : {
                        'b' : None
                    }
                }
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_idValue_accessor_dot_slash_a_slash_b_value_None(self):

        ref         = 'idValue'
        accessor    = './a/b'

        newRef = self.xmp.setValue(ref=ref, accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : {
                    'a' : {
                        'b' : None
                    }
                }
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_idValue_accessor_slash_a_slash_b_value_None(self):

        ref         = 'idValue'
        accessor    = '/a/b'

        newRef = self.xmp.setValue(ref=ref, accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : {
                    'a' : {
                        'b' : None
                    }
                }
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_idValue_accessor_a_slash_b_value_None(self):

        ref         = 'idValue'
        accessor    = 'a/b'

        newRef = self.xmp.setValue(ref=ref, accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : {
                    'a' : {
                        'b' : None
                    }
                }
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_default_accessor_idValue_slash_a_slash_c_value_None(self):

        self.xmp.repository = {
                'idValue' : {
                    'a' : {
                        'b' : None
                    }
                }
            }
        accessor    = '/idValue/a/c'

        newRef = self.xmp.setValue(accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : {
                    'a' : {
                        'b' : None,
                        'c' : None,
                    }
                }
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_idValue_accessor_dot_slash_a_slash_c_value_None(self):

        self.xmp.repository = {
                'idValue' : {
                    'a' : {
                        'b' : None
                    }
                }
            }
        ref         = 'idValue'
        accessor    = './a/c'

        newRef = self.xmp.setValue(ref=ref, accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : {
                    'a' : {
                        'b' : None,
                        'c' : None,
                    }
                }
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_idValue_accessor_slash_a_slash_c_value_None(self):

        self.xmp.repository = {
                'idValue' : {
                    'a' : {
                        'b' : None
                    }
                }
            }
        ref         = 'idValue'
        accessor    = '/a/c'

        newRef = self.xmp.setValue(ref=ref, accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : {
                    'a' : {
                        'b' : None,
                        'c' : None,
                    }
                }
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_idValue_accessor_a_slash_c_value_None(self):

        self.xmp.repository = {
                'idValue' : {
                    'a' : {
                        'b' : None
                    }
                }
            }
        ref         = 'idValue'
        accessor    = 'a/c'

        newRef = self.xmp.setValue(ref=ref, accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : {
                    'a' : {
                        'b' : None,
                        'c' : None,
                    }
                }
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_idValue_accessor_a_slash_b_slash_c_value_None(self):

        self.xmp.repository = {
                'idValue' : {
                    'a' : {
                        'b' : None
                    }
                }
            }
        ref         = 'idValue'
        accessor    = 'a/b/c'

        newRef = self.xmp.setValue(ref=ref, accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : {
                    'a' : {
                        'b' : {
                            'c' : None,
                        }
                    }
                }
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_default_accessor_idValue_slash_zero_value_zero(self):

        accessor    = '/idValue/0'
        value       = 0

        newRef = self.xmp.setValue(accessor=accessor, value=value)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : [
                    0
                ]
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_default_accessor_idValue_slash_zero_slash_zero_value_zero(self):

        accessor    = '/idValue/0/0'
        value       = 0

        newRef = self.xmp.setValue(accessor=accessor, value=value)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : [
                    [
                        0
                    ]
                ]
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_default_accessor_idValue_slash_one_slash_one_value_zero(self):

        accessor    = '/idValue/1/1'
        value       = 1

        newRef = self.xmp.setValue(accessor=accessor, value=value)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : [
                    None,
                    [
                        None,
                        1
                    ]
                ]
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_default_accessor_idValue_slash_one_then_zero_then_two_value_one_then_zero_then_two(self):

        newRef = self.xmp.setValue(accessor='/idValue/1', value=1)
        newRef = self.xmp.setValue(accessor='/idValue/2', value=2)
        newRef = self.xmp.setValue(accessor='/idValue/0', value=0)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : [
                    0,
                    1,
                    2,
                ]
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_default_accessor_idValue_slash_one_then_zero_then_two_slash_ditto_value_one_then_zero_then_two(self):

        newRef = self.xmp.setValue(accessor='/idValue/1/1', value=1)
        newRef = self.xmp.setValue(accessor='/idValue/2/2', value=2)
        newRef = self.xmp.setValue(accessor='/idValue/0/0', value=0)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : [
                    [
                        0,
                    ],
                    [
                        None,
                        1,
                    ],
                    [
                        None,
                        None,
                        2,
                    ],
                ]
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_default_accessor_idValue_slash_zero_slash_a_then_b_then_c_value_zero_then_one_then_two(self):

        newRef = self.xmp.setValue(accessor='/idValue/0/a', value=0)
        newRef = self.xmp.setValue(accessor='/idValue/0/b', value=1)
        newRef = self.xmp.setValue(accessor='/idValue/0/c', value=2)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : [
                    {
                        'a' : 0,
                        'b' : 1,
                        'c' : 2,
                    }
                ]
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_default_accessor_idValue_slash_one_slash_zero_slash_a_then_b_then_c_value_zero_then_one_then_two(self):

        newRef = self.xmp.setValue(accessor='/idValue/1/0/a', value=0)
        newRef = self.xmp.setValue(accessor='/idValue/1/0/b', value=1)
        newRef = self.xmp.setValue(accessor='/idValue/1/0/c', value=2)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : [
                    None,
                    [
                        {
                            'a' : 0,
                            'b' : 1,
                            'c' : 2,
                        }
                    ]
                ]
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_dict_accessor_default_value_None(self):

        ref = self.xmp.repository

        newRef = self.xmp.setValue(ref=ref)

        self.assertTrue(newRef.startswith('REF_'))
        self.assertEqual(
            {
                newRef : None
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_dict_accessor_idValue_value_None(self):

        ref         = self.xmp.repository
        accessor    = './idValue'

        newRef = self.xmp.setValue(ref=ref, accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : None
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setValue_ref_dict_accessor_slash_b_value_None(self):

        subDict     = {
                'a' : None
            }
        self.xmp.repository = {
                'idValue' : subDict
            }
        ref         = subDict
        accessor    = '/b'

        newRef = self.xmp.setValue(ref=ref, accessor=accessor)

        self.assertEqual(None, newRef)
        self.assertEqual(
            {
                'idValue' : {
                    'a'  : None,
                    'b'  : None,
                }
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
if __name__ == '__main__':
    t = SetValueTest()
    t.setUp()
    t.test_setValue_ref_default_accessor_idValue_slash_zero_slash_a_then_b_then_c_value_zero_then_one_then_two()
