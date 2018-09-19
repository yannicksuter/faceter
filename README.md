# Faceter
Script to explode a 3d (obj) file into printable pieces.

## WhereWasI
* add primitives
    * Cylinder
    * Box
* improve model simplification
* model/merge: when merging models, group definitions are lost
* explore boolean operations on model or parametric models
    * support box and cylinder
    * support and/or/xor operations
* remove cur_group concept from model, leads to confusion. better to be stateless
* improving rev-triangulation algorithm to be also robust with polygon(P>4) -> use ear clipping approach for 3d (P>4) polygon
* generate interesting triangle fields, first attempt using delaunay
* clean up tag/group mess in model-class. groups could be a virtual selector of tags

## Issues
* BUG/model: faces added with area 0, this can happen with svg triangulation where vertices span a horizontal line.

## Requirements
python 3.x

## Install dependencies
pip install -r ./requirements.txt
