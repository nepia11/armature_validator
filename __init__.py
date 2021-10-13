# Copyright (c) 2021 nepia11
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


import bpy
import pprint

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


def is_top_level_bone(bone: bpy.types.Bone):
    """親のいないボーンを探す"""
    if bone.parent is None:
        return True
    else:
        return False


def search_bone(bone: bpy.types.Bone):
    """
    ボーンの子を再帰的に探査する
    {bone_name.bone_name.bone_name....}みたいなつながりで返すようにしたい
    """
    children = list(bone.children)
    if children == []:
        return {bone.name: None}
    else:
        children_dict = {}
        for child in children:
            child_dict = search_bone(child)
            children_dict.update(child_dict)
        bone_dict = {bone.name: children_dict}
        return bone_dict


def armature_to_dict(armature: bpy.types.Armature):
    top_level_bones = [b for b in armature.bones if is_top_level_bone(b)]
    hierarchy = {}
    for bone in top_level_bones:
        tree = search_bone(bone)
        hierarchy.update(tree)
    return hierarchy


class Show_Armature_Hierarchy_Operator(bpy.types.Operator):

    bl_idname = "armature.show_hierarchy"
    bl_label = "show hierarchy"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        try:
            if context.active_object.type == "ARMATURE":
                return True
            return False
        except AttributeError:
            return False

    def execute(self, context: bpy.context):
        obj = context.active_object
        if obj.type == "ARMATURE":
            armature: bpy.types.Armature = obj.data
            armature_dict = armature_to_dict(armature)
            msg = pprint.pformat(armature_dict, compact=True)
            self.report({"INFO"}, msg)
        return {"FINISHED"}


def menu_fn(self, context):
    self.layout.operator("armature.show_hierarchy")


# Registration
classes = [Show_Armature_Hierarchy_Operator]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_fn)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_fn)


if __name__ == "__main__":
    register()
