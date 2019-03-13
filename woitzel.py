#-*- utf-8 -*-
import numpy as np
np.random.seed(5)
import bpy

# define Lindenmayer system as a new class
class L_system:

    def __init__(self,axiom,production_rules,w=1.):
        self.axiom = axiom
        self.rules = production_rules
        self.stochastic = w<1.
        self.w = w
        self.current_word = self.axiom
        self.n = 0
        
    def get_iteration(self,n=None):
        word = self.current_word

        if n is None:
            n=1
            word = self.current_word
        else:
            word = self.axiom

        for i in range(n):
            new_word = ""
            for letter in word:
                if letter in self.rules:
                    if (not self.stochastic) or (self.stochastic and np.random.random()<self.w):
                        new_word += self.rules[letter]
                    else:
                        new_word += letter
                else:
                    new_word += letter
            word = str(new_word)

        self.current_word = word
        self.n = i
        return word

# define coordinate system
class coordinate_system:
    
    # This system has an origin (3-dimensional vector),
    # an orientation, or "rotation" (3x3 matrix with determinant 1)
    # and a scale factor 

    def __init__(self,origin=None,rotation=None,scale=None,other=None):

        if other is not None:
            self.rotation = other.rotation.copy()
            self.origin = other.origin.copy()
            self.scale = float(other.scale)
        elif origin is not None and rotation is not None and scale is not None:
            self.rotation = rotation
            self.origin = origin
            self.scale = scale
        else:
            raise ValueError("""
                Provide either an instance of `other` or 
                the three bases `origin`, `rotation` and `scale`
                """)

# define rotation matrices
def RZ(angle):
    return np.array([
                        [  np.cos(angle), np.sin(angle), 0 ],
                        [ -np.sin(angle), np.cos(angle), 0 ],
                        [              0,             0, 1 ],
                        ])
def RX(angle):
    return np.array([
                        [  1,   0, 0], 
                        [  0,  np.cos(angle), np.sin(angle) ],
                        [  0, -np.sin(angle), np.cos(angle)],
                        ])
def RY(angle):
    return np.array([
                        [  np.cos(angle), 0, -np.sin(angle) ],
                        [  0,   1, 0], 
                        [  np.sin(angle), 0, np.cos(angle)],
                    ])

# a function to create a new coordinate system based on an old one
def new_coordinate_system(coo, translate=None,rotate=None,scale=None):
    new_coo = coordinate_system(other=coo)
    if translate is not None:
        new_coo.origin += translate*coo.scale
    if scale is not None:
        new_coo.scale *= scale 
    if rotate is not None:
        new_coo.rotation = rotate.dot(new_coo.rotation)

    return new_coo

# a list of vertices and faces which will be duplicated
sq2 = np.sqrt(2)
# a list of points
base_verts = [ 
                np.array([-1.,-1,-1]),  
                np.array([-1.,-1, 1]),  
                np.array([-1., 1,-1]),  
                np.array([-1., 1, 1]),  
                np.array([ 1.,-1,-1]),  
                np.array([ 1.,-1, 1]),  
                np.array([ 1., 1,-1]),  
                np.array([ 1., 1, 1]),  
             ]
base_faces = [ 
                np.array([0,2,3,1],dtype=int),
                np.array([4,6,7,5],dtype=int),
                np.array([0,4,5,1],dtype=int),
                np.array([1,5,7,3],dtype=int),
                np.array([2,6,7,3],dtype=int),
                np.array([0,4,6,2],dtype=int),
             ]
# The initial stack of coordinate systems
coos = [ coordinate_system(np.array([0.,0.,0.]),np.eye(3),1.0) ]

# These letters represent coordinate transformations
transformation_letters = u'abcdefghijklmnopqrstuvwxyz'

# a dictionary keeping track of the coordinate transformations
vectors = {} 
rotations = {}    
angle = np.pi/7
sq2 = np.sqrt(2)

ez = np.array([0,0,1])
angle = np.pi/4
# Define rotations and translations
rotations['a'] = RZ(-angle).dot(RX(+angle))
rotations['b'] = RZ(-angle).dot(RX(-angle))
rotations['c'] = RZ(+angle).dot(RX(+angle))
rotations['d'] = RZ(+angle).dot(RX(-angle))
rotations['e'] = RZ(np.pi/5)

for k in rotations.keys():
    vectors[k] = rotations[k].dot(ez)

scales = {'a':0.3, 'b':0.3, 'c':0.3, 'd':0.3,'e':0.7}

# The different objects associated with letters A, B, and C.
# Here, these are all the same objects
letter_verts = { 'A': base_verts, 'B': base_verts, 'C': base_verts,  }
letter_faces = { 'A': base_faces, 'B': base_faces, 'C': base_faces,  }

# save all vertices and all faces of the fractal in these arrays
verts = []
edges = []
faces = []

# define a Lindenmayer-System and run it for N iterations
linden = L_system('A',{'A':'[AaA][bA][cA][dA][eA]',})
result = linden.get_iteration(n=2)

# keep track of the total number of vertices
nverts = 0

# iterate through the result-string
for il, l in enumerate(result):
    if l == '[':
        # a '['-symbol represents that a new coordinate system is created
        # and pushed to the stack of coordinate systems
        coos.append(new_coordinate_system(coos[-1]))
    elif l == ']':
        # a ']'-symbol closes the currently active coordinate system and returns
        # to the last one
        coos.pop()
    elif l in transformation_letters:
        # if the symbol is a transformation-symbol        
        # transform the current coordinate system according to the demanded rules
        coos[-1].origin += coos[-1].scale*coos[-1].rotation.dot(vectors[l])
        coos[-1].rotation = rotations[l].dot(coos[-1].rotation)
        coos[-1].scale *= scales[l]
    else:
        # if it's a capital letter, paste the corresponding base-object and
        # transform it according to the current coordinate system
        these_faces = letter_faces[l]
        these_verts = letter_verts[l]

        # transform all faces to point to the new vertices
        for f in these_faces:
            _f = f.copy()
            faces.append(tuple((_f+nverts).tolist()))

        nverts += len(these_verts)

        # transform all vertices according to the current coordinate system
        # and push to the list
        for r in these_verts:
            newr = r.copy()
            newr *= coos[-1].scale
            newr = coos[-1].rotation.dot(newr)
            newr += coos[-1].origin

            verts.append(tuple(newr.tolist()))


 
#create mesh and object
mymesh = bpy.data.meshes.new("fractal")
myobject = bpy.data.objects.new("fractal",mymesh)
 
#set mesh location
myobject.location = bpy.context.scene.cursor_location
bpy.context.scene.objects.link(myobject)
 
#create mesh from python data
mymesh.from_pydata(verts,edges,faces)
mymesh.update(calc_edges=True)
 
#set the object to edit mode
bpy.context.scene.objects.active = myobject
bpy.ops.object.mode_set(mode='EDIT')
 
# remove duplicate vertices
bpy.ops.mesh.remove_doubles() 
 
# recalculate normals
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
 
# subdivide modifier
myobject.modifiers.new("subd", type='SUBSURF')
myobject.modifiers['subd'].levels = 3
 
# show mesh as smooth
mypolys = mymesh.polygons
for p in mypolys:
    p.use_smooth = True

