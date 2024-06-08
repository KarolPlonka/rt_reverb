import json


def load_materials(json_file_path = 'assets/materials.json'):
    materials = {}
    default_material = None

    with open(json_file_path) as f:
        material_list = json.load(f)

    for material in material_list:
        materials[material['name']] = material

        if 'default' in material.keys() and material['default']:
            default_material = material

    if not default_material:
        default_material = material_list[0]

    return materials, default_material


MATERIALS, DEFAULT_MATERIAL = load_materials()
