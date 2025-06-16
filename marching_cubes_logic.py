import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import glfw
from OpenGL.GL import *

def marchingCubes(obj):
    '''
    Input: Flattened sdf of object
    Output: triangles
    '''
    dtype = 'float32'
    sdf = np.fromfile(obj, dtype=dtype)

    triangle_list = []

    N = round(sdf.size ** (1/3))
    for z in range(N - 1):       # z-axis
        for y in range(N - 1):   # y-axis
            for x in range(N - 1):  # x-axis
                # Getting voxel corners (ampped from 3D space to 1D space)
                # v0 = sdf[x     + y*N     + z*N*N]
                # v1 = sdf[(x+1) + y*N     + z*N*N]
                # v2 = sdf[(x+1) + (y+1)*N + z*N*N]
                # v3 = sdf[x     + (y+1)*N + z*N*N]
                # v4 = sdf[x     + y*N     + (z+1)*N*N]
                # v5 = sdf[(x+1) + y*N     + (z+1)*N*N]
                # v6 = sdf[(x+1) + (y+1)*N + (z+1)*N*N]
                # v7 = sdf[x     + (y+1)*N + (z+1)*N*N]
                v0 = sdf[x     + y*N     + z*N*N]
                v1 = sdf[(x+1) + y*N     + z*N*N]
                v2 = sdf[x     + (y+1)*N + z*N*N]
                v3 = sdf[(x+1) + (y+1)*N + z*N*N]
                v4 = sdf[x     + y*N     + (z+1)*N*N]
                v5 = sdf[(x+1) + y*N     + (z+1)*N*N]
                v6 = sdf[x     + (y+1)*N + (z+1)*N*N]
                v7 = sdf[(x+1) + (y+1)*N + (z+1)*N*N]
                
                corners = [v0, v1, v2, v3, v4, v5, v6, v7]

                cube_index = 0 # binary = 0000 0000
                for i, val in enumerate(corners):
                    if val > 0:
                        cube_index |= (1 << i)  # If outside object, set that bit in the binary high
                                                # |= is binary OR... ORs current binary with (1 << i)
                triangles_edges = tri_table[cube_index]
                triangles_edges = triangles_edges[:(np.argmax(triangles_edges < 0))] # Efficinetly find first index of value -1

                for t in range(0, len(triangles_edges), 3):
                    triangle = []
                    for e in triangles_edges[t:t+3]:
                        a, b = edge_vertex_indices[e]
                        
                        # Get corner positions in world space
                        p1 = np.array(corner_offsets[a]) + np.array([x, y, z])
                        p2 = np.array(corner_offsets[b]) + np.array([x, y, z])
                        
                        # Midpoint of the edge
                        midpoint = (p1 + p2) / 2
                        triangle.append(midpoint)

                        # Draw a single triangle
                    triangle_list += [triangle]  # triangle is a list of 3 (x,y,z) points

                        

    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # # plt.ion()  # Turn on interactive mode
    # # plt.show()
    # poly = Poly3DCollection(triangle_list, facecolors='black', edgecolors='red', alpha=0.5)
    # ax.add_collection3d(poly)
    # ax.set_xlim(0, N)
    # ax.set_ylim(0, N)
    # ax.set_zlim(0, N)
    # plt.tight_layout()
    # plt.show()
                

    return triangle_list

tri_table = np.load('lookup_tables/triangle_table.npy')
edge_vertex_indices = np.load('lookup_tables/edge_vertex_indices.npy')
edge_masks = np.load('lookup_tables/edge_masks.npy')

corner_offsets = [
    (0, 0, 0),  # 0
    (1, 0, 0),  # 1
    (0, 1, 0),  # 2
    (1, 1, 0),  # 3
    (0, 0, 1),  # 4
    (1, 0, 1),  # 5
    (0, 1, 1),  # 6
    (1, 1, 1),  # 7
]


def renderObject(triangles):

     # Initialize GLFW
    if not glfw.init():
        print("Failed to initialize GLFW")
        return

    window = glfw.create_window(800, 600, "Marching Cubes Triangles", None, None)
    if not window:
        print("Failed to create GLFW window")
        glfw.terminate()
        return

    glfw.make_context_current(window)

    # Enable depth testing
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    triangles = np.array(triangles, dtype=np.float32)

    min_corner = triangles.min(axis=(0,1))
    max_corner = triangles.max(axis=(0,1))
    center = (min_corner + max_corner) / 2
    scale = (max_corner - min_corner).max() / 2

    triangles = (triangles - center) / scale  # now fits in [-1,1]^3
    # vertices = triangles.flatten()


    # Main render loop
    while not glfw.window_should_close(window):
        glfw.poll_events()

        # Clear screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Apply basic transform
        # glTranslatef(0.0, 0.0, -2.5)  # move back just enough to see [-1,1]^3 space
        # glRotatef(glfw.get_time() * 20, 0, 1, 0)

        angle = glfw.get_time() * 50
        glRotatef(angle, 0, 1, 0)

        # Draw triangles
        glBegin(GL_TRIANGLES)
        glColor3f(1.0, 0.0, 0.0)

        for tri in triangles:
            for vertex in tri:
                glVertex3f(*vertex)
        glEnd()

        glColor3f(0.0, 0.0, 0.0)  # black edges
        glBegin(GL_LINES)
        for tri in triangles:
            # triangle is 3 vertices, each with x,y,z
            for i in range(3):
                v1 = tri[i]
                v2 = tri[(i+1) % 3]
                glVertex3f(v1[0], v1[1], v1[2])
                glVertex3f(v2[0], v2[1], v2[2])
        glEnd()


        glfw.swap_buffers(window)

    glfw.terminate()


    return 0

# with open('inputs/torus_sdf.bin', 'rb') as file:
with open('inputs/sphere_sdf.bin', 'rb') as file:
# with open('inputs/sphere_sdf_float32.bin', 'rb') as file:
    renderObject(marchingCubes(file))
