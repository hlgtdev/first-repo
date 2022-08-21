#!/usr/bin/python3
import os
XMPG_HOME = os.getenv('XMPG_HOME')

import sys
sys.path.append('%s/xmprog/core' % XMPG_HOME)

from Example import *

import unittest

class SetObjectTest(unittest.TestCase):

    def setUp(self):

        self.maxDiff = None

        self.xmp = Example()
    #___________________________________________________________________________
    #
    def test_setObject_objectAsMap_dictWithClassAndId_idName_default_className_default(self):

        classe = 'my.new.package'
        id = 0
        objectAsMap = { '@class' : classe,
                'id'        : id,
                'string'    : 'a',
                'integer'   : 1,
            }

        ref = self.xmp.setObject(objectAsMap=objectAsMap)

        self.assertEqual(ref, '%s::%s' % (classe, id))
        self.assertEqual({
                '%s::%s' % (classe, id) : objectAsMap
            }, self.xmp.repository)
    #___________________________________________________________________________
    #
    def test_setObject_objectAsMap_dictWithoutClassAndId_idName_default_className_default(self):

        classe = 'my.new.package'
        id = 0
        objectAsMap = {
                'string'    : 'a',
                'integer'   : 1,
            }

        newRef = self.xmp.setObject(objectAsMap=objectAsMap)

        self.assertTrue(newRef.startswith('REF_'))
        self.assertEqual({
                newRef : objectAsMap
            }, self.xmp.repository)
