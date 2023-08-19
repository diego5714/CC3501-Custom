import pyglet
from OpenGL import GL  #Wrapper de python para OpenGL
import numpy as np
from pathlib import Path
import os

WIDTH = 640
HEIGHT = 640

class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.set_minimum_size(240, 240) # Evita error cuando se redimensiona a 0
        self.set_caption(title)

    def update(self, dt):
        
        pass

if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Auxiliar 1", width=WIDTH, height=HEIGHT, resizable=True)
    
    # Cargar archivos y asignarlos a variables
    with open(Path(os.path.dirname(__file__)) / "shaders/basic.vert") as f: #Cargamos nuestro vertex shader a una variable.
        vertex_source_code = f.read()                                       #Nos permite manipular vértices y sus propiedades (Aún sin dibujar).
                                                                            #Usualmente aquí se manipulan sus posiciones nada más,
                                                                            #o propiedades que no tengan que ver con la apariencia final.


    with open(Path(os.path.dirname(__file__)) / "shaders/basic.frag") as f:  #Lo mismo con el fragment shader. Nos permite modificar propiedades
        fragment_source_code = f.read()                                      #(apariencia) de los píxeles ya rasterizados asociados a cada vértice                
                                                                             #y de los píxeles que se crean entre ellos mediante interpolación
                                                                             #Ej: Color, intensidad
    
    #Tamién es posible pegar el codigo del shader como un string directamente (con 3 comillas).
    
    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)  #Creamos nuestro pipeline con los shaders especificados.
                                                                               #Es posible crear todos los que queramos.
    positions = np.array([
        -0.5, -0.5,
         0.5, -0.5,           #Definimos nuestros vértices para una figura (con sus colores e intensidades)
         0.0,  0.5            #Los vectores deben ser del mismo largo (En Nº de vértices, no de elementos necesariamente)
    ], dtype=np.float32)

    colors = np.array([
        1, 0, 0,
        0, 1, 0,            
        0, 0, 1
    ], dtype=np.float32)  #Le indica al array de numpy que usamos floats

    intensities = np.array([
        1, 0.5, 1
    ], dtype=np.float32)

    gpu_triangle = pipeline.vertex_list(3, GL.GL_TRIANGLES)  #Tomamos nuestros vertices almacenados en CPU y los transformamos a 
    gpu_triangle.position = positions                        #formato que la GPU entienda (Vertex_list (no indexada): Es un método del pipeline)
    gpu_triangle.color = colors                              
    gpu_triangle.intensity = intensities                     #Especificamos que tipo de primitiva definen nuestros vértices.
                                                             #y el número de ellos. (Definimos su forma)
    quad_positions = np.array([
        -1, -1,
        1, -1,
        1,  1,                         #Repetimos proceso pero para un cuadrado (quad)
        -1,  1
    ], dtype=np.float32)

    quad_colors = np.array([
        1, 0, 0,
        0.0, 1.0, 0.0, # verde
        0.0, 0.0, 1.0, # azul
        1.0, 1.0, 1.0  # blanco
    ], dtype=np.float32)

    quad_intensities = np.array([1, 1, 1, 1], dtype=np.float32)

    quad_indices = np.array([  #Definimos una lista de vértices indexada que le indica al pipeline en que orden dibujar los 
        0, 1, 2,               #vértices, esto nos permite evitar dibujar algunos vértices múltiples veces y ahorrar recursos.
        2, 3, 0
    ], dtype=np.uint32)

    gpu_quad = pipeline.vertex_list_indexed(4, GL.GL_TRIANGLES, quad_indices)  #Lo transformamos a formato GPU (pero con lista indexada)
    gpu_quad.position = quad_positions
    gpu_quad.color = quad_colors
    gpu_quad.intensity = quad_intensities

    # draw loop
    @controller.event
    def on_draw():
        GL.glClearColor(0, 0, 0, 1.0)  #Setea la ventana en negro
        controller.clear()  #Limpia lo que pyglet hubiese dibujado antes
        
        pipeline.use()  #Establecemos que pipeline se va a usar a continuación (Útil si tenemos muchos pipelines con shaders distintos)
        
        gpu_quad.draw(GL.GL_TRIANGLES)      #[vertex_list].draw() Dibujamos la lista de vértices mediante el pipeline seleccionado
        gpu_triangle.draw(GL.GL_TRIANGLES)  #Le podemos especificar al pipeline como queremos que se dibuje finalmente la figura 
                                            #(mediante Lineas, triangulos, etc...). Esto es distinto a la forma que definimos antes.
   
    pyglet.clock.schedule_interval(controller.update, 1/60)
    pyglet.app.run()