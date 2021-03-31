import time
import os

import bpy
from bpy.props import *
from bpy.types import Operator
from bpy_extras.io_utils import (
    ExportHelper,
    path_reference_mode,
)

def fbxexport(self, context):
    """ use export fbx addon """
    view_layer = bpy.context.view_layer

    obj_active = view_layer.objects.active
    selection = bpy.context.selected_objects

    bpy.ops.object.select_all(action='DESELECT')

    # Only embed textures in COPY mode!
    # if embed_textures and path_mode != 'COPY':
    #     embed_textures = False

    batch_properties = bpy.context.scene.batch_exporter

    for obj in selection:

        obj.select_set(True)

        # some exporters only use the active object
        view_layer.objects.active = obj

        name = bpy.path.clean_name(obj.name)
        export_folder = ""
        #fn = os.path.join(basedir, name)
        
        if batch_properties.export_multipleFolder:
            export_folder = batch_properties.ExportFolder + name + "\\"
            
            if not os.path.exists(export_folder):
                os.mkdir(export_folder)  

        bpy.ops.export_scene.fbx(
            filepath=export_folder + name + ".fbx",
            check_existing=True,
            filter_glob='*.fbx',
            # use selection ... no ?
            use_selection=True,
            use_active_collection=False,
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_NONE',
            #use_space_transform=True,
            bake_space_transform=False,
            object_types=batch_properties.ObjectTypes,
            use_mesh_modifiers=True,
            use_mesh_modifiers_render=True,
            mesh_smooth_type='OFF',
            use_subsurf=False,
            use_mesh_edges=False,
            use_tspace=False,
            use_custom_props=False,
            add_leaf_bones=True,
            primary_bone_axis='Y',
            secondary_bone_axis='X',
            use_armature_deform_only=False,
            armature_nodetype='NULL',
            bake_anim=True,
            bake_anim_use_all_bones=True,
            bake_anim_use_nla_strips=True,
            bake_anim_use_all_actions=True,
            bake_anim_force_startend_keying=True,
            bake_anim_step=1.0,
            bake_anim_simplify_factor=1.0,
            path_mode=batch_properties.path_mode,
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=True,
            axis_forward=batch_properties.axis_forward,
            axis_up=batch_properties.axis_up,
        )

        # Can be used for multiple formats
        # bpy.ops.export_scene.x3d(filepath=fn + ".x3d", use_selection=True)

        obj.select_set(False)

        #print("written:", fn)

    self.report({'INFO'}, "%s fbx exported successfully." % (len(selection)))

    view_layer.objects.active = obj_active

    for obj in selection:
        obj.select_set(True)
#end main

def gltfexport (self, context):
    """ use gltf export addon """
    view_layer = bpy.context.view_layer

    obj_active = view_layer.objects.active
    selection = bpy.context.selected_objects

    bpy.ops.object.select_all(action='DESELECT')


    # Only embed textures in COPY mode!
    # if embed_textures and path_mode != 'COPY':
    #     embed_textures = False

    batch_properties = bpy.context.scene.batch_exporter

    for obj in selection:

        obj.select_set(True)

        # some exporters only use the active object
        view_layer.objects.active = obj

        name = bpy.path.clean_name(obj.name)
        file_ext = ""
        export_folder = ""

        if batch_properties.export_format == "GLB":
            file_ext = ".glb"
        else:
            file_ext = ".gltf"
        
        if batch_properties.export_multipleFolder:
            export_folder = batch_properties.ExportFolder + name + "\\"
            
            if not os.path.exists(export_folder):
                os.mkdir(export_folder)        

        bpy.ops.export_scene.gltf(
            export_format=batch_properties.export_format,
            ui_tab='GENERAL',
            export_copyright='',
            export_image_format='AUTO',
            export_texture_dir='',
            export_texcoords=True,
            export_normals=True,
            export_draco_mesh_compression_enable=False,
            export_draco_mesh_compression_level=6,
            export_draco_position_quantization=14,
            export_draco_normal_quantization=10,
            export_draco_texcoord_quantization=12,
            #export_draco_color_quantization=10,
            export_draco_generic_quantization=12,
            export_tangents=False,
            export_materials='EXPORT',
            export_colors=True,
            export_cameras=False,
            export_selected=False,
            use_selection=True,
            export_extras=False,
            export_yup=True,
            export_apply=False,
            export_animations=True,
            export_frame_range=True,
            export_frame_step=1,
            export_force_sampling=True,
            export_nla_strips=True,
            export_def_bones=False,
            export_current_frame=False,
            export_skins=True,
            export_all_influences=False,
            export_morph=True,
            export_morph_normal=True,
            export_morph_tangent=False,
            export_lights=False,
            export_displacement=False,
            will_save_settings=False,
            filepath=export_folder + name + file_ext,
            check_existing=True,
        )

        obj.select_set(False)

    #print("written:", fn)

    self.report({'INFO'}, "%s gltf/glb exported successfully." % (len(selection)))

    view_layer.objects.active = obj_active

    for obj in selection:
        obj.select_set(True)

class BatchExportFbx(Operator):
    """Export selected objects to folder"""
    bl_idname = "object.batch_export"
    bl_label = "Export selected objects"

    def invoke(self, context,_event):
        if len(bpy.context.selected_objects) <= 0:
            self.report({'ERROR'}, 'No object selected. Select at least one object.')
        else:
            bpy.ops.object.open_folderbrowser('INVOKE_DEFAULT')
        return {'FINISHED'}

class OpenFolderBrowser(Operator, ExportHelper):
    """Open main export window"""
    bl_idname = "object.open_folderbrowser"
    bl_label = "Select folder"

    # ExportHelper mixin class uses this
    filename_ext = ""

    filter_glob: StringProperty(
        default="",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def draw(self, context):
        scene = context.scene
        batch_exporter = scene.batch_exporter
        layout = self.layout

        if 'FBX' in batch_exporter.ExportFormat:
            layout.label(text="Fbx export options :")
            row = layout.row(align=True)
            row.prop(batch_exporter, "path_mode")
            sub = row.row(align=True)
            sub.enabled = (batch_exporter.path_mode == 'COPY')
            sub.prop(
                batch_exporter,
                "embed_textures",
                text="",
                icon='PACKAGE' if batch_exporter.embed_textures else 'UGLYPACKAGE'
            )

            col = layout.column(align=True)
            col.prop(batch_exporter, "ObjectTypes", text="toto")

            layout.prop(batch_exporter, "axis_forward")
            layout.prop(batch_exporter, "axis_up")

        if 'GLTF' in batch_exporter.ExportFormat:
            layout.label(text="Gltf export options :")
            row = layout.row(align=True)
            row.prop(batch_exporter, "export_format")

        layout.label(text="Global")
        row = layout.row(align=True)
        row.prop(batch_exporter, "export_multipleFolder")

    # Rewrite Invoke to avoid blend_filepath with file name
    def invoke(self, context, _event):
        #if not self.filepath:
        self.filepath = ""

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        bpy.context.scene.batch_exporter.ExportFolder = self.filepath

        scene = context.scene
        batch_exporter = scene.batch_exporter

        if 'FBX' in batch_exporter.ExportFormat:
            fbxexport(self, context)
        if 'GLTF' in batch_exporter.ExportFormat:
            gltfexport(self, context)
        return {'FINISHED'}


def register():
    for cls in classes:
        bpy.utils.register_class(operators)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(operators)

if __name__ == "__main__":
    register()


operators = [
    BatchExportFbx,
    OpenFolderBrowser,
    ]
