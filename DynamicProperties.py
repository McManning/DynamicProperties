from typing import Optional
import bpy

from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)

from bpy.types import (
    PropertyGroup,
    Panel
)

# Base type for `bpy.type.*` classes that can be registered
StructMetaProp = bpy.types.bpy_struct_meta_idprop


def get_key(bpy_type: StructMetaProp, name: str) -> str:
    """Internal method to create a unique key for a dynamic property group

    Args:
        bpy_type (StructMetaProp):  bpy.type containing the dynamic property group
        name (str):                 Name of the dynamic property group
    """
    return '{}{}'.format(bpy_type.__name__, name)


class BaseDynamicPanel(Panel):
    """Base class for panels associated with dynamic property groups

    Attributes:
        bpy_type (StructMetaProp):  bpy.type containing the dynamic property group
        title (str):                Title of this panel
        name (str):                 Name of the dynamic property group to read from the context
        context_attr (str):         Attribute in poll() and draw() contexts to read the
                                    dynamic property group from
    """
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    @classmethod
    def poll(cls, context):
        attr = getattr(context, cls.context_attr)

        # If the context attribute isn't defined, not relevant.
        # E.g. bl_context was `data` but we need to check that
        # it's a light via `context.light is not None`
        if attr is None:
            return False

        props = getattr(attr, cls.name)

        # Skip the panel if this dynamic property group is disabled
        if not props.enabled:
            return False

        # TODO: Other conditions.
        # E.g. if bl_context == 'engine' we need to determine
        # *what* engine it's associated with from somewhere.
        # if bl_context == 'material' we need to determine
        # whether or not this group supports GPENCIL
        return True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        col = layout.column()

        # Pull the dynamic property group associated with the context
        attr = getattr(context, self.context_attr)
        props = getattr(attr, self.name)

        # Iterate through and render editors for each property
        for key, meta in props.meta.items():
            if key == 'enabled':
                continue

            if meta[0] == 'header':
                # Show a dividing header label.
                # Best we can do is a label right now.
                col.separator()
                box = col.box()
                box.label(text=meta[1])
            elif meta[0] == 'image':
                # Render a custom editor for image props that adds new/open buttons
                col.separator()
                col.template_ID(
                    props,
                    key,
                    new='image.new',
                    open='image.open',
                    text=meta[1]
                )
            else:
                # Standard property editor
                col.prop(props, key)


class BaseDynamicPropertyGroup(PropertyGroup):
    """Base class for dynamic property groups

    Attributes:
        bpy_type (StructMetaProp):  bpy.type containing the dynamic property group
        title (str):                Title of this group
        name (str):                 Name of the dynamic property group to associate with the bpy.type
        meta (dict):                Mapping of property keys to a tuple of (prop_type, name, description)
    """

    def items(self) -> dict:
        """Return a dictionary of current property metadata and values

        Returns:
            dict:   Mapping property key to a tuple of (type, value)
                    where type is one of `float`, `vec3`, `image`, etc
                    matching the `DynamicProperties.add_*` method that created it.
        """
        items = dict()
        for key, meta in self.meta.items(): # meta being ('vec3', name, description)
            if key != 'enabled' and meta[0] != 'header': # skip the internal `enabled` flag prop
                items[key] = (meta[0], getattr(self, key))

        return items

    @classmethod
    def register(cls):
        setattr(cls.bpy_type, cls.name, PointerProperty(
            name=cls.title,
            description='',
            type=cls
        ))

    @classmethod
    def unregister(cls):
        delattr(cls.bpy_type, cls.name)


class PropertyCollection:
    """A set of bpy.type.*Property instances that can be added/removed from.

    Attributes:
        props (dict): Mapping between a property key and the bpy.type.*Property method
        meta (dict): Mapping between a property key and a tuple (type_str, name, description)
    """
    def __init__(self, enabled: bool = True):
        """
        Args:
            enabled (bool): Should the group be enabled by default on new instances
        """
        self.clear(enabled)

    def add_header(self, key: str, text: str):
        """Add a header to separate groups of related properties in the UI

        Args:
            key (str):  Unique key
            text (str): Header text used in the user interface
        """
        self.meta[key] = ('header', text, '')

    def add_float(self, key: str, name: str, **kwargs):
        """Add a float

        Args:
            key (str):  Unique key
            name (str): Name used in the user interface

        Keyword Args:
            Accepts bpy.props.FloatProperty kwargs
        """
        args = {
            'name': name,
        }

        args = {**kwargs, **args}
        self.props[key] = FloatProperty(**args)
        self.meta[key] = ('float', name, kwargs.get('description', ''))

    def add_bool(self, key: str, name: str, **kwargs):
        """Add a boolean

        Args:
            key (str):  Unique key
            name (str): Name used in the user interface

        Keyword Args:
            Accepts bpy.props.BoolProperty kwargs
        """
        args = {
            'name': name,
        }

        args = {**kwargs, **args}
        self.props[key] = BoolProperty(**args)
        self.meta[key] = ('bool', name, kwargs.get('description', ''))

    def add_str(self, key: str, name: str, **kwargs):
        """Add a string

        Args:
            key (str):  Unique key
            name (str): Name used in the user interface

        Keyword Args:
            Accepts bpy.props.StringProperty kwargs
        """
        args = {
            'name': name,
        }

        args = {**kwargs, **args}
        self.props[key] = StringProperty(**args)
        self.meta[key] = ('str', name, kwargs.get('description', ''))

    def add_vec2(self, key: str, name: str, **kwargs):
        """Add a 2 dimensional vector of floats.

        Args:
            key (str):  Unique key
            name (str): Name used in the user interface

        Keyword Args:
            Accepts bpy.props.FloatVectorProperty kwargs
        """
        args = {
            'size': 2,
            'name': name,
        }

        args = {**kwargs, **args}
        self.props[key] = FloatVectorProperty(**args)
        self.meta[key] = ('vec2', name, kwargs.get('description', ''))

    def add_vec3(self, key: str, name: str, **kwargs):
        """Add a 3 dimensional vector of floats.

        Args:
            key (str):  Unique key
            name (str): Name used in the user interface

        Keyword Args:
            Accepts bpy.props.FloatVectorProperty kwargs
        """
        args = {
            'size': 3,
            'name': name,
        }

        args = {**kwargs, **args}
        self.props[key] = FloatVectorProperty(**args)
        self.meta[key] = ('vec3', name, kwargs.get('description', ''))

    def add_rgb(self, key: str, name: str, **kwargs):
        """Add an RGB color

        Args:
            key (str):  Unique key
            name (str): Name used in the user interface

        Keyword Args:
            Accepts bpy.props.FloatVectorProperty kwargs
        """
        args = {
            'size': 3,
            'name': name,
            'subtype': 'COLOR',
            'min': 0.0,
            'max': 1.0
        }

        args = {**kwargs, **args}
        self.props[key] = FloatVectorProperty(**args)
        self.meta[key] = ('rgb', name, kwargs.get('description', ''))

    def add_rgba(self, key: str, name: str, **kwargs):
        """Add an RGBA color

        Args:
            key (str):  Unique key
            name (str): Name used in the user interface

        Keyword Args:
            Accepts bpy.props.FloatVectorProperty kwargs
        """
        args = {
            'size': 4,
            'name': name,
            'subtype': 'COLOR',
            'min': 0.0,
            'max': 1.0
        }

        args = {**kwargs, **args}
        self.props[key] = FloatVectorProperty(**args)
        self.meta[key] = ('rgba', name, kwargs.get('description', ''))

    def add_enum(self, key: str, name: str, **kwargs):
        """Add a dropdown enum of options

        Args:
            key (str):  Unique key
            name (str): Name used in the user interface

        Keyword Args:
            Accepts bpy.props.EnumProperty kwargs
        """
        args = {
            'name': name,
        }

        args = {**kwargs, **args}
        self.props[key] = EnumProperty(**args)
        self.meta[key] = ('enum', name, kwargs.get('description', ''))

    def add_file(self, key: str, name: str, **kwargs):
        """Add a filename picker

        Args:
            key (str):  Unique key
            name (str): Name used in the user interface

        Keyword Args:
            Accepts bpy.props.StringProperty kwargs
        """
        args = {
            'name': name,
            'subtype': 'FILE_PATH',
        }

        args = {**kwargs, **args}
        self.props[key] = StringProperty(**args)
        self.meta[key] = ('file', name, kwargs.get('description', ''))

    def add_dir(self, key: str, name: str, **kwargs):
        """Add a directory picker

        Args:
            key (str):  Unique key
            name (str): Name used in the user interface

        Keyword Args:
            Accepts bpy.props.StringProperty kwargs
        """
        args = {
            'name': name,
            'subtype': 'DIR_PATH',
        }

        args = {**kwargs, **args}
        self.props[key] = StringProperty(**args)
        self.meta[key] = ('dir', name, kwargs.get('description', ''))

    def add_image(self, key: str, name: str, description: str = ''):
        """Add an image selector

        Args:
            key (str):          Unique key
            name (str):         Name used in the user interface
            description (str):  Text used for the tooltip and API documentation
        """
        # Typically, accessing bpy.types.* would be unsafe
        # while loading addons during boot. But since this
        # is a dynamically registered instance, it's assumed
        # this ends up being registered after initial load.
        self.props[key] = PointerProperty(
            name=name,
            description=description,
            type=bpy.types.Image
        )
        self.meta[key] = ('image', name, description)

    def remove(self, key: str):
        """Remove a property by key

        Args:
            key (str): The key to remove
        """
        if key in self.props:
            del self.props[key]

        if key in self.meta:
            del self.meta[key]

    def clear(self, enabled: bool = True):
        """Clear all previously registered properties

        Args:
            enabled (bool): Should the group be enabled by default on new instances
        """
        self.props = dict()
        self.meta = dict()

        # We add an extra prop to indicate whether this collection is enabled
        self.add_bool('enabled', name='enabled', default=enabled, options={'HIDDEN'})


class DynamicProperties(PropertyCollection):
    """Management for a dynamic property group and an associated panel

    Attributes:
        bpy_type (StructMetaProp):      bpy.type to use the dynamic PropertyGroup
        name (str):                     Unique name for this property group.
        title (str):                    Title used for the associated panel
        registered_properties (dict):   Mapping a DynamicProperties name to an instance.
                                        This tracks all instances registered with Blender
    """
    registered_properties = dict()

    def __init__(self, bpy_type: StructMetaProp, name: str, title: str, enabled: bool = True, panel_parent_id: str = ''):
        """
        Args:
            bpy_type (StructMetaProp):  bpy.type to use the dynamic PropertyGroup

            name (str):                 Unique name for this property group.
                                        Will be used as the PropertyGroup accessor
                                        on the associated bpy.type

            title (str):                Title used for the associated panel

            enabled (bool):             Should the panel of this property group
                                        be displayed in the UI

            panel_parent_id (str):      `bl_parent_id` for the associated panel
        """
        super().__init__(enabled)

        self.bpy_type = bpy_type
        self.name = name
        self.title = title
        self.panel_parent_id = panel_parent_id

    def register(self, base_property_group = BaseDynamicPropertyGroup, base_panel = BaseDynamicPanel):
        """Register this property group and panel with Blender

        After adding/removing properties, call this again
        to ensure Blender PropertyGroups and Panels are synced.
        """
        type_name = self.bpy_type.__name__
        key = get_key(self.bpy_type, self.name)

        property_class = type(
            key + 'PropertyGroup',
            (base_property_group,),
            { '__annotations__': self.props }
        )
        property_class.bpy_type = self.bpy_type
        property_class.name = self.name
        property_class.title = self.title
        property_class.meta = self.meta

        panel_class = type(
            'DYNAMIC_PT_' + key,
            (base_panel,),
            {}
        )
        panel_class.bpy_type = self.bpy_type
        panel_class.name = self.name
        panel_class.title = self.title
        panel_class.bl_label = self.title
        panel_class.bl_parent_id = self.panel_parent_id

        # TODO: Less shitty mapping technique.
        # We need to determine the appropriate poll()
        # test, as well as a bl_context to add the panel.
        if type_name == 'Light':
            panel_class.bl_context = 'data'
            panel_class.context_attr = 'light'
        elif type_name == 'Material':
            panel_class.bl_context = 'material'
            panel_class.context_attr = 'material'
            # This is a bit more complicated - context.material or context.object
            # and skip GPENCIL (context.active_object.type == 'GPENCIL')
            # maybe we can hand off some evaluator method per type?
        elif type_name == 'Object':
            panel_class.bl_context = 'object'
            panel_class.context_attr = 'object'
        elif type_name == 'RenderEngine':
            panel_class.bl_context = 'render'
            panel_class.context_attr = 'engine'
            # TODO: would need to somehow poll() that engine == specific engine name as well
        else:
            raise TypeError('DynamicProperties cannot be associated to type {}'.format(self.bpy_type))

        # Unregister the previous instance if it exists
        # TODO: If a group was re-registered with different properties,
        # would it make sense to diff and directly delete each property value
        # that isn't in the new group? I could see that being useful, but I can
        # also see issues with losing data when accidentally switching groups
        # (e.g. toggling between different shaders for a material)
        self.unregister()

        # And finally register the new instances
        bpy.utils.register_class(property_class)
        bpy.utils.register_class(panel_class)

        self.property_class = property_class
        self.panel_class = panel_class
        self.registered_properties[key] = self

    def unregister(self):
        """Unregister this property group and panel from Blender"""
        try:
            bpy.utils.unregister_class(self.property_class)
        except:
            pass

        try:
            bpy.utils.unregister_class(self.panel_class)
        except:
            pass

        try:
            key = get_key(self.bpy_type, self.name)
            del self.registered_properties[key]
        except:
            pass

        self.property_class = None
        self.panel_class = None

    @classmethod
    def find(cls, bpy_type: StructMetaProp, name: str) -> Optional['DynamicProperties']:
        """Find a registered DynamicProperties instance.

        This can be used to locate an existing instance
        to add and remove properties when needed.

        Args:
            bpy_type (StructMetaProp):      bpy.type using the dynamic PropertyGroup
            name (str):                     Unique name for the property group.

        Returns:
            Optional[DynamicProperties]
        """
        key = get_key(bpy_type, name)
        return cls.registered_properties.get(key)
