import os
from Model import *

class ObjExporter:
    def __init__(self, model, export_filepath):
        pass

    @staticmethod
    def write(model, export_filepath):
        try:
            path, filename = os.path.split(export_filepath)
            with open(export_filepath, 'w') as obj_export:
                obj_export.write(f'# {filename}\n#\n\ng {model._name}\n')

                # export vertices
                obj_export.write(f'\n')
                for vert in model._vertices:
                    obj_export.write(f'v {vert[0]} {vert[1]} {vert[2]}\n')

                # export faces
                obj_export.write(f'\n')
                for face in model._faces:
                    obj_export.write('f ' + ' '.join([f'{vid+1}//' for vid in face._vids]) + '\n')

                print(f'{filename} successfully written.')
        except:
            print(".obj file could not be written.")

if __name__ == "__main__":
    import ObjLoader
    obj_data = ObjLoader.ObjLoader('./example/cube.obj')
    obj_model = Model.load_fromdata(obj_data)

    ObjExporter.write(obj_model, './export/_cube.obj')
