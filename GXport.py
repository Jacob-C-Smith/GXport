# Exports a Blender scene to a G10 scene
# Copyright (c) 2021, Jacob Smith

import bpy
import json 
import os

textureExportRes = 512

# Export to blend file location
basedir   = os.path.dirname(bpy.data.filepath)

# Here, we create a working directory to start exporting things in
sceneName  = bpy.data.filepath.rsplit('.')
sceneName  = sceneName[0].rsplit('/')
sceneName  = sceneName[-1] 
wd         = os.path.join(basedir, sceneName)
materialwd = os.path.join(wd, "materials")
texturewd  = os.path.join(wd, "textures")
meshwd     = os.path.join(wd, "meshes")
entitieswd = os.path.join(wd, "entities")



print("wd = " + wd)
# Make the working direcrory if it doesn't exist
try:
    os.mkdir(wd)
except FileExistsError:
    print("Directory " + sceneName + " already exists" )

# Make 
try:
    os.mkdir(materialwd)
except FileExistsError:
    print("Directory " + sceneName + "/materials" + " already exists" )
    
try:
    os.mkdir(texturewd)
except FileExistsError:
    print("Directory " + sceneName + "/textures" + " already exists" )
    
try:
    os.mkdir(meshwd)
except FileExistsError:
    print("Directory " + sceneName + "/meshes"  + " already exists" )

try:
    os.mkdir(entitieswd)
except FileExistsError:
    print("Directory " + sceneName + "/entities"  + " already exists" )


# You really should have the file saved if you are going to export it
if not basedir:
    raise Exception("Blend file is not saved")

# Set up a couple of variables
view_layer = bpy.context.view_layer
obj_active = view_layer.objects.active
selection  = bpy.context.selected_objects

Scene = {
    "name"     : sceneName,
    "comment"  : "",
    "entities" : [
        
    ],
    "cameras"  : [
    
    ],
    "lights"   : [
    
    ]
}

bpy.ops.object.select_all(action='DESELECT')

for obj in selection:
    
    # Select the object
    obj.select_set(True)
    view_layer.objects.active = obj
    
    # Find the name and the path
    name = bpy.path.clean_name(obj.name)
    fn   = os.path.join(basedir, name)
    
    # Process as a mesh
    if obj.type == 'MESH':
        
        # Create the entity object
        entity = {
            "name" : obj.name,
        }
        

        # Create a new directory for the object
        lwd = entitieswd
        try:
            os.mkdir(entitieswd + "/" + obj.name)
        except FileExistsError:
            print(obj.name + " already exists")   
              
        lwd = os.path.join(entitieswd, obj.name)

        print("lwd = " + lwd)

        # Process comment
        if "comment" in obj.data:
            entity["comment"] = obj.data["comment"]
        
        # Process mesh
        mesh = {
            "name" : ""
        }
        
        meshPath = str(meshwd) + "/" + obj.name +".ply"
        print("meshPath = " + meshPath)
        
        # Seperate by loose parts
        #bpy.ops.mesh.separate(type='LOOSE')
        
        bpy.ops.export_mesh.ply(filepath      = meshPath, 
                                use_selection = True, 
                                use_ascii     = False,
                                use_normals   = True,
                                use_uv_coords = True,
                                use_colors    = False,
                                axis_forward  = 'Y',
                                axis_up       = 'Z')
        
        
        
        # Process shader
        shader = {
        
        }
        
        # Process transform
        transform = {
                "location" : [ obj.location.x, obj.location.y, obj.location.z ],
                "rotation" : [ obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z ],
                "scale"    : [ obj.scale.x, obj.scale.y, obj.scale.z ]
            } 
        
        # Process material
        if obj.active_material.node_tree.nodes['Principled BSDF'].type == 'BSDF_PRINCIPLED':

            # Convenience variables
            activeMat    = obj.active_material
            materialName = activeMat.name
            shaderInputs = obj.active_material.node_tree.nodes['Principled BSDF'].inputs
            shaderNodes  = obj.active_material.node_tree.nodes
            
            # Define the material and its working directory
            material     = obj.active_material
            materialPath = str(texturewd) + "\\" + str(materialName) + "\\" 
            
            # Define paths and objects
            albedo       = material.node_tree.nodes.new('ShaderNodeTexImage')
            albedoPath   = materialPath + "albedo.png"
            normal       = material.node_tree.nodes.new('ShaderNodeTexImage')
            normalPath   = materialPath + "normal.png"
            rough        = material.node_tree.nodes.new('ShaderNodeTexImage')
            roughPath    = materialPath + "rough.png"
            metal        = material.node_tree.nodes.new('ShaderNodeTexImage')
            metalPath    = materialPath + "metal.png"
            ao           = material.node_tree.nodes.new('ShaderNodeTexImage')
            aoPath       = materialPath + "ao.png"

            # Create a directory for the material textures
            try:
                os.mkdir(os.path.join(texturewd,materialPath))
            except FileExistsError:
                print("")
            
            # Create new images
            albedo.image = bpy.data.images.new(materialName + ".albedo", textureExportRes,textureExportRes)
            normal.image = bpy.data.images.new(materialName + ".normal", textureExportRes,textureExportRes)
            metal.image  = bpy.data.images.new(materialName + ".metal" , textureExportRes,textureExportRes)
            rough.image  = bpy.data.images.new(materialName + ".rough" , textureExportRes,textureExportRes)
            ao.image     = bpy.data.images.new(materialName + ".ao"    , textureExportRes,textureExportRes)
            
            # Process the albedo
            activeMat.node_tree.nodes.active = albedo
            albedo.select                    = True
            
            albedo.image.filepath = albedoPath 
            bpy.ops.object.bake(type='DIFFUSE', width=512, height=512, target='IMAGE_TEXTURES', save_mode='EXTERNAL')
            
            albedo.image.save_render(albedoPath)
            activeMat.node_tree.nodes.remove(albedo)
            
            if(type(shaderInputs['Metallic'].default_value) == float):
                print("Float")

            #shaderInputs['Metallic'].links[0].from_node.
            metalPath  = None
        

            
        material = {
            "albedo" : albedoPath,
            "normal" : normalPath,
            "rough"  : roughPath,
            "metal"  : metalPath,
            "ao"     : aoPath    
        }
        
        with open(os.path.join(materialwd,obj.active_material.name + ".json"), "w+") as outfile:
            try:
                json.dump(material, outfile, indent=5)
            except FileExistsError:
                print("File " +  + "has been overwritten")
        
        
        # Process rigidbody
        rigidbody = {
        
        }
        entity["rigidbody"] = rigidbody
        
        # Process collider
        collider = {
        
        }
        entity["collider"] = collider
        
        entityPath = os.path.join(lwd, entity['name'] + ".json")
        with open(entityPath, "w+") as outfile:
            try:
                json.dump(entity, outfile, indent=5)
            except FileExistsError:
                print("File " +  + "has been overwritten")
        
        Scene["entities"].append(str(entityPath))
        
    elif obj.type == 'LIGHT':
        # Define the light and the variables 
        light = { }
        
        intensity = obj.data.energy
        
        name     = obj.name
        color    = [ obj.data.color[0] * intensity, obj.data.color[1] * intensity, obj.data.color[2] * intensity ]
        position = [ obj.location.x, obj.location.y, obj.location.z ]
        
        light["name"]     = name
        light["color"]    = color
        light["position"] = position
        
        Scene["lights"].append(light)
        
    elif obj.type == 'CAMERA':
         #obj.data.
         print("")
    elif obj.type == 'CURVE':
        print("GXPort does not support exporting curves")
    elif obj.type == 'SURFACE':
        print("GXPort does not support exporting surfaces")
    elif obj.type == 'META':
        print("GXPort does not support exporting meta")
    elif obj.type == 'FONT':
        print("GXPort does not support exporting fonts")
    elif obj.type == 'HAIR':
        print("GXPort does not support exporting hair")
    elif obj.type == 'POINTCLOUD':
        print("GXPort does not support exporting point clouds")
    elif obj.type == 'VOLUME':
        print("GXPort does not support exporting volumes")
    elif obj.type == 'GPENCIL':
        print("GXPort does not support exporting g pencils")
    elif obj.type == 'ARMATURE':
        print("GXPort does not support exporting armatures")
    elif obj.type == 'LATTICE':
        print("GXPort does not support exporting lattices")
    elif obj.type == 'EMPTY':
        print("Nothing to be done for " + obj.name + " as the object  is empty")
    elif obj.type == 'LIGHT_PROBE':
        print("GXPort does not support exporting light probes")
    elif obj.type == 'SPEAKER':
        print("GXPort does not support exporting speakers")
    else:
        print("GXPort has encountered an unknown object type")

    obj.select_set(False)

    print("Exported :", fn)


view_layer.objects.active = obj_active

print(sceneName + ".json")

scenePath = os.path.join(basedir, sceneName + ".json")

with open(scenePath, "w+") as outfile:
    try:
        json.dump(Scene, outfile, indent=5)
    except FileExistsError:
        print("Directory")
print("DONE")

for obj in selection:
    obj.select_set(True)
