#!/usr/bin/env python
# -*- coding: utf-8 -*-
# module_iec_xml_generator.py
#      
# Copyright 2013 Yegor Bayev (kodx) <kodxxx@gmail.com>
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
Simple xml generation program designed for Neva complex
input data - csv file.
http://www.energosoyuz.spb.ru/content/%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%BD%D0%BE%D0%B5-%D0%BE%D0%B1%D0%B5%D1%81%D0%BF%D0%B5%D1%87%D0%B5%D0%BD%D0%B8%D0%B5
"""

try:
    from lxml import etree as et
except ImportError:
    print("can't find lxml package, please install it properly")  

if __name__ == '__main__':
    root = et.Element("IECSchema")

    iec = et.SubElement(root,
                        "IEC", Station="Neva", Port="2404",
                        ClientLimit="5", ASDUAddr="1", KP="1",
                        Sporadic="false", Period="1000")
    et.SubElement(iec, "Periodic").text = "true"
    
    srv = et.SubElement(root, "IECServers")
    et.SubElement(srv, "IECServer_id").text = "1"
    et.SubElement(srv, "IECServer_name").text = "Server"
    et.SubElement(srv, "IECServer_ip").text = "192.168.0.1"
    et.SubElement(srv, "IECServer_port").text = "2500"
    et.SubElement(srv, "IECServer_Period").text = "1"
    et.SubElement(srv, "IECServer_Mode")
    et.SubElement(srv, "IECServer_UniqueIDBase").text = "0"
    et.SubElement(srv, "IECServer_TimeMode").text = "1"
    et.SubElement(srv, "IECServer_NeedConvertToUTC").text = "0"
    et.SubElement(srv, "IECServer_PeriodSync").text = "60000"

    idx = 0
    for line in open("iec_values_and_opc_tags.csv", "rb"):
        values = (line.strip()).split(";")
        uid = values[0]
        tag = values[1]
        item = et.SubElement(root, "IECItems")
        et.SubElement(item, "IECItem_id").text = str(idx)
        et.SubElement(item, "IECItem_server").text = "1"
        et.SubElement(item, "IECItem_kp").text = "0"
        et.SubElement(item, "IECItem_uid").text = uid
        if int(uid) < 1000:
            itype = "TS"
        else:
            itype = "TI"
        
        et.SubElement(item, "IECItem_OPCName").text = itype+"."+tag
        et.SubElement(item, "IECItem_ordernum").text = "1"
        et.SubElement(item, "IECItem_UniqueID").text = uid
        et.SubElement(item, "IECItem_type").text = itype
        et.SubElement(item, "IECItem_Offset").text = "0"
        et.SubElement(item, "IECItem_Scale").text = "1"
        et.SubElement(item, "IECItem_UOM")
        idx += 1
    
    tree = et.ElementTree(root)
    tree.write("IEC_Config.xml", pretty_print=True, xml_declaration=True,
               encoding="UTF-8", standalone="true")
    
# module_iec_xml_generator ends here
