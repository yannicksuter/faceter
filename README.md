# Faceter
Script to explode a 3d (obj) file into printable pieces.

## WhereWasI
* add extrude method to model
* add shape embedding
* improving rev-triangulation algorithm to be also robust with polygon(P>4)
** use ear clipping approach for 3d (P>4) polygon
* generate interesting triangle fields, first attempt using delaunay
* refactor visualizer to render model-class objects
* matrix math (translation, rotation, ..) and optimize some export functions 

## Issues
* BUG/model: faces added with area 0, this can happen with svg triangulation where vertices span a horizontal line.
* TODO/Shape: inner shapes with >1 shared vertices cannot be triangulated 

## Requirements
python 3.x

## Install dependencies
pip install -r ./requirements.txt
