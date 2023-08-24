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
with open(Path(os.path.dirname(__file__)) / "auxiliares/shaders/basic.vert") as f:
    VertexFuente = f.read()

with open(Path(os.path.dirname(__file__)) / "auxiliares/shaders/basic.frag") as f:
    FragmentFuente = f.read()

#Creamos el pipeline:
VertexShader = pyglet.graphics.shader.Shader(VertexFuente,'vertex')
FragmentShader = pyglet.graphics.shader.Shader(FragmentFuente, 'fragment')

pipeline1 = pyglet.graphics.shader.ShaderProgram(VertexShader, FragmentShader)

#Ahora definimos nuestros vertexes:
A = [-0.75, -0.75]
B = [0.0, 0.8]
C = [0.25, -0.25]
D = [0.7, -0.33]

Rojo = [1.0, 0.0, 0.0]
Azul = [0.0, 0.0, 1.0]
Amarillo = [1.0, 0.788, 0.0]

T1 = np.array(A + B + C, dtype = np.float32)

C1 = np.array(Rojo + Rojo + Rojo, dtype = np.float32)

T2 = np.array(B + C + D, dtype = np.float32)

C2 = np.array(Azul + Azul + Azul, dtype = np.float32)

T3 = np.array(A + C + D, dtype = np.float32)

C3 = np.array(Amarillo + Amarillo + Amarillo, dtype = np.float32)


#Procedemos a transformar nuestros vertexes a una vertex list indexada
triangulo1 = pipeline1.vertex_list(3, GL.GL_TRIANGLES)

triangulo1.position = T1
triangulo1.color = C1
triangulo1.intensity = np.array([1.0, 1.0, 1.0], dtype = np.float32)

triangulo2 = pipeline1.vertex_list(3, GL.GL_TRIANGLES)

triangulo2.position = T2
triangulo2.color = C2
triangulo2.intensity = np.array([1.0, 1.0, 1.0], dtype = np.float32)

triangulo3 = pipeline1.vertex_list(3, GL.GL_TRIANGLES)

triangulo3.position = T3
triangulo3.color = C3
triangulo3.intensity = np.array([1.0, 1.0, 1.0], dtype = np.float32)

@ventana.event
def on_draw():  #Procedemos a dibujar mediante triangulos en el pipeline
    GL.glClearColor(0.529, 0.522, 0.49, 1.0)
    ventana.clear()
    pipeline1.use()
    triangulo1.draw(GL.GL_TRIANGLES)
    triangulo2.draw(GL.GL_TRIANGLES)
    triangulo3.draw(GL.GL_TRIANGLES)

pyglet.clock.schedule_interval(ventana.update, 1/60)
pyglet.app.run()    