import pyglet
import numpy as np
from OpenGL import GL
import os 
from pathlib import Path

#Resolucion base:
ANCHO = 700
ALTO = 700

#Creamos clase del controlador
class Controller(pyglet.window.Window):
    def __init__(self, ancho, alto, titulo):
        super().__init__(ancho, alto, resizable = True, caption = titulo)
        self.set_minimum_size(200,200)

    def update(self, dt):
        pass

#Creamos un controlador (ventana)
ventana = Controller(ancho = ANCHO, alto = ALTO, titulo = "Tarea #0")

#Procedemos a cargar los shaders y crear el pipeline
with open(Path(os.path.dirname(__file__)) / "shaders/basic.vert") as f:
    VertexFuente = f.read()

with open(Path(os.path.dirname(__file__)) / "shaders/basic.frag") as f:
    FragmentFuente = f.read()

#Creamos el pipeline:
VertexShader = pyglet.graphics.shader.Shader(VertexFuente,'vertex')
FragmentShader = pyglet.graphics.shader.Shader(FragmentFuente, 'fragment')

pipeline1 = pyglet.graphics.shader.ShaderProgram(VertexShader, FragmentShader)

#Ahora definimos nuestros vertexes:

pac_pos = np.array([
    0.0,    0.0,        #Pto 0
    0.707, -0.707,      #Pto 1
    0.0,   -1.0,        #Pto 2
   -0.707, -0.707,      #Pto 3
   -1.0,    0.0,        #Pto 4
   -0.707,  0.707,      #Pto 5
    0.0,    1.0,        #Pto 6
    0.707,  0.707       #Pto 7
    ], dtype=np.float32)

pac_color = np.array([
    0.016, 0.529, 0.537, #0
    0.314, 0.239, 0.180, #1
    0.831, 0.302, 0.153, #2
    0.682, 0.831, 0.153, #3
    0.886, 0.655, 0.180, #4
    0.655, 0.180, 0.886, #5
    0.180, 0.412, 0.886, #6
    0.937, 0.922, 0.784  #7

], dtype=np.float32)

pac_int = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], dtype=np.float32)

pac_index = np.array([
        0, 1, 2,
        2, 0, 3, 
        3, 0, 4,
        4, 0, 5,
        5, 0, 6,
        6, 0, 7
], dtype=np.uint32)

#Procedemos a transformar nuestros vertexes a una vertex list indexada

pacman = pipeline1.vertex_list_indexed(8, GL.GL_TRIANGLES, pac_index)

pacman.position = pac_pos * 0.9
pacman.color = pac_color
pacman.intensity = pac_int

@ventana.event
def on_draw():  #Procedemos a dibujar mediante triangulos en el pipeline
    GL.glClearColor(0, 0, 0, 1.0)
    ventana.clear()
    pipeline1.use()
    pacman.draw(GL.GL_TRIANGLES)

pyglet.clock.schedule_interval(ventana.update, 1/60)
pyglet.app.run()    