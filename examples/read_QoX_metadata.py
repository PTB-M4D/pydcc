# PyDCC
#
# Automated uncertainty verification example
#
# Copyright (c) Siemens AG, 2024
#
# Authors:
#     Tim Ruhland, Siemens AG
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#
# SPDX-License-Identifier:  MIT
#
# This example demonstrates the automated extraction of metadata from a Digital Calibration Certificate (DCC).
# It focuses on retrieving calibration QoX parameters and verifying their compliance with required standards.
# This process ensures the applicability of automated parameter extraction from the DCC .


import sys
import numpy as np
sys.path.append("../dcc/")
from dcc.dcc import DCC


def search_metadata_results(data, reftype):
    def find_in_dict(d):
        if isinstance(d, dict):
            if '@refType' in d and d['@refType'] == reftype:
                return d
            for key, value in d.items():
                result = find_in_dict(value)
                if result:
                    return result
        elif isinstance(d, list):
            for item in d:
                result = find_in_dict(item)
                if result:
                    return result
        return None

    if 'metaData' in data:
        return find_in_dict(data['metaData'])
    return None

def get_all_quantities_from_list(list_refType, data):
    def find_list(d):
        if isinstance(d, dict) and d.get('@refType') == list_refType:
            return d
        elif isinstance(d, dict):
            for value in d.values():
                result = find_list(value)
                if result:
                    return result
        elif isinstance(d, list):
            for item in d:
                result = find_list(item)
                if result:
                    return result
        return None

    def extract_quantities(d):
        quantities = {}
        if isinstance(d, list):
            for item in d:
                if isinstance(item, dict) and '@refType' in item:
                    if 'realListXMLList' in item:
                        value = item['realListXMLList']['valueXMLList']
                        unit = item['realListXMLList']['unitXMLList']
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                        quantities[item['@refType']] = (value, unit)
        elif isinstance(d, dict):
            for key, value in d.items():
                if key == 'quantity' and isinstance(value, list):
                    for quantity in value:
                        if '@refType' in quantity and 'realListXMLList' in quantity:
                            val = quantity['realListXMLList']['valueXMLList']
                            uni = quantity['realListXMLList']['unitXMLList']
                            try:
                                val = float(val)
                            except ValueError:
                                pass
                            quantities[quantity['@refType']] = (val, uni)
        return quantities

    specific_list = find_list(data)
    if specific_list:
        return extract_quantities(specific_list.get('quantity', []))
    return {}


if __name__ == '__main__':
    
    # Load DCC and create the DCC object (dcco)
    dcco = DCC('../data/dcc/dcc_gp_temperature_typical_v12_QoX.xml')
 
    if not dcco.status_report.is_loaded:
        print("Error: DCC was not loaded successfully!")

    # Get the metadata dictionary for the searched "dcc:metaData" reference type
    metadata_dict = dcco.get_calibration_metadata(refType='QoX_parameter')
    metadata_dict_2 = dcco.get_calibration_metadata(refType='basic_conformity')
 
    # Search for metadata results with a specific quantity reference type
    metadata_quantity_dict = search_metadata_results(metadata_dict, 'QoX_packetRate')
    print("Metadata QoX_packetRate: %s" % metadata_quantity_dict)
 
    # Get all quantities within a specific list
    all_quantities = get_all_quantities_from_list('QoX_completeness', metadata_dict)
    print("All quantities: %s" % all_quantities)
