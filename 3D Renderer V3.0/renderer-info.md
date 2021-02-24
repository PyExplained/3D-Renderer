# This is a list of classes with their variables and methods
<sub><sub> (Written using Markdown) <br> </sub></sub>
<sub> Examples of how to create instances of these classes and 
how to use basic functions that are implemented in the renderer, can be found in the example-scenes, 
including the basic format of making and rendering a scene. <br> 
The controller-class isn't discussed in this file, you can find explanation about it in the example-scenes.</sub>

## CUBES, CUBOIDS AND 3D-MODELS:
### METHODS:
- delete()
- make_visible() and make_invisible()
- change_var(var_name, value) -> *changes variable called var_name (string) for each of its plates (=polygons)*
- move(x, y, z)
- rotate(x_angle, y_angle, z_angle, center='self') -> *center is optional, either 'self' or 
coordinate (array / tuple / list of size 3)*

## PLATES AND SPHERES:
<sub> Clarification: "plate" is quite a confusing name, it's more like a polygon. </sub>

### METHODS: 
same as above (rotate only for plate)

### VARIABLES: 
#### --- Basic renderer ---
- shading *(bool: when True, basic shading gets applied in the renderer, doesn't affect raytracing)*
- fill *(array (size 3, RGB) / list / tuple / color name as string: color of object)*
- outline *(hex or color name as string: outline-color)*
- outline_thickness *(float / int: thickness of outline)*
- radius *(float / int: only for spheres and plates consisting of one point)*
- alpha *(int, only 25, 50, 75 and 100 are allowed: basic transparency in renderer, only for plates, 
        doesn't affect raytracing)*
- visible *(bool: visible for cameras)*
- ray_tracer_visible *(bool: visible for 'rays')*
- xangle, yangle, zangle *(int / float)*

#### --- Raytracing Only ---  
% = percentage *(float / int: in interval: [0, 100])*
- fill and ray_tracer_visible also apply to raytracing
- unbounded *(bool: only for plates, makes plate stretch to infinity when True, True: plate => plane, False: plate => polygon)*
- shadows *(%: default=100, effect / influence of shadows and highlights on color of object)*
- reflectiveness *(%: effect / influence of reflections on color of object)*

(refraction:)
- transparency *(%: effect / influence of refracted ray-color on object)*
- ior *(float / int: default=1, index of refraction, air≈1, water≈1.3, glass≈1.5)*
- volume *(bool: when True, object acts like volume of 1 material and ray is only considered leaving volume 
        when intersecting a plate / side of sphere with certain ior for a **2nd time**,  
        when False, acts like hollow object)*
- thickness *(float / int: default=1, only effects refraction when volume=False, 
            =thickness of plate / side of sphere (like window pane) instead of being infinitely thin,  
            !IMPORTANT!: when setting the thickness too high, the refracted ray might 'teleport' too far and 
            intersect other geometry)*
- project_color *(%: default=100, affects how much influence the color of the object has on light passing through, 
                when 0 < transparency < 100)*

- roughness *(%: default=0, affects reflection and refraction and allows simulating rough surfaces, 
                = amount of randomness in refracted / reflected ray,
                100% = totally random direction, 0% = perfectly flat surface, 
                when used with refraction, it can be used to simulate translucency)*
- num_ray_splits *(int >= 1: default=1, amount of sample-rays when 'deflecting' ray with randomness 
                 (= when roughness > 0), more samples allows for blurry reflections and refracted images)*

## LIGHTS:
### METHODS:
- on()
- off()
- move(x, y, z)
- rotate(x_angle, y_angle, z_angle, center='self') -> *center='self' doesn't do anything in case of light*
- delete()

### VARIABLES:
- x, y, z *(float / int: location)*
- is_on *(bool: True=on, False=off)*
- visible *(bool: visible for cameras)*
- ray_tracer_visible *(bool: visible for 'rays')*
- box_size *(float / int: size of cube representing light when visible)*
- brightness *float / int: brightness of light)*
- color *(like fill of plate)*

#### --- Raytracing Only ---
- direction *array (size 3, !IMPORTANT!: unit-vector) or None: direction of spot when lighting_angle < 360)*
- lighting_angle *(float / int: size of 'exposed light' in degrees, when < 360, light acts like spotlight)*
- size *(float / int: default=0.5, amount of 'indirect light' reaching places OUTSIDE of lit part when lighting_angle < 360)*

## CAMERAS:
### METHODS:
- reset() -> *resets position to initialized position and rotation to (0, 0, 0)*
- on()
- off()
- move and rotate like described above

### VARIABLES:
- x, y, z *(float / int: location)*
- xangle, yangle, zangle *(int / float)*
- displaying *(False or string: name of window it has to display on)*
- visible *(bool: camera-box visible for other cameras)*
- ray_tracer_visible *(bool: camera-box visible for other cameras during raytracing)*
- box_size *(float / int: size of cube representing camera when visible)*

#### --- Raytracing Only ---
- resolution *(list / tuple / array (size 2): resolution of rendered image (width X height))*
- fov *(float / int: field of view, not in degrees and planar, not spherical)*  
(volumetric lighting:)
- volumetric_checks *(int >= 1: default=1, amount of dust-particles being sampled per distance-unit)*
- max_volumetric_distance *(float / int: default=50, maximum distance for sampling dust-particles)*
- volumetric_particle *(instance of DustParticle class: representation of all dust-particles)*
- volumetric_activated *(bool: default=False, when density gets procedurally changed, should be turned to True manually)*

- hdri *(image-array: replaces default background color with 360°-image,
         load in using <code>rayTracer.load_hdri(r"insert_path")</code>, 
         possible file types are '.hdri', '.jpg' and most other image formats, 
         as long as the image is a 360°-image and maps the complete environment (360° X 180°),
         don't forget to append the file extension to the end of the path)*

## DUST-PARTICLES:
### VARIABLES:
- fill *(array (size 3, RGB) / list / tuple / color name as string: color of dust-particle)*
- density *(%: density / transparency of 'fog' or dust-particles, can be procedurally changed to vary locally: see extra)*
- visible *(bool: if changed procedurally, set volumetric_activated to True)*
- shadows *(%: influence of shadows and highlights of dust-particles)*


## EXTRA: Procedural materials (raytracing only)
The fill and material-properties of plates, spheres and dust-particles can be changed procedurally.
Each of these objects has a built-in method called getColor. This returns its own fill by default, however, 
you can replace it with a function of your own. This function takes in the following arguments:
- instance *(object itself: eg. Plate-instance, Sphere-instance...)*
- x *(float / int: x-location)*
- y *(float / int: y-location)*
- z *(float / int: z-location)*

An example of how to make a checkerboard-pattern, where the dark squares are 85% reflective, would be:  
```Python
from renderer.renderer import *
from math import *

def checkerboard_pattern(instance, x, y, z):  
    x /= 5
    z /= 5
    if (floor(x) + floor(z) % 2) % 2:  
        instance.reflectiveness = 0  # Change material-properties of tiles  
        instance.shadows = 100
        return [255, 255, 255]
    else:  
        instance.reflectiveness = 85
        instance.shadows = 10
        return [50, 50, 50]

ground = Plate([(-15, -4, -10), (15, -4, 20)], fill='grey75', orientation=2)
ground.getColor = checkerboard_pattern
ground.unbounded = True
```