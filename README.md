# faceter
Script to explode a 3d (obj) file into printable pieces.

# requirements
python 3.x

# install dependencies
pip install -r ./requirements.txt

# WhereWasI
* smarter plane selection to calculate offset
* optimize offset calculation
v 34.705 17.205 -13.919
v -3.377 -36.949 -13.919
v -15.157 38.115 -13.919
v -10.911 35.390 0.207
v 0.388 -36.358 0.589
v 33.934 15.367 0.948
v 31.634 16.306 -13.719
v -5.086 -35.912 -13.719 ## problem punkt vorne unten
v -12.493 34.811 -13.719
v -8.895 32.503 -1.754
v 0.684 -28.324 -1.430 ## problem punkt vorne oben
v 30.993 14.765 -1.095

vertex[1]: 4 connected faces
ref_plane #1: 3 -> ref: 5
ref_plane #2: 2 -> ref: 4
ref_plane #3: 0 -> ref: 0
offset vertex: 84.82176755269903, 23.675930983306955, 0.01163659996571198

v 34.705 17.205 -13.919
v -3.377 -36.949 -13.919
v -15.157 38.115 -13.919
v -10.911 35.390 0.207
v 0.388 -36.358 0.589
v 33.934 15.367 0.948
v 31.631 16.287 -13.406
v -5.086 -35.912 -13.719 # immer noch ein problem.. -> orig pos: v (84.822 23.676 0.012)
v -12.493 34.811 -13.719
v -8.648 32.345 -0.933
v 1.077 -30.819 -1.417
v 30.719 14.887 -1.100
