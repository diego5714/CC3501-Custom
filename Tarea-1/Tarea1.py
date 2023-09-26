#Implementacion del la tarea #1 

import pyglet 
from OpenGL import GL
import numpy as np
import trimesh as tm 
import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
import grafica.transformations as tr
import auxiliares.utils.shapes as shapes


#Resolucion inicial
ANCHO = 1280
ALTO = 800

class Controller(pyglet.window.Window):
    def __init__(self, ancho, alto, titulo):
        super().__init__(ancho, alto, resizable = True, caption = titulo)
        self.set_minimum_size(200,200)
        self.ancho = ANCHO
        self.alto = ALTO
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_handler)
        self.init()

    def init(self):
        GL.glClearColor(0.118, 0.122, 0.11, 1.0) #Gris
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
    
    def is_key_pressed(self, key):
        return self.key_handler[key]


class Camara(): #Definimos clase de la camara
    def __init__(self, tipo = "perspectiva"):
        self.posicion = np.array([1, 0, 0], dtype=np.float32)
        self.mirando_a = np.array([0, 0, 0], dtype=np.float32)
        self.tipo = tipo
    
    def update(self):
        pass

    def obtener_vista(self):
        matrix_vista = tr.lookAt(self.posicion, self.mirando_a, np.array([0, 1, 0], dtype=np.float32))
        return np.reshape(matrix_vista, (16, 1), order="F")

    def obtener_proyeccion(self,width,height):
        if self.tipo == "perspectiva":
            matrix_perspectiva = tr.perspective(90, width / height, 0.01, 100)
        
        elif self.tipo == "ortografica":
            depth = self.posicion - self.mirando_a
            depth = np.linalg.norm(depth)
            matrix_perspectiva = tr.ortho(-(width/height) * depth, (width/height) * depth, -1 * depth, 1 * depth, 0.01, 100)
        
        return np.reshape(matrix_perspectiva, (16, 1), order="F")

class CamaraOrbital(Camara):
    def __init__(self, distancia, tipo = "perspectiva"):
        super().__init__(tipo)
        self.distancia = distancia
        self.phi = 0
        self.theta = np.pi / 2
        self.update()

    def update(self):
        if self.theta > np.pi:
            self.theta = np.pi
        elif self.theta < 0:
            self.theta = 0.0001

        self.posicion[0] = self.distancia * np.sin(self.theta) * np.sin(self.phi)
        self.posicion[1] = self.distancia * np.cos(self.theta)
        self.posicion[2] = self.distancia * np.sin(self.theta) * np.cos(self.phi)

class Modelo():
    def __init__(self, data_posicion, data_color, data_indices = None):
        self.data_posicion = data_posicion
        self.data_color = data_color
        self.data_indices = data_indices

        if data_indices is not None:
            self.data_indices = np.array(data_indices, dtype=np.uint32)

        self.data_gpu = None

        #Inicializamos parametros por defecto del modelo 3D
        self.posicion = np.array([0,0,0], dtype=np.float32) #Posicion del centro
        self.rotacion = np.array([0,0,0], dtype=np.float32) #Rotacion inicial
        self.escala = np.array([1.5,1.5,1.5], dtype=np.float32) #Escala inicial

    def inicializar(self, pipeline):
        if self.data_indices is not None: #Si existen indices, creamos una vertex list indexada, si no no.
            self.data_gpu = pipeline.vertex_list_indexed(len(self.data_posicion) // 3, GL.GL_TRIANGLES, self.data_indices)

        else:
            self.data_gpu = pipeline.vertex_list(len(self.data_posicion) // 3, GL.GL_TRIANGLES)

        #Finalmente, le pasamos la informacion al shader:
        self.data_gpu.position = self.data_posicion
        self.data_gpu.color = self.data_color

    def dibujar(self, mode = GL.GL_TRIANGLES):
        self.data_gpu.draw(mode)

    def transformaciones(self):
        matrix_traslacion = tr.translate(self.posicion[0], self.posicion[1], self.posicion[2])
        matrix_rotacion = tr.rotationX(self.rotacion[0]) @ tr.rotationY(self.rotacion[1]) @ tr.rotationZ(self.rotacion[2])
        matrix_escala = tr.scale(self.escala[0], self.escala[1], self.escala[2])
        transformacion = matrix_traslacion @ matrix_rotacion @ matrix_escala
        return np.reshape(transformacion, (16, 1), order="F")

class Malla(Modelo):
    def __init__(self, path, color_base = None):
        data_malla = tm.load(path)
        malla_unitaria = tr.uniformScale(2.0 / data_malla.scale)
        malla_centrada = tr.translate(*-data_malla.centroid)
        data_malla.apply_transform(malla_unitaria @ malla_centrada)

        data_vertex = tm.rendering.mesh_to_vertexlist(data_malla)
        indices = data_vertex[3]
        posiciones = data_vertex[4][1]

        count = len(posiciones) // 3 #Numero de vertices
        colores = np.ones((count * 3, 1), dtype = np.float32) #inicializamos vector de colores

        if color_base is None:
            colores = data_vertex[5][1]
        else:
            for i in range(count):
                colores[i * 3] = color_base[0]
                colores[i * 3 + 1] = color_base[1]
                colores[i * 3 + 2] = color_base[2]

        super().__init__(posiciones, colores, indices)

ventana = Controller(ancho = ANCHO, alto = ALTO, titulo = "Tarea #1")

with open(Path(os.path.dirname(__file__)) / "shaders/transform.vert") as f:
        vertex_source_code = f.read()

with open(Path(os.path.dirname(__file__)) / "shaders/color.frag") as f:
        fragment_source_code = f.read()

VertexShader = pyglet.graphics.shader.Shader(vertex_source_code,'vertex')
FragmentShader = pyglet.graphics.shader.Shader(fragment_source_code,'fragment')

pipeline1 = pyglet.graphics.shader.ShaderProgram(VertexShader, FragmentShader)

camara = CamaraOrbital(2,"perspectiva")

figura = Malla("Tarea-1/Rueda.stl", [0.77, 0.15, 0.23])
figura.inicializar(pipeline1)

axes = Modelo(shapes.Axes["position"], shapes.Axes["color"])
axes.inicializar(pipeline1)

print("Controles Cámara:\n\tWASD: Rotar\n\t Q/E: Acercar/Alejar\n\t1/2: Cambiar tipo")
def update(dt):
    if ventana.is_key_pressed(pyglet.window.key.A):
        camara.phi -= dt
    if ventana.is_key_pressed(pyglet.window.key.D):
        camara.phi += dt
    if ventana.is_key_pressed(pyglet.window.key.W):
        camara.theta -= dt
    if ventana.is_key_pressed(pyglet.window.key.S):
        camara.theta += dt
    if ventana.is_key_pressed(pyglet.window.key.Q):
        camara.distancia += dt
    if ventana.is_key_pressed(pyglet.window.key.E):
        camara.distancia -= dt
    if ventana.is_key_pressed(pyglet.window.key._1):
        camara.tipo = "perspectiva"
    if ventana.is_key_pressed(pyglet.window.key._2):
        camara.tipo = "ortografica"

    camara.update()

@ventana.event
def on_draw(): 
    ventana.clear()
    pipeline1.use()

    pipeline1["u_view"] = camara.obtener_vista()
    pipeline1["u_projection"] = camara.obtener_proyeccion(ventana.ancho,ventana.alto)
    
    pipeline1["u_model"] = axes.transformaciones()
    axes.dibujar(GL.GL_LINES)
    
    pipeline1["u_model"] = figura.transformaciones()
    figura.dibujar()

pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()    