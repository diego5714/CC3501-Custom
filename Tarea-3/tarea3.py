#Implementacion de la tarea #3

import pyglet
from OpenGL import GL
import numpy as np
import sys
import trimesh as tm
from trimesh.scene.scene import Scene
from Box2D import b2PolygonShape, b2World

import car_select_scene
import track_scene

if sys.path[0] != "":
    sys.path.insert(0, "")
sys.path.append('../')

import grafica.transformations as tr
import auxiliares.utils.shapes as shapes
from auxiliares.utils.camera import Camera, FreeCamera
from auxiliares.utils.scene_graph import SceneGraph
from auxiliares.utils.drawables import Model, Texture, DirectionalLight, PointLight, SpotLight, Material
from auxiliares.utils.helpers import init_axis, init_pipeline, mesh_from_file, get_path

#Resolucion inicial
ANCHO = 1280
ALTO = 720

#Definimos cool down para la pulsacion de teclas:
Max_CD = 0.5

class Ventana(pyglet.window.Window):
    def __init__(self, ancho, alto, titulo):
        super().__init__(ancho, alto, resizable = True, caption = titulo)
        self.set_minimum_size(200,200)
        self.ancho = ANCHO
        self.alto = ALTO
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_handler)
        self.program_state = {  "camera": None,
                                "pista": None,
                                "scene": 0,
                                "seleccion": 0, 
                                "Key_Cool_Down": 0,
                                "transicion": False,
                                "Offset_Inicial": None,
                                "Offset_Final": np.array([0, 0, 15], dtype=np.float32),
                                "Offset_Actual": np.array([0, 0, 15], dtype=np.float32),
                                "Parametro_Vista_Final": 0,
                                "Parametro_Vista_Actual": 0,
                                "Angulo_Final": np.pi,
                                "physics_world" : None,
                                "bodies": {},
                                #Parametros para el integrador de fuerzas
                                "vel_iters": 10,
                                "pos_iters": 10
                            }
                                 #valores por defecto de la posicion del centro de la camera, y a donde miramos.
        self.init()

    def init(self):
        GL.glClearColor(1.0, 1.0, 1.0, 1.0) #Blanco
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)
    
    def is_key_pressed(self, key):
        return self.key_handler[key]

class Camara_Orbital(Camera):
    def __init__(self, distancia, tipo = "perspective", ancho = ANCHO, alto = ALTO, center_offset = np.array([0, 0, 0], dtype=np.float32), angle_offset = np.pi):
        super().__init__(tipo, ancho, alto)
        self.distancia = distancia
        self.center_offset = center_offset
        self.angle_offset = angle_offset
        self.phi = 0
        self.theta = np.pi / 2.7
        self.update()

    def update(self):
        if self.theta > np.pi:
            self.theta = np.pi
        elif self.theta < 0:
            self.theta = 0.0001

        self.position[0] = self.distancia * np.sin(self.theta) * np.sin(-1 * self.phi + self.angle_offset) + self.center_offset[0]
        self.position[1] = self.distancia * np.cos(self.theta) + self.center_offset[1]
        self.position[2] = self.distancia * np.sin(self.theta) * np.cos(-1 * self.phi + self.angle_offset) + self.center_offset[2]

if __name__ == "__main__":

    ventana = Ventana(ANCHO, ALTO, "Tarea #3")

    #Creamos y configuramos la camara con sus parametros iniciales
    ventana.program_state["camera"] = Camara_Orbital(7, ancho = ventana.ancho, alto = ventana.alto)
    ventana.program_state["camera"].theta = np.pi / 2.7
    ventana.program_state["camera"].phi = 0
    
    ventana.program_state["camera"].center_offset = ventana.program_state["Offset_Actual"]
    ventana.program_state["camera"].focus = np.array([0, 0, 15])
    

    garaje = car_select_scene.crear_garaje(ventana)
    axis_scene = init_axis(ventana)

    def update(dt):
        ventana.program_state["Key_Cool_Down"] += dt

        if ventana.program_state["Key_Cool_Down"] >= 10.0:
            ventana.program_state["Key_Cool_Down"] = 0.01

        if ventana.is_key_pressed(pyglet.window.key.ENTER) \
            and ventana.program_state["Key_Cool_Down"] >= 0.5 \
            and ventana.program_state["scene"] == 0 \
            and not ventana.program_state["transicion"]:
            
            ventana.program_state["pista"] = track_scene.crear_pista(ventana)
            
            ventana.program_state["scene"] = 1
            ventana.program_state["camera"].focus = np.array([0, 0, 0])
            ventana.program_state["camera"].center_offset = np.array([0, 0, -2])
            ventana.program_state["camera"].angle_offset = 0
            ventana.program_state["camera"].phi = np.pi / 2 - 0.225
            ventana.program_state["camera"].theta = np.pi / 3
            ventana.program_state["camera"].distancia = 10

            
        
        if ventana.program_state["scene"] == 0:
            car_select_scene.update_garaje(dt, ventana, garaje)
        
        else:
            track_scene.update_pista(dt, ventana, ventana.program_state["pista"])

        camera = ventana.program_state["camera"]
        #print([camera.phi, camera.angle_offset])

    @ventana.event
    def on_resize(width, height):
        ventana.program_state["camera"].resize(width, height)

    # draw loop
    @ventana.event
    def on_draw():
        ventana.clear()
        
        if ventana.program_state["scene"] == 0:
            garaje.draw()
        
        else:
            ventana.program_state["pista"].draw()
            axis_scene.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()