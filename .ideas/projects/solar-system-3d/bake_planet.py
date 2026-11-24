"""Blender loop test: build a procedural planet, bake colour/normal/roughness, export .glb,
then re-import the .glb on its own and render it to check what the web app will get.

Run: blender -b --factory-startup -P bake_planet.py -- <outdir>
"""
import bpy, sys, os, time, math

OUT = sys.argv[sys.argv.index("--") + 1:][0]
os.makedirs(OUT, exist_ok=True)
RES = 1024


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.cycles.samples = 64
    s.cycles.use_denoising = True
    s.render.resolution_x = s.render.resolution_y = 512
    return s


def camera_and_light(s, dist=3.2):
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    s.collection.objects.link(cam)
    cam.location = (0, -dist, 0)
    cam.rotation_euler = (math.radians(90), 0, 0)
    s.camera = cam
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 4
    sun.rotation_euler = (math.radians(60), math.radians(-40), 0)
    s.collection.objects.link(sun)
    w = bpy.data.worlds.new("W"); w.color = (0.003, 0.004, 0.008); s.world = w


def render(s, path):
    t = time.time()
    s.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print(f"RENDER {os.path.basename(path)} {time.time()-t:.1f}s")


def ramp(n, stops):
    r = n.new("ShaderNodeValToRGB"); cr = r.color_ramp
    for i, (pos, col) in enumerate(stops):
        e = cr.elements[i] if i < 2 else cr.elements.new(pos)
        e.position = pos; e.color = col if len(col) == 4 else (*col, 1)
    return r


# --- Build the procedural planet ---
s = reset()
bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=1)
planet = s.objects[-1]; planet.name = "Planet"
bpy.ops.object.shade_smooth()
mat = bpy.data.materials.new("Terran"); mat.use_nodes = True
nt = mat.node_tree; n = nt.nodes; L = nt.links
bsdf = n["Principled BSDF"]
noise = n.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 2.2
noise.inputs["Detail"].default_value = 12
noise.inputs["Roughness"].default_value = 0.6
SEA = 0.5
colour = ramp(n, [(SEA - 0.02, (0.02, 0.08, 0.25)), (SEA + 0.02, (0.12, 0.30, 0.08)),
                  (0.62, (0.35, 0.28, 0.16)), (0.70, (0.9, 0.9, 0.92))])
rough = ramp(n, [(SEA - 0.005, (0.25,) * 3), (SEA + 0.005, (0.85,) * 3), (0.68, (0.85,) * 3), (0.70, (0.5,) * 3)])
# Bump only on land: height is flat below sea level
land = n.new("ShaderNodeMapRange")
land.inputs["From Min"].default_value = SEA; land.inputs["From Max"].default_value = 1
bump = n.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.6
bump.inputs["Distance"].default_value = 0.08  # Blender 5 default is 0.001 (4.x was 1.0)
L.new(noise.outputs["Fac"], colour.inputs["Fac"])
L.new(noise.outputs["Fac"], rough.inputs["Fac"])
L.new(noise.outputs["Fac"], land.inputs["Value"])
L.new(land.outputs["Result"], bump.inputs["Height"])
L.new(colour.outputs["Color"], bsdf.inputs["Base Color"])
L.new(rough.outputs["Color"], bsdf.inputs["Roughness"])
L.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
planet.data.materials.append(mat)
camera_and_light(s)
render(s, os.path.join(OUT, "procedural.png"))

# --- Bake colour, roughness and tangent-space normal ---
bpy.context.view_layer.objects.active = planet; planet.select_set(True)
s.cycles.samples = 4
bk = s.render.bake


def bake(kind, name, non_color):
    img = bpy.data.images.new(name, RES * 2, RES, float_buffer=False)
    if non_color:
        img.colorspace_settings.name = "Non-Color"
    tex = n.new("ShaderNodeTexImage"); tex.image = img
    for node in n: node.select = False
    tex.select = True; n.active = tex
    if kind == "DIFFUSE":
        bk.use_pass_direct = bk.use_pass_indirect = False; bk.use_pass_color = True
    if kind == "NORMAL":
        bk.normal_space = "TANGENT"
    t = time.time(); bpy.ops.object.bake(type=kind); print(f"BAKE {kind} {time.time()-t:.1f}s")
    img.filepath_raw = os.path.join(OUT, f"{name}.png"); img.file_format = "PNG"; img.save()
    return tex


t_col = bake("DIFFUSE", "Terran_diffuse", False)
t_rough = bake("ROUGHNESS", "Terran_roughness", True)
t_norm = bake("NORMAL", "Terran_normal", True)

# Swap the procedural nodes for the baked images, the way the glTF exporter wants them
for node in (noise, colour, rough, land, bump):
    n.remove(node)
nmap = n.new("ShaderNodeNormalMap")
L.new(t_col.outputs["Color"], bsdf.inputs["Base Color"])
L.new(t_rough.outputs["Color"], bsdf.inputs["Roughness"])
L.new(t_norm.outputs["Color"], nmap.inputs["Color"])
L.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
glb = os.path.join(OUT, "Terran.glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_image_format="WEBP")
print("EXPORTED", glb, f"{os.path.getsize(glb)/1e6:.2f} MB")

# --- Check: the exported .glb alone, in a fresh scene ---
s = reset()
bpy.ops.import_scene.gltf(filepath=glb)
m = [o for o in s.objects if o.type == "MESH"][0].active_material
print("REIMPORT inputs:", sorted({l.to_socket.name for l in m.node_tree.links if l.to_node.type == "BSDF_PRINCIPLED"}))
camera_and_light(s)
render(s, os.path.join(OUT, "exported_glb.png"))
