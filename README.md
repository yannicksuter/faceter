# Faceter
Script to explode a 3d (obj) file into printable pieces.

## WhereWasI
* implementing ear clipping for shapes
* add support for holes to tessalation of shapes 
* improving rev-triangulation algorithm to be also robust with polygon(P>4)
* using scipy.spacial for 2d triangulations 
* generate interesting triangle fields, first attempt using delaunay
* add contours/glyphs with extrude functionality
* refactor visualizer to render model-class objects
* matrix math (translation, rotation, ..) and optimize some export functions 

* BUG/model: faces added with area 0, this can happen with svg triangulation where vertices span a horizontal line.

## Requirements
python 3.x

## Install dependencies
pip install -r ./requirements.txt
