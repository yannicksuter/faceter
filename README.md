# Faceter
Script to explode a 3d (obj) file into printable pieces.

## WhereWasI
* remove cur_group concept from model, leads to confusion. better to be stateless
* improving rev-triangulation algorithm to be also robust with polygon(P>4) -> use ear clipping approach for 3d (P>4) polygon
* generate interesting triangle fields, first attempt using delaunay
* add b-spline/interpolation support to path
* clean up tag/group mess in model-class. groups could be a virtual selector of tags

## Issues
* BUG/model: faces added with area 0, this can happen with svg triangulation where vertices span a horizontal line.

## Requirements
python 3.x

## Install dependencies
pip install -r ./requirements.txt
