"""
This file performs data wrangling for Austin openstreet map.
Input is the osm file from openstreetmap, output is the JSON file.
Sample output for each document:
{
  "shop": "clothes", 
  "website": "premiumoutlets.com", 
  "name": "Round Rock Premium Outlet", 
  "created": {
    "uid": "1554107", 
    "changeset": "22071440", 
    "version": "3", 
    "user": "jgpacker", 
    "timestamp": "2014-05-01T19:48:28Z"
  }, 
  "pos": [
    30.5664621, 
    -97.6901121
  ], 
  "address": {
    "street": "North Interstate Highway 35", 
    "housename": "4401", 
    "postcode": "78664"
  }, 
  "type": "node", 
  "id": "345201951"
}

or
{
  "node_refs": [
    "149050926", 
    "149050928", 
    "149050930"
  ], 
  "name": "Yupon Drive", 
  "created": {
    "uid": "20587", 
    "changeset": "4351802", 
    "version": "2", 
    "user": "balrog-kun", 
    "timestamp": "2010-04-07T08:22:45Z"
  }, 
  "tiger": {
    "separated": "no", 
    "name_base": "Yupon", 
    "zip_left": "78602", 
    "tlid": "45464964", 
    "cfcc": "A41", 
    "reviewed": "no", 
    "county": "Bastrop, TX", 
    "source": "tiger_import_dch_v0.6_20070829", 
    "name_type": "Dr", 
    "zip_right": "78602"
  }, 
  "type": "way", 
  "id": "15094217", 
  "highway": "residential"
}
"""
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
import os
os.chdir('/Users/Cinkie/Documents/Nanodegree/MongoDB/Project2')

special = {"Avenue": "Ave",
           "Ave." : "Ave",
           "Avene" : "Ave",
           "Circle" : "Cir",
           "Drive" : "Dr",
           "Dr." : "Dr",
           "Street": "St",
           "St." : "St",
           }

mapping = { "Ave": "Avenue",
            "Blvd." : "Boulevard",
            "Blvd" : "Boulevard",
            "CR" : "Court",
            "Cir" : "Circle",
            "Ct" : "Court",
            "Cv" : "Cove",
            "Dr":"Drive",
            "Ln" : "Lane",
            "lane" : "Lane",
            "RD" : "Road",
            "Rd.": "Road",
            "Rd": "Road",
            "Pkwy":"Parkway",
            'Ste. ': 'Suite ',
            'Ste,' : 'Suite ',
            'STE ': 'Suite ',
            "St": "Street",
            "street":"Street",
             
             'IH': 'Interstate Highway',
             'I ': 'Interstate Highway ',
             'Interstate ': 'Interstate Highway ',
             'HWY ': 'Highway ',
             'Hwy ': 'Highway ',
             'Bldg ' : 'Building ',
             'Bldg. ': 'Building ',
             'Bld ': 'Building ',
             'U.S. ': 'Highway ',
             'US Highway' : 'Highway',
             'US ': 'Highway ',
             
             'S ': 'South ',
             'S. ': 'South ',
             'N ': 'North ',
             'N. ': 'North ',
             'W ': 'West ',
             'W. ': 'West ',
             'E ': 'East',
             'E. ': 'East',

            }

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


def update_name(name, mapping):
    
    # conver full name to abbr, then convert all abbr to full name
    # to avoid convert Street to Streetreet, Drive to Driveive
    for s in special.keys():
        if s in name:
            name = name.replace(s, special[s])

    # Our street types contain numbers, cannot use street_type_re
    for key in mapping.keys():
        if key in name:
            name = name.replace(key, mapping[key])
            
    return name

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE

        node['id'] = element.attrib['id']
        node['type'] = element.tag
        if 'visible' in element.attrib.keys():
            node['visible'] = element.attrib['visible']
        if 'lat' in element.attrib.keys():
            node['pos'] = [float(element.attrib['lat']), float(element.attrib['lon'])]

        node['created'] = {}
        for index in CREATED:
            node['created'][index] = element.attrib[index]
            
        address = {}
        tiger = {}
        for tag in element.iter('tag'):
            if problemchars.search(tag.attrib['k']):
                continue
            elif tag.attrib['k'][:5] == "addr:":
                
                # contain the second :
                if ':' in tag.attrib['k'][5:]:
                    continue
                
                # update the street names
                elif tag.attrib['k'][5:] == 'street':
                    address['street'] = update_name(tag.attrib['v'], mapping)

                # drop the incorrect postcodes
                elif tag.attrib['k'][5:]=='postcode' and tag.attrib['v'][:2] != '78':
                    continue
                else:
                    address[tag.attrib['k'][5:]] = tag.attrib['v']
                    
            elif tag.attrib['k'][:6] == "tiger:":
                tiger[tag.attrib['k'][6:]] = tag.attrib['v']
                
            else:
                node[tag.attrib['k']] = tag.attrib['v']
                
        if address != {}:
            node['address'] = address

        if tiger != {}:
            node['tiger'] = tiger
        

        node_refs = []
        for nd in element.iter('nd'):
            node_refs.append(nd.attrib['ref'])
        if node_refs != []:
            node['node_refs'] = node_refs
                                
        
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


data = process_map('austin_texas.osm', True)
#pprint.pprint(data)
    
 
