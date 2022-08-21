#!/usr/bin/python3
import os
XMPG_HOME = os.getenv('XMPG_HOME')

import sys
sys.path.append('%s/xmprog/core' % XMPG_HOME)

from Example import *

import unittest

class GetValueTest(unittest.TestCase):

    def setUp(self):

        self.maxDiff = None

        self.xmp = Example()
    #___________________________________________________________________________
    #
    def test_getValue_ref_default_accessor_dot_slash_integer_default_default(self):

        self.xmp.repository = {
                'integer' : 1
            }
        accessor    = './integer'

        value = self.xmp.getValue(accessor=accessor)

        self.assertEqual(1, value)
    #___________________________________________________________________________
    #
    def test_getValue_ref_default_accessor_slash_integer_default_default(self):

        self.xmp.repository = {
                'integer' : 1
            }
        accessor    = '/integer'

        value = self.xmp.getValue(accessor=accessor)

        self.assertEqual(1, value)
    #___________________________________________________________________________
    #
    def test_getValue_ref_default_accessor_integer_default_default(self):

        self.xmp.repository = {
                'integer' : 1
            }
        accessor    = 'integer'

        value = self.xmp.getValue(accessor=accessor)

        self.assertEqual(1, value)
    #___________________________________________________________________________
    #
    def test_getValue_ref_default_accessor_integers_slash_1_default_default(self):

        self.xmp.repository = {
                'integers' : [
                    0,
                    10,
                    20
                ]
            }
        accessor    = 'integers/1'

        value = self.xmp.getValue(accessor=accessor)

        self.assertEqual(10, value)
    #___________________________________________________________________________
    #
    def test_getValue_ref_default_accessor_integers_slash_unknownThird_default_default(self):

        self.xmp.repository = {
                'integers' : [
                    0,
                    10,
                    20
                ]
            }
        accessor    = 'integers/3'

        with self.assertRaises(ValueError) as context:
            value = self.xmp.getValue(accessor=accessor)

        self.assertTrue("INDICE [3] DE L'ACCESSOR [integers/3] NON TROUVE" in str(context.exception))
    #___________________________________________________________________________
    #
    def test_getValue_ref_default_accessor_integers_slash_d_slash_2_default_default(self):

        self.xmp.repository = {
                'integers' : [
                    0,
                    10,
                    20
                ]
            }
        accessor    = 'integers/d/2'

        with self.assertRaises(ValueError) as context:
            value = self.xmp.getValue(accessor=accessor)

        self.assertTrue("INDICE [d] DE L'ACCESSOR [integers/d/2] INCORRECT" in str(context.exception))
    #___________________________________________________________________________
    #
    def test_getValue_ref_default_accessor_integers_slash_d_slash_2_default_999(self):

        self.xmp.repository = {
                'integers' : [
                    0,
                    10,
                    20
                ]
            }
        accessor    = 'integers/d/2'
        default     = 999

        with self.assertRaises(ValueError) as context:
            value = self.xmp.getValue(accessor=accessor, default=default)

        self.assertTrue("INDICE [d] DE L'ACCESSOR [integers/d/2] INCORRECT" in str(context.exception))
    #___________________________________________________________________________
    #
    def test_getValue_ref_default_accessor_integers_slash_2_slash_d_default_default(self):

        self.xmp.repository = {
                'integers' : [
                    0,
                    10,
                    20
                ]
            }
        accessor    = 'integers/2/d'

        with self.assertRaises(ValueError) as context:
            value = self.xmp.getValue(accessor=accessor)

        self.assertTrue("ELEMENT [d] DE L'ACCESSOR [integers/2/d] NON TROUVE" in str(context.exception))
    #___________________________________________________________________________
    #
    def test_getValue_ref_default_accessor_integers_slash_2_slash_d_default_999(self):

        self.xmp.repository = {
                'integers' : [
                    0,
                    10,
                    20
                ]
            }
        accessor    = 'integers/2/d'
        default     = 999

        value = self.xmp.getValue(accessor=accessor, default=default)

        self.assertEqual(default, value)
    #___________________________________________________________________________
    #
    def test_getValue_ref_default_accessor_integers_slash_unknownThird_default_999(self):

        self.xmp.repository = {
                'integers' : [
                    0,
                    10,
                    20
                ]
            }
        accessor    = 'integers/3'
        default     = 999

        value = self.xmp.getValue(accessor=accessor, default=default)

        self.assertEqual(default, value)
    #___________________________________________________________________________
    #
    def test_getValue_ref_default_accessor_dot_slash_unknown_default_default(self):

        self.xmp.repository = {
            }
        accessor    = './unknown'

        with self.assertRaises(ValueError) as context:
            value = self.xmp.getValue(accessor=accessor)

        self.assertTrue("CLE [unknown] DE L'ACCESSOR [./unknown] NON TROUVEE" in str(context.exception))
    #___________________________________________________________________________
    #
    def test_getValue_ref_default_accessor_dot_slash_unknown_default_DEFAULT(self):

        self.xmp.repository = {
            }
        accessor    = './unknown'
        default     = 'DEFAULT'

        value = self.xmp.getValue(accessor=accessor, default=default)

        self.assertEqual(default, value)
    #___________________________________________________________________________
    #
    def test_getValue_ref_str_accessor_default_default_default(self):

        self.xmp.repository = {
                'integer' : 1
            }
        ref         = 'integer'

        value = self.xmp.getValue(ref=ref)

        self.assertEqual(1, value)
    #___________________________________________________________________________
    #
    def test_getValue_ref_dict_accessor_integer_default_default(self):

        self.xmp.repository = {
                'integer' : 1
            }
        ref         = self.xmp.repository
        accessor    = 'integer'

        value = self.xmp.getValue(ref=ref, accessor=accessor)

        self.assertEqual(1, value)
    #___________________________________________________________________________
    #
    def test_getValue_ref_dict_accessor_dot_slash_unknown_default_default(self):

        self.xmp.repository = {
            }
        ref         = self.xmp.repository
        accessor    = './unknown'

        with self.assertRaises(ValueError) as context:
            value = self.xmp.getValue(ref=ref, accessor=accessor)

        self.assertTrue("CLE [unknown] DE L'ACCESSOR [./unknown] NON TROUVEE" in str(context.exception))
    #___________________________________________________________________________
    #
    def test_getValue_ref_dict_accessor_dot_slash_unknown_default_DEFAULT(self):

        self.xmp.repository = {
            }
        ref         = self.xmp.repository
        accessor    = './unknown'
        default     = 'DEFAULT'

        value = self.xmp.getValue(ref=ref, accessor=accessor, default=default)

        self.assertEqual(default, value)
    #___________________________________________________________________________
    #
    def test_getValue_many_cases(self):

        self.xmp.repository = {
                'v1' : 'a',
                'v2' : 1,
                'v3' : 2.3,
                'v4' : {
                    'attr1' : 'b',
                    'attr2' : 2,
                    'attr3' : 3.4
                },
                'v5' : [
                    10,
                    20,
                    30,
                ]
            }

        self.assertEqual('a',
            self.xmp.getValue(ref='v1'))
        self.assertEqual(1,
            self.xmp.getValue(ref='v2'))
        self.assertEqual(2.3,
            self.xmp.getValue(ref='v3'))
        self.assertEqual('b',
            self.xmp.getValue(ref='v4', accessor='./attr1'))
        self.assertEqual(2,
            self.xmp.getValue(ref='v4', accessor='./attr2'))
        self.assertEqual(3.4,
            self.xmp.getValue(ref='v4', accessor='./attr3'))
        self.assertEqual(10,
            self.xmp.getValue(ref='v5', accessor='./0'))
        self.assertEqual(20,
            self.xmp.getValue(ref='v5', accessor='./1'))
        self.assertEqual(30,
            self.xmp.getValue(ref='v5', accessor='./2'))
    #___________________________________________________________________________
    #
if __name__ == '__main__':
    t = GetValueTest()
    t.setUp()
    t.test_getValue_ref_default_accessor_integers_slash_d_slash_2_default_999()
