.. image:: https://api.travis-ci.org/naparuba/mod-snapshot-mongodb.svg?branch=master
  :target: https://travis-ci.org/naparuba/mod-snapshot-mongodb

==================================
SNAPSHOTS
==================================

Snapshots are used on hosts and services to dump a state of an host or a service when there is an error, like dumping processes when your load is too high


  

  define module {
    module_name snapshot-mongodb
    module_type mongodb_snapshot
    uri mongodb://localhost/?safe=false
    database shinken
  }

  
Declare a snapshot command on a service:
  
::

  define service{
     service_description   Load
     [...]
     snapshot_command    dump_processes
     snapshot_enabled    1
     snapshot_period     24x7
     snapshot_criteria   w,c,u
   }

The data will in the the shinken.snapshots collection 
