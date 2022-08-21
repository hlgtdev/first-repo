#!/usr/bin/python3
import os
XMPG_HOME = os.getenv('XMPG_HOME')

import sys
sys.path.append('%s/xmprog/core' % XMPG_HOME)

from Example import *

import unittest

class FindAllTest(unittest.TestCase):

    def setUp(self):

        self.maxDiff = None

        self.xmp = Example()
    #___________________________________________________________________________
    #
    def test_findAll_ref_default_select_default_where_default(self):

        self.xmp.setObject({ '@class' : 'application.conception.Scenario',
                'id' : 1,
                'operations' : [
                    {
                        'name'          : 'Set',
                        'variable'      : 'a',
                        'value'         : 1,
                    },
                    {
                        'name'          : 'Set',
                        'variable'      : 'b',
                        'value'         : 2,
                    },
                    {
                        'name'          : 'Call',
                        'method'        : 'methode1',
                        'parameters'    : []
                    },
                ]
            })

        values = self.xmp.findAll()

        self.assertEqual({
                '.' : {
                    'application.conception.Scenario::1' : {
                        '@class'        : 'application.conception.Scenario',
                        'id'            : 1,
                        'operations'    : [
                            {
                                'name'          : 'Set',
                                'variable'      : 'a',
                                'value'         : 1
                            },
                            {
                                'name'          : 'Set',
                                'variable'      : 'b',
                                'value'         : 2
                            },
                            {
                                'name'          : 'Call',
                                'method'        : 'methode1',
                                'parameters'    : []
                            }
                        ]
                    }
                },
                './application.conception.Scenario::1'  : {
                    '@class'        : 'application.conception.Scenario',
                    'id'            : 1,
                    'operations'    : [
                        {
                            'name'          : 'Set',
                            'variable'      : 'a',
                            'value'         : 1
                        },
                        {
                            'name'          : 'Set',
                            'variable'      : 'b',
                            'value'         : 2
                        },
                        {
                            'name'          : 'Call',
                            'method'        : 'methode1',
                            'parameters'    : []
                        }
                    ]
                },
                './application.conception.Scenario::1/@class'       : 'application.conception.Scenario',
                './application.conception.Scenario::1/id'           : 1,
                './application.conception.Scenario::1/operations'   : [
                    {
                        'name'          : 'Set',
                        'variable'      : 'a',
                        'value'         : 1
                    },
                    {
                        'name'          : 'Set',
                        'variable'      : 'b',
                        'value'         : 2
                    },
                    {
                        'name'          : 'Call',
                        'method'        : 'methode1',
                        'parameters'    : []
                    }
                ],
                './application.conception.Scenario::1/operations/0' : {
                    'name'          : 'Set',
                    'variable'      : 'a',
                    'value'         : 1
                },
                './application.conception.Scenario::1/operations/0/name'        : 'Set',
                './application.conception.Scenario::1/operations/0/variable'    : 'a',
                './application.conception.Scenario::1/operations/0/value'       : 1,
                './application.conception.Scenario::1/operations/1'             : {
                    'name'          : 'Set',
                    'variable'      : 'b',
                    'value'         : 2
                },
                './application.conception.Scenario::1/operations/1/name'        : 'Set',
                './application.conception.Scenario::1/operations/1/variable'    : 'b',
                './application.conception.Scenario::1/operations/1/value'       : 2,
                './application.conception.Scenario::1/operations/2'             : {
                    'name'          : 'Call',
                    'method'        : 'methode1',
                    'parameters'    : []
                },
                './application.conception.Scenario::1/operations/2/name'        : 'Call',
                './application.conception.Scenario::1/operations/2/method'      : 'methode1',
                './application.conception.Scenario::1/operations/2/parameters'  : []
            }, values)
    #___________________________________________________________________________
    #
    def test_findAll_ref_default_select_operations_where_Call(self):

        self.xmp.setObject({ '@class' : 'application.conception.Scenario',
                'id' : 1,
                'operations' : [
                    {
                        'name'          : 'Set',
                        'variable'      : 'a',
                        'value'         : 1,
                    },
                    {
                        'name'          : 'Call',
                        'method'        : 'methode1',
                        'parameters'    : []
                    },
                    {
                        'name'          : 'Set',
                        'variable'      : 'b',
                        'value'         : 2,
                    },
                    {
                        'name'          : 'Call',
                        'method'        : 'methode2',
                        'parameters'    : []
                    },
                ]
            })

        values = self.xmp.findAll(select='.+/operations/\d+', where='name .* Call')

        self.assertEqual({
                './application.conception.Scenario::1/operations/1' : {
                    'name'          : 'Call',
                    'method'        : 'methode1',
                    'parameters'    : []
                },
                './application.conception.Scenario::1/operations/3' : {
                    'name'          : 'Call',
                    'method'        : 'methode2',
                    'parameters'    : []
                }
            }, values)
    #___________________________________________________________________________
    #
    def test_findAll_ref_scenario1_select_operations_where_Call(self):

        self.xmp.setObject({ '@class' : 'application.conception.Scenario',
                'id' : 1,
                'operations' : [
                    {
                        'name'          : 'Set',
                        'variable'      : 'a',
                        'value'         : 1,
                    },
                    {
                        'name'          : 'Call',
                        'method'        : 'methode1',
                        'parameters'    : []
                    },
                    {
                        'name'          : 'Set',
                        'variable'      : 'b',
                        'value'         : 2,
                    },
                    {
                        'name'          : 'Call',
                        'method'        : 'methode2',
                        'parameters'    : []
                    },
                ]
            })

        values = self.xmp.findAll(ref='application.conception.Scenario::1', select='.+/operations/\d+', where='name .* Call')

        self.assertEqual({
                './operations/1' : {
                    'name'          : 'Call',
                    'method'        : 'methode1',
                    'parameters'    : []
                },
                './operations/3' : {
                    'name'          : 'Call',
                    'method'        : 'methode2',
                    'parameters'    : []
                }
            }, values)
    #___________________________________________________________________________
    #
if __name__ == '__main__':
    t = FindAllTest()
    t.setUp()
    t.test_findAll_ref_scenario1_select_operations_where_Call()
