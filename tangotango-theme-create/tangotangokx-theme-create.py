#!/usr/bin/env python3
# coding: utf-8
# File: tangotangokx-theme-create.py
# Author: Yegor Bayev <baev.egor (at) gmail.com>
# Created: Thu Aug 29 20:44:21 2013
# License:
#      
# Copyright 2013 Yegor Bayev <baev.egor (at) gmail.com>
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

'''
create changes with command
$ cat ./tangotango-theme.el | grep -o '\"[(a-z)(A-Z)(0-9) ]*\"' | sort -u > changes
then fill corresponding colors to it number
'''

import fileinput, re

changesFile = 'changes'
sourceFile = 'tangotango-theme.el'
targetFile = 'tangotangokx-theme.el'

if __name__ == '__main__':
    chMap = {}
    with open(changesFile, 'r') as f:
        for line in f:
            if line.strip() != '':
                color, number = line.strip().split(' - ')
                chMap[color] = number
            
    p = re.compile('\"[(a-z)(A-Z)(0-9) #]*\"')
    
    with open(sourceFile, 'r') as f:
        outFile = []
        for line in f:
            m = p.findall(line.strip())
            if m:
                for i in m:
                    if i in chMap:
                        line = line.replace(i, chMap[i])

            # remove italic styles
            if ':slant italic' in line:
                line = line.replace(':slant italic', '')
            # remove font declaration
            if ':family "DejaVu Sans Mono" :foundry "unknown" :width normal :height 90 :weight normal ' in line:
                line = line.replace(':family "DejaVu Sans Mono" :foundry "unknown" :width normal :height 90 :weight normal ', '')
            # renaming theme
            if 'tangotango' in line:
                if 'color-theme-tangotango' not in line:
                    line = line.replace('tangotango', 'tangotangokx')
            # adding mod annotaion
            if ';; This file is NOT part of GNU Emacs.' in line:
                outFile.append(";; kodx version 0.0.2\n;; Author: Yegor Bayev <baev.egor (at) gmail.com>\n;; URL: https://github.com/kodx/emacs.d\n\n")
            outFile.append(line)

    with open(targetFile, 'w') as f:
        for line in outFile:
            f.write("%s" % line)
    
# tangotangokx-theme-create.py ends here
