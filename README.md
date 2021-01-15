# DynamicProperties

Addon API for dynamically creating and updating PropertyGroups at runtime in Blender 2.8+

This is built to be used by other addons and is not a standalone addon itself.

## Features

* Define new `bpy.types.PropertyGroup` instances at runtime from some external data source (e.g. ShaderLab property blocks, GLSL uniforms, linked Unity materials, etc)
* Automatic creation and configuration of a `bpy.types.Panel` to render an editor for the dynamic `PropertyGroup`.

## Usage

Creating a new dynamic PropertyGroup:

```py
# Somewhere in your addon, instantiate a new DynamicProperties
shader_uniforms = DynamicProperties(
    bpy.types.Material,
    'shader_uniforms',
    'Shader Uniforms'
)

# Add properties - presumably from some external source
shader_uniforms.add_color3(
    'ambient_color',
    name='Ambient Color',
    description='Color of ambient lighting'
)

shader_uniforms.add_float(
    'opacity',
    name='Opacity',
    description='Uniform model opacity',
    # Supports kwargs of bpy.types.FloatProperty
    default=1.0,
    min=0.0,
    max=1.0
)

# Register the updated properties with Blender
shader_uniforms.register()
```

Reading from a dynamic PropertyGroup:

```py
props = bpy.data.materials[0].shader_uniforms

# Retrieve a specific property
print(props.ambient_color)
# -> <Color (r=0.0000, g=0.0000, b=0.0000)>

# Iterate through all available properties
for name, meta in props.items():
    prop_type = meta[0] # color3, float, bool, image, etc
    value = meta[1]
    print(name, prop_type, value)

    # -> ambient_color color3 <Color (r=0.0000, g=0.0000, b=0.0000)>
    # -> opacity float 1.0
```

Replacing properties at runtime:

```py
# Find a previously registered group
shader_uniforms = DynamicProperties.find(
    bpy.types.Material,
    'shader_uniforms'
)

# Clear old properties and add new ones.
# Can also do .remove('key') to remove specific properties
# or just add new properties to the existing set.
shader_uniforms.clear()

shader_uniforms.add_color3(
    'ambient_color',
    name='Ambient Color',
    description='Color of ambient lighting'
)

# Register the changes with Blender.
shader_uniforms.register()
```

Destroying a property group and panel:

```py
# Find a previously registered group
shader_uniforms = DynamicProperties.find(
    bpy.types.Material,
    'shader_uniforms'
)

shader_uniforms.unregister()
```

Disabling a property group (hides the Panel from the instance's UI):

```py
bpy.data.materials[0].shader_properties.enabled = False
```

## More Examples

Look at `demo.py` for an example of swapping the active dynamic property group on a type by using a separate PropertyGroup to track the active instance.
