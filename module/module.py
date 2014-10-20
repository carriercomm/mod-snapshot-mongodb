#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014:
#    Gabes Jean, naparuba@gmail.com

"""
This is a broker and webui module to save host/service snapshots data into a mongodb database
"""

import time
import uuid


try:
    import pymongo
    from pymongo.connection import Connection
except ImportError:
    Connection = None
    pymongo = None
try:
    from pymongo import ReplicaSetConnection
except ImportError:
    ReplicaSetConnection = None

from shinken.basemodule import BaseModule
from shinken.log import logger

properties = {
    'daemons': ['broker', 'webui'],
    'type': 'snapshot_mongodb',
    'external': False,
    }


def get_instance(plugin):
    """
    Called by the plugin manager to get a broker
    """
    logger.debug("Get a Mongodb snapshot module for plugin %s" % plugin.get_name())
    if not Connection:
        raise Exception('Cannot find the module python-pymongo. Please install it.')
    uri = plugin.uri
    database = plugin.database
    replica_set = getattr(plugin, 'replica_set', '')
    instance = Mongodb_snapshot(plugin, uri, database, replica_set)
    return instance


class Mongodb_snapshot(BaseModule):
    def __init__(self, modconf, uri, database, replica_set):
        BaseModule.__init__(self, modconf)
        self.uri = uri
        self.database = database
        self.replica_set = replica_set
        if self.replica_set and not ReplicaSetConnection:
            logger.error('[MongodbSnapshot] Can not initialize module with '
                         'replica_set because your pymongo lib is too old. '
                         'Please install it with a 2.x+ version from '
                         'https://github.com/mongodb/mongo-python-driver/downloads')
            return None


    def init(self):
        """
        Called by broker to say 'let's prepare yourself guy'
        """
        logger.debug("Initialization of the mongodb snapshot module")

        if self.replica_set:
            self.con = ReplicaSetConnection(self.uri, replicaSet=self.replica_set, fsync=False)
        else:
            # Old versions of pymongo do not known about fsync
            if ReplicaSetConnection:
                self.con = Connection(self.uri, fsync=False)
            else:
                self.con = Connection(self.uri)

        self.db = getattr(self.con, self.database)
        self.snapshots = getattr(self.db, 'snapshots')
        self.snapshots.ensure_index([ ('host_name',pymongo.DESCENDING), ('snapshot_time',pymongo.DESCENDING)])


    def manage_host_snapshot_brok(self, b):
        data = b.data
        to_load = ['host_name', 'snapshot_output', 'snapshot_time', 'snapshot_exit_status']
        d = {
            '_id':uuid.uuid1().hex,
        }
        for prop in to_load:
            d[prop] = data[prop]
        self.snapshots.insert(d, w=0, j=False, fsync=False)
        

    def manage_service_snapshot_brok(self, b):
        data = b.data
        to_load = ['host_name', 'service_description', 'snapshot_output', 'snapshot_time', 'snapshot_exit_status']
        d = {
            '_id':uuid.uuid1().hex,
        }
        for prop in to_load:
            d[prop] = data[prop]
        self.snapshots.insert(d, w=0, j=False, fsync=False)
