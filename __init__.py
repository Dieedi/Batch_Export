bl_info = {
    "name": "Batch Exporter",
    "description": "Export multiple objects to fbx files named as the objects are.",
    "author": "Jeremy Pouillot",
    "version": (0, 1, 4),
    "blender": (2, 91, 0),
    "location": "View3D > Tool Shelf > Tool Tab",
    "warning": "WIP",
    "doc_url": "none",
    "category": "Import-Export",
}

import bpy, os, importlib

from bpy.props import StringProperty, BoolProperty
from bpy.props import (
        BoolProperty,
        IntProperty,
        FloatProperty,
        EnumProperty,
        CollectionProperty,
        StringProperty,
        FloatVectorProperty,
        )
from . import operators
from bpy_extras.io_utils import (
    ExportHelper,
    path_reference_mode,
    orientation_helper,
)

if 'bpy' in locals():
    importlib.reload(operators)

from bpy.types import (
        AddonPreferences,
        PropertyGroup,
        )

@orientation_helper(axis_forward='-Z', axis_up='Y')
class BatchexporterSettings(bpy.types.PropertyGroup):
    # The path !
    # https://docs.blender.org/api/current/bpy.props.html#bpy.props.StringProperty
    ExportFolder: StringProperty(
        name="ExportFolder",
        default="" #bpy.context.user_preferences.filepaths.temporary_directory
        )
    ExportFormat: EnumProperty(
        name="Export format",
        options={'ENUM_FLAG'},
        items=(
            ('FBX', "Fbx", ""),
            ('GLTF', "Gltf", ""),
        ),
        description="Which format needed",
        default={'FBX'},
    )
    # Fbx Properties
    ObjectTypes: EnumProperty(
        name="Object Types",
        options={'ENUM_FLAG'},
        items=(
            ('EMPTY', "Empty", ""),
            ('CAMERA', "Camera", ""),
            ('LIGHT', "Lamp", ""),
            ('ARMATURE', "Armature", "WARNING: not supported in dupli/group instances"),
            ('MESH', "Mesh", ""),
            ('OTHER', "Other", "Other geometry types, like curve, metaball, etc. (converted to meshes)"),
        ),
        description="Which kind of object to export",
        default={'MESH'},
    )
    path_mode: path_reference_mode
    embed_textures: BoolProperty(
        name="Embed Textures",
        description="Embed textures in FBX binary file (only for \"Copy\" path mode!)",
        default=False,
    )
    # Gltf Properties
    export_format: EnumProperty(
        name='Format',
        items=(('GLB', 'glTF Binary (.glb)',
                'Exports a single file, with all data packed in binary form. '
                'Most efficient and portable, but more difficult to edit later'),
               ('GLTF_EMBEDDED', 'glTF Embedded (.gltf)',
                'Exports a single file, with all data packed in JSON. '
                'Less efficient than binary, but easier to edit later'),
               ('GLTF_SEPARATE', 'glTF Separate (.gltf + .bin + textures)',
                'Exports multiple files, with separate JSON, binary and texture data. '
                'Easiest to edit later')),
        description=(
            'Output format and embedding options. Binary is most efficient, '
            'but JSON (embedded or separate) may be easier to edit later'
        ),
        default='GLB',
    )

    export_multipleFolder: BoolProperty(
        name='Export Multiple Folder',
        description="Export selected objects to independent folders named as each object",
        default=False,
    )

# Create Menus
class VIEW3D_PT_FbxBatchExportPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "Tool"
    bl_label = "Fbx Batch Export"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        batch_exporter = scene.batch_exporter

        # Format Selection
        layout.label(text="Needed format :")

        col = layout.column(align=True)
        col.prop(batch_exporter, "ExportFormat", text="toto")

        # Create the Export button
        layout.label(text="Export Selection :")
        row = layout.row()
        row.scale_y = 2.0
        # Add operator call to button
        row.operator("object.batch_export")

panels = (
    VIEW3D_PT_FbxBatchExportPanel,
    )

def update_panel(self, context):
    message = "Fbx batch export: Updating Panel locations has failed"
    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)

        for panel in panels:
            panel.bl_category = context.preferences.addons[__name__].preferences.category
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass

class BatchexporterAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    category: StringProperty(
            name="Tab Category",
            description="Choose a name for the category of the panel",
            default="Edit",
            update=update_panel
            )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        col = row.column()
        col.label(text="Tab Category:")
        col.prop(self, "category", text="")

# REGISTER
classes = operators.operators + \
        [
            BatchexporterSettings,
        ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    for panel in panels:
        bpy.utils.register_class(panel)

    bpy.types.Scene.batch_exporter = bpy.props.PointerProperty(name="parameters", type=BatchexporterSettings)

def unregister():
    for panel in panels:
        bpy.utils.unregister_class(panel)

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.batch_exporter

if __name__ == "__main__":
    register()
