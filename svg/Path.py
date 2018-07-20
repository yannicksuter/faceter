#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import numpy as np

class Path:
    def __init__(self, description):
        for token in description['d'].split(' '):
            if token[0:1] == 'm':
                print('>>> moveto')
            elif token[0:1] == 'z':
                print('>>> closepath')
            else:
                print(token)
        print('<<<<<<<<<<<<<<<< DONE')

    @staticmethod
    def read(filename):
        _paths = []
        try:
            tree = ET.parse(filename)
            for elem in tree.iter():
                #only 1.1 support yet
                if elem.tag.endswith('svg'):
                    if 'version' in elem.attrib and float(elem.attrib['version']) > 1.1:
                        print('Only SVG <= 1.1 supported.')
                        return
                #read path elements
                if elem.tag.endswith('path'):
                    try:
                        _paths.append(Path(elem.attrib))
                    except:
                        pass
            print(f'{len(_paths)} elements read from {filename}.')
        except:
            print(f'Error while reading {filename}.')
        return _paths

if __name__ == "__main__":
    paths = Path.read(f'../example/svg/0123.svg')
    print(paths)