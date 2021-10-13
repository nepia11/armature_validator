# Copyright (c) 2021 nepia11
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


import bpy
from bpy.types import Armature, Bone, Operator
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


def is_top_level_bone(bone: Bone):
    """親のいないボーンを探す"""
    if bone.parent is None:
        return True
    else:
        return False


def search_bone(bone: Bone):
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


def search_bone_topology(bone: Bone):
    children = list(bone.children)
    count = len(children)
    if count == 0:
        return [0]
    else:
        c_counts = []
        for child in children:
            child_count = search_bone_topology(child)
            c_counts.append(child_count)
        c_counts.sort()
        return [count, c_counts]


def armature_to_topology(armature: Armature):
    top_level_bones = [b for b in armature.bones if is_top_level_bone(b)]
    hierarchy = []
    for bone in top_level_bones:
        tree = search_bone_topology(bone)
        hierarchy.append(tree)
    hierarchy.sort()
    return hierarchy


def armature_to_dict(armature: Armature):
    top_level_bones = [b for b in armature.bones if is_top_level_bone(b)]
    hierarchy = {}
    for bone in top_level_bones:
        tree = search_bone(bone)
        hierarchy.update(tree)
    return hierarchy


def check_valid_armature(A: Armature, B: Armature):
    A_keys = set(A.bones.keys())
    B_keys = set(B.bones.keys())
    only_A = A_keys - B_keys
    only_B = B_keys - A_keys
    A_and_B = A_keys & B_keys
    invalids = []

    if A_keys == B_keys:
        for key in A_keys:
            if not A.bones[key].parent is None:
                A_parent = A.bones[key].parent.name
            else:
                A_parent = None
            if not B.bones[key].parent is None:
                B_parent = B.bones[key].parent.name
            else:
                B_parent = None
            if not A_parent == B_parent:
                invalids.append(B.bones[key])
    result = dict(only_A=only_A, only_B=only_B, invalid_parent=invalids)
    return result


def check_valid_armature_topology(A: Armature, B: Armature):
    A_topo = armature_to_topology(A)
    B_topo = armature_to_topology(B)
    if A_topo == B_topo:
        return True
    else:
        return False


class Show_Armature_Hierarchy_Operator(Operator):

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
            armature: Armature = obj.data
            armature_dict = armature_to_dict(armature)
            armature_topo = armature_to_topology(armature)
            msg = pprint.pformat(armature_dict, compact=True)
            msg = f"{msg}\n topology:{pprint.pformat(armature_topo, compact=True)}"
            self.report({"INFO"}, msg)
        return {"FINISHED"}


class Check_Armature_Hierarchy_Operator(Operator):

    bl_idname = "armature.check_hierarchy"
    bl_label = "check hierarchy"
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
        active = context.active_object
        selects = context.selected_objects
        selects = set(selects) - set([active])
        for obj in selects:
            if obj.type == "ARMATURE":
                result = check_valid_armature(active.data, obj.data)
                topo_result = check_valid_armature_topology(active.data, obj.data)
                msg = pprint.pformat(result, compact=True)
                msg = (
                    f"<A = {active.name}>,<B = {obj.name}> Comparison results:\n"
                    f"{msg}\n"
                    f"topology:{topo_result}"
                )
                self.report({"INFO"}, msg)
        return {"FINISHED"}


def menu_fn(self, context):
    self.layout.operator("armature.show_hierarchy")
    self.layout.operator("armature.check_hierarchy")


# Registration
classes = [
    Show_Armature_Hierarchy_Operator,
    Check_Armature_Hierarchy_Operator,
]


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
