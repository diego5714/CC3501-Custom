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


#Resolucion inicial
ANCHO = 1280
ALTO = 800

class Controller(pyglet.window.Window):
    def __init__(self, ancho, alto, titulo):
        super().__init__(ancho, alto, resizable = True, caption = titulo)
        self.set_minimum_size(200,200)
        self.ancho = ANCHO
        self.alto = ALTO

    def update(self, dt):
        pass

class Camara():
    def __init__(self, tipo = 'perspectiva'):
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
            matrix_perspectiva = tr.perspective(95, width / height, 0.01, 100)
        elif self.tipo == "ortografica":
            depth = self.posicion - self.mirando_a
            depth = np.linalg.norm(depth)
            matrix_perspectiva = tr.ortho(-(width/height) * depth, (width/height) * depth, -1 * depth, 1 * depth, 0.01, 100)
        return np.reshape(matrix_perspectiva, (16, 1), order="F")



ventana = Controller(ancho = ANCHO, alto = ALTO, titulo = "Tarea #1")

with open(Path(os.path.dirname(__file__)) / "shaders/transform.vert") as f:
        vertex_source_code = f.read()

with open(Path(os.path.dirname(__file__)) / "shaders/color.frag") as f:
        fragment_source_code = f.read()

VertexShader = pyglet.graphics.shader.Shader(vertex_source_code,'vertex')
FragmentShader = pyglet.graphics.shader.Shader(fragment_source_code,'fragment')

pipeline1 = pyglet.graphics.shader.ShaderProgram(VertexShader, FragmentShader)

camara = Camara('perspectiva')

@ventana.event
def on_draw(): 
    GL.glClearColor(0.153, 0.157, 0.133, 1.0) #Gris
    ventana.clear()
    pipeline1.use()

    pipeline1["u_view"] = camara.obtener_vista()
    pipeline1["u_view"] = camara.obtener_proyeccion(ventana.ancho,ventana.alto)

pyglet.clock.schedule_interval(ventana.update, 1/60)
pyglet.app.run()    