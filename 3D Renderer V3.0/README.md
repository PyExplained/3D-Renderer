# README
<sub> Written using Markdown-syntax </sub>

## LIBRARIES:
- Required: numpy, PIL
- Recommended, but optional: cv2, trimesh

When looking at examples, you will see that I often refer to 'the basic renderer' and 'the raytracer', 
here is the distinction made clear:
- **The basic renderer** is a kind of preview, while also being a renderer and semi-game-engine on its own and was
    originally written without any raytracing functionality. It's far from perfect and one of the most obvious 
    visual bugs is when things in the background and foreground aren't layered correctly. However, this 'mode' is 
    meant to be used as a way to sketch your scene while previewing it in real-time.
- **The raytracer** was originally meant as an 'addition', while now actually being a major feature. 
    It isn't realtime by any means, so you have to use it like rendering a picture in 3D-software.  
    This is a little preview of what it can do: <https://www.youtube.com/watch?v=50bsIIsnKrI>

In the examples scene, you can find examples of what you can do using the basic renderer and 
you can find raytracing examples in the other scenes. To start raytracing, you can just press 'b'.

You can change most things directly from the file your running. Eg. you're testing out example_scene.py, but you don't
like the controls. In this case, you can just change the following line(s) from 
<code> controller.bind('z', 'forward', 0.5)</code>
to 
<code> controller.bind('insert_key', 'forward', 0.5)</code>

In renderer-info.md, you can find a semi-detailed documentation (written in Markdown) with a list of 
classes with their variables and methods. A lot of features of the raytracer are also explained there.

!: Please report any bugs when encountering them on GitHub (aside from wrong layering when using the basic renderer).

[click here]: https://www.youtube.com/watch?v=50bsIIsnKrI