#!/usr/bin/python3
import os
XMPG_HOME = os.getenv('XMPG_HOME')

import sys
sys.path.append('%s/xmprog/core' % XMPG_HOME)

from Example import *

import unittest

class ShowValueTest(unittest.TestCase):

    def setUp(self):

        self.maxDiff = None

        self.xmp = Example()
    #___________________________________________________________________________
    #
    def test_showValue_ref_default_accessor_default(self):

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

        lines = self.xmp.showValue(silent=True)

        self.assertEqual([
                '. (dict) {* : 5',
                './v1 (str) : a',
                './v2 (int) : 1',
                './v3 (float) : 2.3',
                './v4 (dict) {* : 3',
                './v4/attr1 (str) : b',
                './v4/attr2 (int) : 2',
                './v4/attr3 (float) : 3.4',
                './v5 (list) [* : 3',
                './v5/0 (int) : 10',
                './v5/1 (int) : 20',
                './v5/2 (int) : 30'
            ], lines)
    #___________________________________________________________________________
    #
if __name__ == '__main__':
    t = ShowValueTest()
    t.setUp()
    t.test_showValue_ref_default_accessor_default()
