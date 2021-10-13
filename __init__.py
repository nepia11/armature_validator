# Copyright (c) 2021 nepia11
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


import bpy
import rna_keymap_ui
from bl_i18n_utils.settings import LANGUAGES

bl_info = {
    "name": "Armature Validator",
    "author": "nepia11",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "description": "アーマチュアの構造を検証するよ",
    "location": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Armature",
}


class TEST_Operator(bpy.types.Operator):

    bl_idname = "object.hoge"
    bl_label = "operator label"

    def execute(self, context):
        return {"FINISHED"}


# Registration
classes = [TEST_Operator]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
