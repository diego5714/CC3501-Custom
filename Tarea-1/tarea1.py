#Implementacion del la tarea #1 

import pyglet 
from OpenGL import GL
import numpy as np
import trimesh as tm 
import networkx as nx
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
        #GL.glEnable(GL.GL_CULL_FACE)
        #GL.glCullFace(GL.GL_BACK)
        #GL.glFrontFace(GL.GL_CCW)
        #GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
    
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
        self.theta = np.pi / 2.7
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
        self.pipeline = pipeline #Se me habia olvidado esta linea y me costo 30k horas de debugging, simplemente pasaba pipeline
                                 #sin asignarlo como atributo :(       
        
        if self.data_indices is not None: #Si existen indices, creamos una vertex list indexada, si no no.
            self.data_gpu = self.pipeline.vertex_list_indexed(len(self.data_posicion) // 3, GL.GL_TRIANGLES, self.data_indices)

        else:
            self.data_gpu = self.pipeline.vertex_list(len(self.data_posicion) // 3, GL.GL_TRIANGLES)

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
        data_malla = tm.load(path, process = False, force = 'mesh')
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

class SceneGraph():
    def __init__(self, camera=None):
        self.graph = nx.DiGraph(root="root")
        self.add_node("root")
        self.camera = camera

    def add_node(self,
                 name,
                 attach_to=None,
                 mesh=None,
                 color=[1, 1, 1],
                 transform=tr.identity(),
                 position=[0, 0, 0],
                 rotation=[0, 0, 0],
                 scale=[1, 1, 1],
                 mode=GL.GL_TRIANGLES):
        self.graph.add_node(
            name, 
            mesh=mesh, 
            color=color,
            transform=transform,
            position=np.array(position, dtype=np.float32),
            rotation=np.array(rotation, dtype=np.float32),
            scale=np.array(scale, dtype=np.float32),
            mode=mode)
        if attach_to is None:
            attach_to = "root"
        
        self.graph.add_edge(attach_to, name)

    def __getitem__(self, name):
        if name not in self.graph.nodes:
            raise KeyError(f"Node {name} not in graph")

        return self.graph.nodes[name]
    
    def __setitem__(self, name, value):
        if name not in self.graph.nodes:
            raise KeyError(f"Node {name} not in graph")

        self.graph.nodes[name] = value
    
    def get_transform(self, node):
        node = self.graph.nodes[node]
        transform = node["transform"]
        translation_matrix = tr.translate(node["position"][0], node["position"][1], node["position"][2])
        rotation_matrix = tr.rotationX(node["rotation"][0]) @ tr.rotationY(node["rotation"][1]) @ tr.rotationZ(node["rotation"][2])
        scale_matrix = tr.scale(node["scale"][0], node["scale"][1], node["scale"][2])
        return transform @ translation_matrix @ rotation_matrix @ scale_matrix

    def dibujar(self):
        root_key = self.graph.graph["root"]
        edges = list(nx.edge_dfs(self.graph, source=root_key))
        transformations = {root_key: self.get_transform(root_key)}

        for src, dst in edges:
            current_node = self.graph.nodes[dst]

            if not dst in transformations:
                transformations[dst] = transformations[src] @ self.get_transform(dst)

            if current_node["mesh"] is not None:
                current_pipeline = current_node["mesh"].pipeline
                current_pipeline.use()

                if self.camera is not None:
                    if "u_view" in current_pipeline.uniforms:
                        current_pipeline["u_view"] = self.camera.obtener_vista()

                    if "u_projection" in current_pipeline.uniforms:
                        current_pipeline["u_projection"] = self.camera.obtener_proyeccion(ventana.ancho, ventana.alto)

                current_pipeline["u_model"] = np.reshape(transformations[dst], (16, 1), order="F")

                if "u_color" in current_pipeline.uniforms:
                    current_pipeline["u_color"] = np.array(current_node["color"], dtype=np.float32)
                current_node["mesh"].dibujar(current_node["mode"])

ventana = Controller(ancho = ANCHO, alto = ALTO, titulo = "Tarea #1")

with open(Path(os.path.dirname(__file__)) / "shaders/transform.vert") as f:
        vertex_source_code = f.read()

with open(Path(os.path.dirname(__file__)) / "shaders/color.frag") as f:
        fragment_source_code = f.read()

VertexShader = pyglet.graphics.shader.Shader(vertex_source_code,'vertex')
FragmentShader = pyglet.graphics.shader.Shader(fragment_source_code,'fragment')

pipeline1 = pyglet.graphics.shader.ShaderProgram(VertexShader, FragmentShader)

camara = CamaraOrbital(1.2,"perspectiva")

garaje = SceneGraph(camara)

cubo = Modelo(shapes.Cube["position"], shapes.Cube["color"], shapes.Cube["indices"])
cubo.inicializar(pipeline1)

cilindro = Malla("Tarea-1/models/cylinder.stl")
cilindro.inicializar(pipeline1)

chasis = Malla("Tarea-1/models/Chevrolet_Camaro_SS_SIN_VENTANAS.stl")
chasis.inicializar(pipeline1)

ventanas = Malla("Tarea-1/models/Ventanas.stl", color_base = np.array([0, 0.867, 1]))
ventanas.inicializar(pipeline1)

rueda = Malla("Tarea-1/models/Rueda.stl")
rueda.inicializar(pipeline1)

garaje.add_node("objetos")
garaje.add_node("garaje", mesh = cubo, transform = tr.translate(0, 2, 0) @ tr.uniformScale(4))
garaje.add_node("plataforma", attach_to = "objetos")

garaje.add_node("cilindro", attach_to = "plataforma", mesh = cilindro, transform = tr.rotationX(-np.pi / 2) @ tr.scale(1.9, 1.9, 0.063))
garaje.add_node("vehiculo", attach_to = "plataforma", transform = tr.translate(0, 0.29, 0) @ tr.rotationX(-np.pi / 2))

garaje.add_node("chasis", attach_to = "vehiculo", mesh = chasis)
garaje.add_node("ventanas", attach_to = "vehiculo", mesh = ventanas, transform = tr.translate(0, 0.113, 0.145) @ tr.scale(0.519, 0.519, 0.519))
garaje.add_node("ruedas", attach_to = "vehiculo", transform = tr.translate(0, 0, -0.13) @ tr.uniformScale(0.19))

garaje.add_node("R_Derechas", attach_to = "ruedas", transform = tr.translate(-1.5, 0, 0) @ tr.rotationZ(np.pi))
garaje.add_node("R_Izquierdas", attach_to = "ruedas", transform = tr.translate(1.5, 0, 0))

garaje.add_node("ruedaTD", attach_to = "R_Derechas", mesh = rueda, transform = tr.translate(0, -2.82, 0))
garaje.add_node("ruedaTI", attach_to = "R_Izquierdas", mesh = rueda, transform = tr.translate(0, -2.82, 0))
garaje.add_node("ruedaFD", attach_to = "R_Derechas", mesh = rueda, transform = tr.translate(0, 2.82, 0))
garaje.add_node("ruedaFI", attach_to = "R_Izquierdas", mesh = rueda, transform = tr.translate(0, 2.82, 0))


#axes = Modelo(shapes.Axes["position"], shapes.Axes["color"])
#axes.inicializar(pipeline1)

#print("Controles Cámara:\n\tWASD: Rotar\n\t Q/E: Acercar/Alejar\n\t1/2: Cambiar tipo")
#def update(dt):
#    if ventana.is_key_pressed(pyglet.window.key.A):
#        camara.phi -= dt
#    if ventana.is_key_pressed(pyglet.window.key.D):
#        camara.phi += dt
#    if ventana.is_key_pressed(pyglet.window.key.W):
#        camara.theta -= dt
#    if ventana.is_key_pressed(pyglet.window.key.S):
#        camara.theta += dt
#    if ventana.is_key_pressed(pyglet.window.key.Q):
#        camara.distancia += dt
#    if ventana.is_key_pressed(pyglet.window.key.E):
#        camara.distancia -= dt
#    if ventana.is_key_pressed(pyglet.window.key._1):
#        camara.tipo = "perspectiva"
#    if ventana.is_key_pressed(pyglet.window.key._2):
#        camara.tipo = "ortografica"

#    camara.update()

def update(dt):
    coseno = abs(np.cos(camara.phi))

    if coseno < 0.6:
        coseno = 0.6

    camara.distancia = coseno + 0.5
    
    camara.phi -= dt / 2
    camara.update()

@ventana.event
def on_draw(): 
    ventana.clear()
    pipeline1.use()

    pipeline1["u_view"] = camara.obtener_vista()
    pipeline1["u_projection"] = camara.obtener_proyeccion(ventana.ancho,ventana.alto)
    
    #pipeline1["u_model"] = axes.transformaciones()
    #axes.dibujar(GL.GL_LINES)

    garaje.dibujar()

pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()    