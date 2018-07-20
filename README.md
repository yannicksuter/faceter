# Faceter
Script to explode a 3d (obj) file into printable pieces.

## WhereWasI
* support SVG to load contours 
* improving rev-triangulation algorithm to be also robust with polygon(P>4)
* using scipy.spacial for 2d triangulations 
* generate interesting triangle fields, first attempt using delaunay
* add contours/glyphs with extrude functionality
* refactor visualizer to render model-class objects
* matrix math (translation, rotation, ..) and optimize some export functions 

## Requirements
python 3.x

## Install dependencies
pip install -r ./requirements.txt
