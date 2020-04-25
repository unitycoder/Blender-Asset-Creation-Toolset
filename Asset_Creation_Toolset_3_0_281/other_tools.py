import bpy

from bpy.props import StringProperty


#-------------------------------------------------------
#Clear Custom Split Normals
class Clear_Normals(bpy.types.Operator):
	"""Clear Custom Split Normals"""
	bl_idname = "object.clear_normals"
	bl_label = "Clear Custom Split Normals"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		selected_obj = bpy.context.selected_objects
		active_obj = bpy.context.active_object
		
		for x in selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			x.select_set(True)
			if x.type == 'MESH':
				bpy.context.view_layer.objects.active = x
				bpy.ops.mesh.customdata_custom_splitnormals_clear()
				bpy.context.object.data.auto_smooth_angle = math.pi
				bpy.context.object.data.use_auto_smooth = True
				
		# Select again objects
		for j in selected_obj:
			j.select_set(True)
		
		bpy.context.view_layer.objects.active = active_obj					
		return {'FINISHED'}		
		
#-------------------------------------------------------
#Recalculate Normals
class Calc_Normals(bpy.types.Operator):
	"""Recalculate Normals"""
	bl_idname = "object.calc_normals"
	bl_label = "Flip/Calculate Normals"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		act = context.scene.act
		
		selected_obj = bpy.context.selected_objects
		active_obj = bpy.context.active_object
		
		for x in selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			x.select_set(True)
			if x.type == 'MESH':
				bpy.context.view_layer.objects.active = x
				bpy.ops.object.mode_set(mode = 'EDIT')
				bpy.ops.mesh.reveal()
				bpy.ops.mesh.select_all(action='SELECT')
				if act.calc_normals_en == False:
					bpy.ops.mesh.flip_normals()
				else:
					bpy.ops.mesh.normals_make_consistent(inside=act.normals_inside)
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode='OBJECT')
				
		# Select again objects
		for j in selected_obj:
			j.select_set(True)
		
		bpy.context.view_layer.objects.active = active_obj
		return {'FINISHED'}


#-------------------------------------------------------
#Obj Name to Mesh Name
class Obj_Name_To_Mesh_Name(bpy.types.Operator):
	"""Obj Name to Mesh Name"""
	bl_idname = "object.objname_to_meshname"
	bl_label = "Obj Name to Mesh Name"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		current_selected_obj = bpy.context.selected_objects
		
		for x in current_selected_obj:
			if x.type == 'MESH':
				x.data.name = x.name
		return {'FINISHED'}


#-------------------------------------------------------
#Merge Bones
class Merge_Bones(bpy.types.Operator):
	"""Merge Selected Bones to Active"""
	bl_idname = "object.merge_bones"
	bl_label = "Merge Selected Bones to Active"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		act = context.scene.act

		#BUG!! Active Bone not updating if switch MODE frome POSE to EDIT
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.mode_set(mode='EDIT')

		armature = bpy.context.active_object
		active_bone_name = armature.data.bones.active.name
		selected_bones_name = []

		bpy.ops.object.mode_set(mode='OBJECT')

		#Collect Selected Bones, but Not Active
		for bone in armature.data.bones:
			if bone.select == True:
				if bone.name != active_bone_name:
					selected_bones_name.append(bone.name)

		#Find Mesh Deformed with this Armature
		for m in bpy.context.scene.objects:
			if m.type == 'MESH':
				if (len(m.modifiers) > 0):
					for n in m.modifiers:
						if n.type == 'ARMATURE' and n.object.name_full == armature.name_full:
							parent_mesh = m

		bpy.ops.object.select_all(action='DESELECT')
		parent_mesh.select_set(True)
		bpy.context.view_layer.objects.active = parent_mesh

		if len(selected_bones_name) > 0:
			for b_name in selected_bones_name:
				try:
					parent_mesh.vertex_groups.active_index = parent_mesh.vertex_groups[b_name].index
				except:
					continue

				bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
						
				parent_mesh.modifiers['VertexWeightMix'].vertex_group_a = active_bone_name
				parent_mesh.modifiers['VertexWeightMix'].vertex_group_b = b_name
				parent_mesh.modifiers['VertexWeightMix'].mix_mode = 'ADD'
				parent_mesh.modifiers['VertexWeightMix'].mix_set = 'ALL'
				
				bpy.ops.object.modifier_apply(apply_as='DATA', modifier="VertexWeightMix")

				bpy.ops.object.vertex_group_remove()

		bpy.ops.object.select_all(action='DESELECT')
		armature.select_set(True)
		bpy.context.view_layer.objects.active = armature
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.armature.select_all(action='DESELECT')
		bpy.ops.object.mode_set(mode='OBJECT')

		for need_delete in selected_bones_name:
			try:
				armature.data.bones[need_delete].select = True
			except:
				continue
			bpy.ops.object.mode_set(mode='EDIT')
			if act.merge_bones_method == 'DELETE':
				bpy.ops.armature.delete()
			elif act.merge_bones_method == 'DISSOLVE':
				bpy.ops.armature.dissolve()
			bpy.ops.object.mode_set(mode='OBJECT')

		armature.data.bones[active_bone_name].select = True
		bpy.ops.object.mode_set(mode='EDIT')

		return {'FINISHED'}


#-------------------------------------------------------
#Panels
class VIEW3D_Other_Tools_Panel(bpy.types.Panel):
	bl_label = "Other Tools"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "ACT"

	@classmethod
	def poll(self, context):
		return (context.object is not None and (context.object.mode == 'OBJECT' or context.mode == 'EDIT_ARMATURE'))

	def draw(self, context):
		act = context.scene.act
		
		layout = self.layout
		row = layout.row()	

		if context.object is not None:
			if context.object.mode == 'EDIT':
				row = layout.row()
		
		if context.object is not None:
			if context.mode == 'OBJECT':
				row = layout.row()	
				row.operator("object.objname_to_meshname", text="Obj Name -> Mesh Name")
				layout.separator()

				row = layout.row()
				row.operator("object.clear_normals", text="Clear Custom Normals")
				
				row = layout.row()
				row.operator("object.calc_normals", text="Flip/Calculate Normals")
				layout.prop(act, "calc_normals_en", text="Recalc Normals")
				if act.calc_normals_en:
					layout.prop(act, "normals_inside", text="Inside")
				layout.separator()
				

			if context.mode == 'EDIT_ARMATURE':
				#Split row
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(factor=0.4, align=True)
				c = split.column()
				c.label(text="Method")
				split = split.split()
				c = split.column()
				c.prop(act, "merge_bones_method", text="", expand=False)
				#----
				row = layout.row()
				row.operator("object.merge_bones", text="Merge Bones")


classes = (
	Clear_Normals,
	Calc_Normals,
	Obj_Name_To_Mesh_Name,
	Merge_Bones,
	VIEW3D_Other_Tools_Panel,
)	


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)