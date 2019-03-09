#-*- utf-8 -*-
#import bpy
import numpy as np
np.random.seed(3)

class L_system():

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

class coordinate_system:

    def __init__(self,origin=None,rotation=None,scale=None,other=None):

        if other is not None:
            self.rotation = other.rotation.copy()
            self.origin = other.origin.copy()
            self.scale = other.scale
        elif origin is not None and rotation is not None and scale is not None:
            self.rotation = rotation
            self.origin = origin
            self.scale = scale
        else:
            raise ValueError("""
                Provide either an instance of `other` or 
                the three bases `origin`, `rotation` and `scale`
                """)

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

def new_coordinate_system(coo, translate=None,rotate=None,scale=None):
    new_coo = coordinate_system(other=coo)
    if translate is not None:
        new_coo.origin += translate*coo.scale
    if scale is not None:
        new_coo.scale *= scale 
    if rotate is not None:
        new_coo.rotation = rotate.dot(new_coo.rotation)

    return new_coo

# a list of points
base_verts = [ 
                np.array([-1.,-1,-1]),  
                np.array([0.,1,1]),  
                np.array([1.,1,1]),  
             ]
base_faces = [ 
                np.array([0,1,2],dtype=int)
             ]


coos = [ coordinate_system(np.array([0.,0.,0.]),np.eye(3),1.0) ]


letters = u'abcdefghijklmnopqrstuvwxyz'
#letters = u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
greek = u'αβγδϵζηθικλμνξoπρστυϕχω'
numbers = u'1234567890'


all_points = []
all_faces = []

vectors = {} 

N_vectors = 2
for v in range(N_vectors):
    r = np.random.randn(3)
    r /= np.linalg.norm(r)

    vectors[letters[v]] = r

rotations = {}
rot_intensity = 0.5

for v in range(N_vectors):

    tx = 2*rot_intensity * np.random.random()*np.pi - rot_intensity * np.pi
    ty = 2*rot_intensity * np.random.random()*np.pi - rot_intensity * np.pi
    tz = 2*rot_intensity * np.random.random()*np.pi - rot_intensity * np.pi

    rotations[letters[v]] = RZ(tz).dot(RY(ty).dot(RX(tx)))

scales = {'a':0.6, 'b':0.4}

letter_verts = { 'A': base_verts, 'B': base_verts }
letter_faces = { 'A': base_faces, 'B': base_faces }

verts = []
faces = []

linden = L_system('A',{'A':'[AaA][bB]','B':'[BaA]'})

result = linden.get_iteration(n=3)

nverts = 0
for il, l in enumerate(result):
    if l == '[':
        coos.append(new_coordinate_system(coos[-1]))
    elif l == ']':
        coos.pop()
    elif l in letters:
        coos[-1].rotation = rotations[l].dot(coos[-1].rotation)
        coos[-1].origin += coos[-1].scale*vectors[l]
        coos[-1].scale *= scales[l]
    else:
        these_faces = letter_faces[l].copy()
        these_verts = letter_verts[l].copy()

        for f in these_faces:
            faces.append(tuple((f+nverts).tolist()))

        nverts += len(these_verts)

        for r in these_verts:
            r *= coos[-1].scale
            r = coos[-1].rotation.dot(r)
            r += coos[-1].origin

            verts.append(tuple(r.tolist()))


print(verts, faces)
