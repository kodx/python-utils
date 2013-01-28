#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: mssql_zero_fill.py 
# Author: Yegor Bayev (kodx) <kodxxx@gmail.com> 
# Created: Wed Dec 19 16:21:48 2012
# License: 
# Copyright 2012 Yegor Bayev (kodx) <kodxxx@gmail.com>
#      
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#     
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#      
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""
Fill MSSQL 2005 database with zeros by given parameters
"""

import _mssql
import time
from datetime import datetime, timedelta

sqluser = 'user'
sqlpass = 'password'
sqlsrv = '192.168.0.1'
sqldb = 'dbname'
sqlenc = 'cp1251'

def mkdate(text):
    return datetime.strptime(text, '%Y-%m-%d %H:%M:%S')

def insert_sql(dDate, dItem):
    sqlquery = """
    insert into data
    (parnumber, object, item, value0, value1, objtype, data_date,
    rcvstamp, season, p2kstatus, p2kstatush, appid)
    values
    (12, 4372, %(dItem)d, 0.0, 0.0, 0, '%(sDate)s', '%(sRcvDate)s',
    4023, 0, 0, 38) 
    """ % \
    {'sDate': dDate.strftime('%Y-%m-%d %H:%M:%S'),
     'sRcvDate': (datetime.now()).strftime('%Y-%m-%d %H:%M:%S'),
     'dItem': dItem}
    try:
        conn = _mssql.connect(server=sqlsrv, user=sqluser, password=sqlpass, \
                              database=sqldb, charset=sqlenc)
        conn.execute_non_query(sqlquery)
        if conn.identity == None:
            print "something is wrong, insert", sqlquery, " failed"
            

    except _mssql.MssqlDatabaseException,e:
        print 'connection error number=', e, ', severity=', e.severity
    finally:
        conn.close()

    return 0
    
if __name__ == '__main__':
    #curDt = mkdate('2012-12-17 01:00:00')
    curDt = datetime.now()
    dtCur = (curDt - timedelta(days=1)).replace(hour=0, minute=0,
                                                  second=0,
                                                  microsecond=0)
    for i in xrange(48):
        dtCur += timedelta(minutes=30)
        insert_sql(dtCur, 1)
        insert_sql(dtCur, 3)

# mssql_zero_fill.py ends here

