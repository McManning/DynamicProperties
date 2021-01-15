
class DEMO_OT_change_fizz(bpy.types.Operator):
    """Example of replacing properties in a dynamic property group at runtime"""
    bl_idname = 'demo_toggle.change_fizz'
    bl_label = 'Change Fizz Properties'

    def invoke(self, context, event):
        fizz = DynamicProperties.find(bpy.types.Light, 'fizz')
        if not fizz:
            raise Exception('`fizz` is not registered')

        # Clear out all old properties.
        # Alternatively, you can do a .remove('prop_name') per property
        fizz.clear()

        # Existing ones we keep (current values will be maintained)
        fizz.add_float('my_float', name='Foo Float', description='Test float')
        fizz.add_rgb('diffuse', name='Diffuse', description='Diffuse color')

        # New ones to add
        fizz.add_float('float2', name='Newer Float', description='Test float 2')
        fizz.add_bool('bool2', name='Newer Bool', description='Test Boolean 2')
        fizz.add_str('str2', name='Newer String', description='Test String 2')

        # Register changes with Blender.
        fizz.register()

        return {'FINISHED'}


class DEMO_PT_Toggle_DynamicPropertyGroups(bpy.types.Panel):
    bl_label = 'Toggle Dynamic Property Group'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context):
        return context.light

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        col = layout.column()

        col.prop(context.light.demo_toggle, 'active_group')

        # # If there's no active group yet, set one automatically
        # if len(context.light.demo_toggle.active_group) < 1:

def update_active_group(self, context):
    """Switch enabled status between two dynamic property groups based on the selected active_group"""
    active = context.light.demo_toggle.active_group
    if active == 'fizz':
        context.light.buzz.enabled = False
        context.light.fizz.enabled = True
    else:
        context.light.buzz.enabled = True
        context.light.fizz.enabled = False


class DemoToggleSettings(bpy.types.PropertyGroup):
    active_group: bpy.props.EnumProperty(
        name='Active Group',
        # You would dynamically populate this based on... whatever
        # (shaders available, etc)
        items=[
            ('fizz', 'Fizz', 'Use the fizz property group'),
            ('buzz', 'Buzz', 'Use the buzz property group'),
        ],
        update=update_active_group,
        default='fizz'
    )

    @classmethod
    def register(cls):
        bpy.types.Light.demo_toggle = PointerProperty(
            name='Toggle Dynamic Property Group',
            type=cls
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Light.demo_toggle


# To nest the dynamic properties under the toggle demo's panel
parent_id = 'DEMO_PT_Toggle_DynamicPropertyGroups'

# Dynamic property group - setup and configure
fizz = DynamicProperties(bpy.types.Light, 'fizz', 'Fizz Settings', panel_parent_id=parent_id)
fizz.add_float('my_float', name='Foo Float', description='Test float')
fizz.add_bool('my_bool', name='Foo Bool', description='Test Boolean')
fizz.add_str('my_str', name='Foo String', description='Some string description')
fizz.add_vec2('my_v2', name='Vec2 Test', description='Test Vec2')
fizz.add_vec3('my_v3', name='Vec3 Test', description='Test Vec3')
fizz.add_rgb('diffuse', name='Diffuse', description='Diffuse color')
fizz.add_rgba('rgba', name='RGBA Color')

fizz.add_enum('my_enum', name='My Enum', description='Some Enum',
    items=[('foo', 'Foo', 'Foo Description'), ('bar', 'Bar', 'Bar Description')]
)

fizz.add_header('my_header', 'More Complicated Examples')

fizz.add_file('my_file', name='Filename', description='Some file to load')
fizz.add_file('my_dir', name='Directory', description='Some directory to load')

fizz.add_header('my_header_2', 'Another Group Of Stuff')
fizz.add_image('diffuse_tex', name='Diffuse Texture', description='Image file for diffuse texture')

# Another set - disabled by default
buzz = DynamicProperties(bpy.types.Light, 'buzz', 'Buzz Settings', enabled=False, panel_parent_id=parent_id)
buzz.add_float('my_float', name='Bar Float', description='Test float')
buzz.add_str('my_str', name='Bar String', description='Some string description')


def register():
    # Demo stuff
    bpy.utils.register_class(DEMO_PT_Toggle_DynamicPropertyGroups)
    bpy.utils.register_class(DEMO_OT_change_fizz)
    bpy.utils.register_class(DemoToggleSettings)

    # Can happen at plugin register() or any time after
    fizz.register()
    buzz.register()


def unregister():
    # Demo stuff
    bpy.utils.unregister_class(DemoToggleSettings)
    bpy.utils.unregister_class(DEMO_OT_change_fizz)
    bpy.utils.unregister_class(DEMO_PT_Toggle_DynamicPropertyGroups)

    # Can happen at plugin unregister() or any time before
    fizz.unregister()
    buzz.unregister()


if __name__ == "__main__":
    register()
