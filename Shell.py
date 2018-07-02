from Model import Model

def generate_shell(model, thickness):
    return None

if __name__ == "__main__":

    obj_name = 'cube'

    import ObjLoader
    obj_data = ObjLoader.ObjLoader(f'./example/{obj_name}.obj')
    obj_model = Model.load_fromdata(obj_data, scale=100.)
    obj_model.simplify()

    thickness = [0 if i == 0 else 10 for i in range(len(obj_model._faces))]
    obj_hull = generate_shell(obj_model, thickness)

    if obj_hull:
        from Exporter import Exporter
        Exporter.write_obj(obj_hull, f'./export/_{obj_name}_shell.obj')