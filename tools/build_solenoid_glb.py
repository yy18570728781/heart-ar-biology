import bpy
import math
from mathutils import Vector

OUT = r"C:\Users\Administrator\Documents\ChatGPT\AI教育赋能\dist\community\assets\solenoid-hand-control.glb"


def material(name, color, metallic=0.0, roughness=0.45, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, alpha)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, alpha)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Alpha"].default_value = alpha
    if alpha < 1:
        mat.surface_render_method = 'DITHERED'
    return mat


COPPER = material("Copper winding", (0.95, 0.33, 0.04), 0.82, 0.22)
GOLD = material("Magnetic field", (1.0, 0.72, 0.08), 0.4, 0.25)
CORE = material("Solenoid core", (0.08, 0.37, 0.66), 0.5, 0.28, 0.46)
RED = material("North pole", (0.86, 0.04, 0.10), 0.22, 0.32)
BLUE = material("South pole", (0.03, 0.27, 0.83), 0.22, 0.32)
TEAL = material("Guide arrow", (0.02, 0.92, 0.70), 0.25, 0.26)
DARK = material("Terminal", (0.025, 0.06, 0.13), 0.6, 0.2)


def smooth(obj):
    if obj.type == 'MESH':
        for face in obj.data.polygons:
            face.use_smooth = True


def cylinder(name, location, radius, depth, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return obj


def sphere(name, location, radius, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return obj


def cone(name, location, radius1, radius2, depth, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=radius1, radius2=radius2, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return obj


for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# The solenoid axis is X, so it naturally faces a learner looking at the model.
cylinder("Transparent iron core", (0, 0, 0), 0.86, 5.0, CORE, (0, math.pi / 2, 0))

# 11 separate torus rings make a clear, high-quality winding that reads in 3D.
for index in range(11):
    x = -2.18 + index * 0.436
    bpy.ops.mesh.primitive_torus_add(
        major_radius=1.08,
        minor_radius=0.105,
        major_segments=64,
        minor_segments=16,
        location=(x, 0, 0),
        rotation=(0, math.pi / 2, 0),
    )
    loop = bpy.context.object
    loop.name = f"Copper turn {index + 1:02d}"
    loop.data.materials.append(COPPER)
    smooth(loop)

# Leads and coloured pole end-caps.
for x, pole_mat, name in [(-2.76, BLUE, "South pole"), (2.76, RED, "North pole")]:
    cylinder(f"{name} cap", (x, 0, 0), 1.14, 0.16, pole_mat, (0, math.pi / 2, 0))
    sphere(f"{name} terminal", (x * 1.18, 0, 0), 0.25, DARK)

# Three visible internal magnetic field arrows point toward North.
for x in (-1.25, 0, 1.25):
    cylinder("Magnetic field direction", (x, 0, 0), 0.055, 0.72, TEAL, (0, math.pi / 2, 0))
    cone("Magnetic field arrowhead", (x + 0.42, 0, 0), 0.15, 0.0, 0.30, TEAL, (0, math.pi / 2, 0))

# A transparent circular gesture guide behind the model gives hand-control feedback in the web player.
bpy.ops.mesh.primitive_torus_add(major_radius=2.25, minor_radius=0.024, major_segments=80, minor_segments=8, location=(0, 0, -0.18), rotation=(math.pi / 2, 0, 0))
guide = bpy.context.object
guide.name = "Gesture rotation guide"
guide.data.materials.append(GOLD)

# Studio light nodes make the GLB useful in generic web viewers too.
for name, location, energy, color in [
    ("Key", (3, -5, 5), 1200, (0.65, 0.82, 1.0)),
    ("Rim", (-4, 4, 2), 850, (1.0, 0.42, 0.12)),
]:
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.color = color
    data.shape = 'DISK'
    data.size = 5
    light = bpy.data.objects.new(name, data)
    light.location = location
    bpy.context.collection.objects.link(light)

bpy.ops.wm.save_as_mainfile(filepath=OUT.replace('.glb', '.blend'))
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format='GLB',
    export_materials='EXPORT',
    export_lights=True,
    export_cameras=False,
    export_apply=True,
)
