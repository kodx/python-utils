#!/usr/bin/env python
# -*- coding: utf-8 -*-
# cts_complex_sql_get.py
#      
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

import _mssql
import time
from datetime import datetime, timedelta
import csv

"""
This program get data from MSSQL database by given
parameters and calculates avarage.

Target is MSSQL 2005 database of complex from
http://www.cts.spb.ru/

output: create 2 files:
full - all data from request
avg - average

it uses pymssql module based upon freetds and it can be broken for
database above version 2008

http://code.google.com/p/pymssql/
python 2.6
"""

# source date and time
sStart = '2013-01-16 07:00:00'
sEnd = '2013-01-16 18:00:00'

# Table to get data from
# SNAP_1 - every minute snapshot
# TIT - all data
sqltable = 'SNAP_1'

# specific parameter
uidvar = 291
uidvarDesc = 'G3' # this description will be added to filename
"""
Generator channels
G2 - 100
G3 - 291
G4 - 482
G5 - 673
G6 - 864
"""

# Database connection settings
sqluser = 'user'
sqlpass = 'password'
sqlsrv = 'mssql_base_address'
sqldb = 'dbname'
sqlenc = 'cp1251' # database encoding

# calc. of utc datetime offset, it can be set in numbers
# for this example datatime in db was in utc, and i had to convert it
# to local time (UTC+4)
utcOffset = (time.timezone / -(60*60))

# calculate date and time for request
dtStart = (datetime.strptime(sStart, '%Y-%m-%d %H:%M:%S') -
           timedelta(hours=utcOffset))
dtEnd = (datetime.strptime(sEnd, '%Y-%m-%d %H:%M:%S') -
         timedelta(hours=utcOffset))

# sql request
sqlquery = """
SELECT Tbl1.DateInKP AS DateINKP, Tbl1.ValueVariable 
FROM ( SELECT * FROM %(sqltable)s_%(dtStartShort)s
       where UIDVariable=%(uidvar)d
       UNION
       SELECT * FROM %(sqltable)s_%(dtEndShort)s
       where UIDVariable=%(uidvar)d
) Tbl1
where DateInKP >= '%(dtStart)s' and 
      DateInKP <  '%(dtEnd)s'
ORDER BY Tbl1.DateINKP""" % \
{'uidvar': uidvar,
 'sqltable': sqltable,
 'dtStartShort': dtStart.strftime('%Y%m%d'),
 'dtEndShort': dtEnd.strftime('%Y%m%d'),
 'dtStart': dtStart.strftime('%Y-%m-%d %H:%M:%S'),
 'dtEnd': dtEnd.strftime('%Y-%m-%d %H:%M:%S')}
# In this case i was using this form of string format cause standart
# connect() was broken.

def total_seconds(date):
    """
    Calculate seconds in given datetime.timedelta.
    Parameters:
    date - datetime.timedelta
    
    returns - float
    
    This function python 2.7.2 built-in, i was using python 2.6 and
    had to make my own implementation.
    """
    return (date.microseconds + (date.seconds + date.days * 24 * 3600)
            * 10**6) / 10**6.

def calc_avg_int(input_list):
    prev_val = count = tmpsum = 0
    tmp = input_list[0][0]
    res = []
    cur_hour = prev_time = datetime(tmp.year, tmp.month, tmp.day, tmp.hour)

    for row in input_list:
        if (row[0] - cur_hour) >= timedelta(hours=1):
            cur_hour = datetime(row[0].year, row[0].month, row[0].day,
                                row[0].hour)
            secs = total_seconds(cur_hour - prev_time)
            tmpsum += prev_val * secs
            res.append([cur_hour, tmpsum/3600])
            tmpsum = 0
        secs = total_seconds(row[0] - prev_time)
        tmpsum += float(row[1]) * secs
        prev_time = row[0]
        prev_val = float(row[1])
        
    tmp = prev_time + timedelta(hours=1)
    cur_hour = datetime(tmp.year, tmp.month, tmp.day, tmp.hour)
    tmpsum += prev_val * total_seconds(cur_hour - prev_time)
    res.append([cur_hour, tmpsum/3600])

    return res    

def calc_avg(input_list):
    count = tmpsum = 0
    tmp = input_list[0][0]
    res = []
    cur_hour = prev_time = datetime(tmp.year, tmp.month, tmp.day,
                                    tmp.hour)
    for row in input_list:
        if (row[0] - cur_hour) >= timedelta(hours=1):
            cur_hour = datetime(row[0].year, row[0].month, row[0].day,
                                row[0].hour)
            res.append([cur_hour, float(tmpsum/count)])
            tmpsum = count = 0
        tmpsum += float(row[1])
        count += 1
        prev_time = row[0]

    if (prev_time - cur_hour) < timedelta(hours=1):
        cur_hour = cur_hour+timedelta(hours=1)
    
    res.append([cur_hour, float(tmpsum/count)])
    return res

def read_sql():
    reslst = [] # result list
    try:
        conn = _mssql.connect(server=sqlsrv, user=sqluser, password=sqlpass, \
                              database=sqldb, charset=sqlenc)
        conn.execute_query(sqlquery)
        for row in conn:
            reslst.append([(row[0] + timedelta(hours=utcOffset)),
                           row[1]])

    except _mssql.MssqlDatabaseException,e:
        print 'connection error number=', e, ', severity=', e.severity
    finally:
        conn.close()
    
    return reslst

def mkcsv(fname, input_list):
    with open(fname, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';',
                                quotechar='|',
                                quoting=csv.QUOTE_MINIMAL)

        for row in input_list:
            csvwriter.writerow([row[0].strftime('%Y-%m-%d %H:%M:%S'),
                                str(row[1]).replace('.',',')])
        
if __name__ == '__main__':
    sdata = read_sql()
    if not sdata :
        print "No data to proceed, check SQL Query!"
    else:
        if sqltable == 'TIT':
            avgdata = calc_avg_int(sdata)
        elif sqltable == 'SNAP_1':
            avgdata = calc_avg(sdata)
        else:
            print 'Error table name selected!'
    
        stmp = sStart.replace(':', '_')
        etmp = sEnd.replace(':', '_')
        mkcsv('full '+uidvarDesc+' '+stmp+' - '+etmp+'.csv', sdata)
        mkcsv('avg '+uidvarDesc+' '+stmp+' - '+etmp+'.csv', avgdata)

