#Implementacion de la tarea #2

import pyglet
from OpenGL import GL
import numpy as np
import sys
import trimesh as tm
from trimesh.scene.scene import Scene

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
ALTO = 800

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
                                "seleccion": 0, 
                                "Key_Cool_Down": 0,
                                "transicion": False, 
                                "Offset_Inicial": None,
                                "Offset_Final": np.array([0, 0, 15], dtype=np.float32),
                                "Offset_Actual": np.array([0, 0, 15], dtype=np.float32),
                                "Parametro_Vista_Final": 0,
                                "Parametro_Vista_Actual": 0
                            }
                                 #valores por defecto de la posicion del centro de la camera, y a donde miramos.
        self.init()

    def init(self):
        GL.glClearColor(0.118, 0.122, 0.11, 1.0) #Gris
        GL.glEnable(GL.GL_DEPTH_TEST)
    
    def is_key_pressed(self, key):
        return self.key_handler[key]

class cameraOrbital(Camera):
    def __init__(self, distancia, tipo = "perspective", ancho = ANCHO, alto = ALTO, center_offset = np.array([0, 0, 0], dtype=np.float32), angle_offset = 0):
        super().__init__(tipo, ancho, alto)
        self.distancia = distancia
        self.center_offset = center_offset
        self.angle_offset = angle_offset
        self.phi = 0 + angle_offset
        self.theta = np.pi / 2.7
        self.update()

    def update(self):
        if self.theta > np.pi:
            self.theta = np.pi
        elif self.theta < 0:
            self.theta = 0.0001

        self.position[0] = self.distancia * np.sin(self.theta) * np.sin(self.phi + self.angle_offset) + self.center_offset[0]
        self.position[1] = self.distancia * np.cos(self.theta) + self.center_offset[1]
        self.position[2] = self.distancia * np.sin(self.theta) * np.cos(self.phi + self.angle_offset) + self.center_offset[2]

def mesh_from_file_custom(path, escalar = True):
    mesh_data = tm.load(path)
    
    if escalar:
        mesh_data.apply_transform(tr.uniformScale(2.0 / mesh_data.scale))

    mesh_list = []

    def process_geometry(id, geometry):
        vertex_data = tm.rendering.mesh_to_vertexlist(geometry)
        indices = vertex_data[3]
        positions = vertex_data[4][1]
        uvs = None
        texture = None
        normals = vertex_data[5][1]

        if geometry.visual.kind == "texture":
            texture = Texture()
            uvs = vertex_data[6][1]
            texture.create_from_image(geometry.visual.material.image)

        model = Model(positions, uvs, normals, indices)
        return {"id": id, "mesh": model, "texture": texture}

    if type(mesh_data) is Scene:
        for id, geometry in mesh_data.geometry.items():
            mesh_list.append(process_geometry(id, geometry))
    else:
        mesh_list.append(process_geometry("model", mesh_data))

    return mesh_list

##################################################################################################################################################################

if __name__ == "__main__":
    #Inicializamos programa

    Ventana = Ventana(ANCHO, ALTO, "Tarea #2")

    #Cargamos los archivos de shader y e inicializamos el pipeline
    Color_Mesh_Lit_Pipeline = init_pipeline(
        get_path("auxiliares/shaders/color_mesh_lit.vert"),
        get_path("auxiliares/shaders/color_mesh_lit.frag"))

    '''
    Ventana.program_state["camera"] = FreeCamera([2.5, 2.5, 2.5], "perspective")
    Ventana.program_state["camera"].yaw = -3* np.pi/ 4
    Ventana.program_state["camera"].pitch = -np.pi / 4
    '''

    Ventana.program_state["camera"] = cameraOrbital(8, ancho = Ventana.ancho, alto = Ventana.alto)
    Ventana.program_state["camera"].theta = np.pi / 2.7
    Ventana.program_state["camera"].center_offset = np.array([0, 0, 15])
    Ventana.program_state["camera"].focus = np.array([0, 0, 15])
    

    #Importamos el vehiculo

    Mesh_Cilindro = mesh_from_file_custom("Tarea-2/Models/Cilindro(Radio = 1, Altura = 2, Centrado).stl", escalar = False)[0]["mesh"]
    Mesh_Cuboide = mesh_from_file_custom("Tarea-2/Models/Cuboide(30x16x30).stl", escalar = False)[0]["mesh"]
    Mesh_marcador = mesh_from_file_custom("Tarea-2/Models/Cuboide(30x16x30).stl")[0]["mesh"]
    
    Mesh_Chasis = mesh_from_file_custom("Tarea-2/Models/Chevrolet_Camaro_SS_Chasis.stl", escalar = False)[0]["mesh"]
    Mesh_Ventanas = mesh_from_file_custom("Tarea-2/Models/Chevrolet_Camaro_SS_Ventanas.stl", escalar = False)[0]["mesh"]
    Mesh_Adornos = mesh_from_file_custom("Tarea-2/Models/Chevrolet_Camaro_SS_Adornos_Metalicos.stl", escalar = False)[0]["mesh"]
    Mesh_Focos = mesh_from_file_custom("Tarea-2/Models/Chevrolet_Camaro_SS_Focos_Delanteros.stl", escalar = False)[0]["mesh"]
    
    Mesh_Neumaticos = mesh_from_file_custom("Tarea-2/Models/Chevrolet_Camaro_SS_Neumaticos.stl", escalar = False)[0]["mesh"]
    Mesh_Rines = mesh_from_file_custom("Tarea-2/Models/Chevrolet_Camaro_SS_Rines.stl", escalar = False)[0]["mesh"]

    #Dimensiones del chasis (approx): 4 x 3 x 10
    #Dimensiones del cilindro base: Radio: 1, altura: 2
    
###################################################################################################################################################################
#Grafo de escena

    Garaje = SceneGraph(Ventana)

    
    Garaje.add_node("Luz_global",
                    pipeline = Color_Mesh_Lit_Pipeline,
                    rotation = np.array([0, 0, np.pi/2]),
                    light = DirectionalLight(
                            ambient = np.array([0.3, 0.2, 0.2]),
                            diffuse = np.array([0.3, 0.2, 0.2]),
                            specular = np.array([0.3, 0.2, 0.2])
                            ),
                    )
    

    Garaje.add_node("garaje", 
                    mesh = Mesh_Cilindro, 
                    pipeline = Color_Mesh_Lit_Pipeline,
                    transform = tr.translate(0, 6, 0) @ tr.scale(25, 6, 25),
                    material = Material(
                                ambient = np.array([0.2, 0.2, 0.2]),
                                diffuse = np.array([0.6, 0.5, 0.5]),
                                specular = np.array([0.6, 0.5, 0.5])
                                ),
                    cull_face = False)

    ###############################################################################################################################################################
    #Primer Vehiculo:

    Garaje.add_node("Plataforma_1",
                    transform = tr.translate(0, 0, 15)
                    ) 

    Garaje.add_node("Marcador_1",
                    attach_to = "Plataforma_1",
                    #mesh = Mesh_marcador,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    position = np.array([0, 5, 2]),
                    material = Material(
                                ambient = np.array([1, 1, 1]),
                                diffuse = np.array([1, 1, 1]),
                                specular = np.array([1, 1, 1]),
                                shininess = 5
                                ),
                    )

    
    Garaje.add_node("Luz_Vehiculo_1", 
                    attach_to = "Marcador_1",
                    pipeline = Color_Mesh_Lit_Pipeline, 
                    light = PointLight(
                            diffuse = [1, 1, 1], 
                            specular = [1, 1, 1], 
                            ambient = [1, 1, 1],
                            constant = 1,
                            linear = 0.09,
                            quadratic = 0.032,
                    )
                    )
    
    
    Garaje.add_node("Cilindro_1", 
                    attach_to = "Plataforma_1",
                    mesh = Mesh_Cilindro, 
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.639, 0.624, 0.584],
                                specular = [0.3, 0.3, 0.3],
                                shininess = 5
                    ),
                    transform = tr.scale(6, 0.15, 6)
                    )

    Garaje.add_node("Vehiculo_1",
                    attach_to = "Plataforma_1",
                    transform = tr.translate(0, 1.66, 0) @ tr.rotationY(-np.pi/2)
                    )
    
    Garaje.add_node("Chasis_1",
                    attach_to = "Vehiculo_1",
                    mesh = Mesh_Chasis,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.859, 0.075, 0.075],
                                specular = [0.859, 0.541, 0.541],
                                shininess = 128
                    )
                    )

    Garaje.add_node("Ventanas_1",
                    attach_to = "Vehiculo_1",
                    mesh = Mesh_Ventanas,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.016, 0.8, 0.941],
                                specular = [0.116, 0.9, 1],
                                shininess = 32
                    )
                    )

    Garaje.add_node("Adornos_1",
                    attach_to = "Vehiculo_1",
                    mesh = Mesh_Adornos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.876, 0.924, 0.931],
                                specular = [0.976, 0.924, 0.931],
                                shininess = 128
                    )
                    )

    Garaje.add_node("Focos_1",
                    attach_to = "Vehiculo_1",
                    mesh = Mesh_Focos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.996, 1, 0.843],
                                diffuse = [0.98, 1, 0],
                                specular = [0.98, 1, 0],
                                shininess = 32
                    )
                    )

    Garaje.add_node("Luz_Focos_1", 
                    attach_to = "Focos_1",
                    pipeline = Color_Mesh_Lit_Pipeline,
                    rotation = [0, np.pi / 2, 0],
                    position = [1.5, 0, 0],
                    light = SpotLight(
                            diffuse = [0.996, 1, 0.843], 
                            specular = [0.996, 1, 0.843], 
                            ambient = [0.996, 1, 0.843],
                            constant = 1,
                            linear = 0.09,
                            quadratic = 0.032,
                            outerCutOff = 0.92,
                            cutOff = 0.99
                    )
                    )

    Garaje.add_node("Neumaticos_1",
                    attach_to = "Vehiculo_1",
                    mesh = Mesh_Neumaticos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.2, 0.216, 0.22],
                                specular = [0.2, 0.216, 0.22],
                                shininess = 2
                    )
                    )
    
    Garaje.add_node("Rines_1",
                    attach_to = "Vehiculo_1",
                    mesh = Mesh_Rines,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.776, 0.824, 0.831],
                                specular = [0.876, 0.924, 0.931],
                                shininess = 128
                    )
                    )

    ###############################################################################################################################################################
    #Segundo Vehiculo:

    Garaje.add_node("Plataforma_2",
                    transform = tr.translate(-12.99, 0, -7.5) @ tr.rotationY(- np.pi / 6)
                    ) 

    Garaje.add_node("Marcador_2",
                    attach_to = "Plataforma_2",
                    #mesh = Mesh_marcador,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    position = [0, 5, 2],
                    material = Material(
                                ambient = [1, 1, 1],
                                diffuse = [1, 1, 1],
                                specular = [1, 1, 1],
                                shininess = 5
                                )
                    )

    
    Garaje.add_node("Luz_Vehiculo_2", 
                    attach_to = "Marcador_2",
                    pipeline = Color_Mesh_Lit_Pipeline, 
                    light = PointLight(
                            diffuse = [1, 1, 1], 
                            specular = [1, 1, 1], 
                            ambient = [1, 1, 1],
                            constant = 1,
                            linear = 0.09,
                            quadratic = 0.032,
                    )
                    )
    
    
    Garaje.add_node("Cilindro_2", 
                    attach_to = "Plataforma_2",
                    mesh = Mesh_Cilindro, 
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.639, 0.624, 0.584],
                                specular = [0.3, 0.3, 0.3],
                                shininess = 5
                    ),
                    transform = tr.scale(6, 0.15, 6)
                    )

    Garaje.add_node("Vehiculo_2",
                    attach_to = "Plataforma_2",
                    transform = tr.translate(0, 1.66, 0) @ tr.rotationY(np.pi)
                    )
    
    Garaje.add_node("Chasis_2",
                    attach_to = "Vehiculo_2",
                    mesh = Mesh_Chasis,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.016, 0.631, 0.133],
                                specular = [0.439, 0.812, 0.051],
                                shininess = 128
                    )
                    )

    Garaje.add_node("Ventanas_2",
                    attach_to = "Vehiculo_2",
                    mesh = Mesh_Ventanas,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.016, 0.8, 0.941],
                                specular = [0.116, 0.9, 1],
                                shininess = 32
                    )
                    )

    Garaje.add_node("Adornos_2",
                    attach_to = "Vehiculo_2",
                    mesh = Mesh_Adornos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.876, 0.924, 0.931],
                                specular = [0.976, 0.924, 0.931],
                                shininess = 128
                    )
                    )

    Garaje.add_node("Focos_2",
                    attach_to = "Vehiculo_2",
                    mesh = Mesh_Focos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.996, 1, 0.843],
                                diffuse = [0.98, 1, 0],
                                specular = [0.98, 1, 0],
                                shininess = 32
                    )
                    )

    Garaje.add_node("Luz_Focos_2", 
                    attach_to = "Focos_2",
                    pipeline = Color_Mesh_Lit_Pipeline,
                    rotation = [0, np.pi / 2, 0],
                    position = [1.5, 0, 0],
                    light = SpotLight(
                            diffuse = [0.996, 1, 0.843], 
                            specular = [0.996, 1, 0.843], 
                            ambient = [0.996, 1, 0.843],
                            constant = 1,
                            linear = 0.09,
                            quadratic = 0.032,
                            outerCutOff = 0.92,
                            cutOff = 0.99
                    )
                    )

    Garaje.add_node("Neumaticos_2",
                    attach_to = "Vehiculo_2",
                    mesh = Mesh_Neumaticos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.2, 0.216, 0.22],
                                specular = [0.2, 0.216, 0.22],
                                shininess = 2
                    )
                    )
    
    Garaje.add_node("Rines_2",
                    attach_to = "Vehiculo_2",
                    mesh = Mesh_Rines,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.776, 0.824, 0.831],
                                specular = [0.876, 0.924, 0.931],
                                shininess = 128
                    )
                    )

    ##############################################################################################################################################################
    #Tercer Vehiculo:

    Garaje.add_node("Plataforma_3",
                    transform = tr.translate(12.99, 0, -7.5) @ tr.rotationY(-5 * np.pi / 6)
                    ) 

    Garaje.add_node("Marcador_3",
                    attach_to = "Plataforma_3",
                    #mesh = Mesh_marcador,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    position = [0, 5, 2],
                    material = Material(
                                ambient = [1, 1, 1],
                                diffuse = [1, 1, 1],
                                specular = [1, 1, 1],
                                shininess = 5
                                )
                    )

    
    Garaje.add_node("Luz_Vehiculo_3", 
                    attach_to = "Marcador_3",
                    pipeline = Color_Mesh_Lit_Pipeline, 
                    light = PointLight(
                            diffuse = [1, 1, 1], 
                            specular = [1, 1, 1], 
                            ambient = [1, 1, 1],
                            constant = 1,
                            linear = 0.09,
                            quadratic = 0.032,
                    )
                    )
    
    
    Garaje.add_node("Cilindro_3", 
                    attach_to = "Plataforma_3",
                    mesh = Mesh_Cilindro, 
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.639, 0.624, 0.584],
                                specular = [0.3, 0.3, 0.3],
                                shininess = 5
                    ),
                    transform = tr.scale(6, 0.15, 6)
                    )

    Garaje.add_node("Vehiculo_3",
                    attach_to = "Plataforma_3",
                    transform = tr.translate(0, 1.66, 0) @ tr.rotationY(np.pi)
                    )
    
    Garaje.add_node("Chasis_3",
                    attach_to = "Vehiculo_3",
                    mesh = Mesh_Chasis,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.239, 0.063, 0.949],
                                specular = [0.592, 0.525, 0.859],
                                shininess = 128
                    )
                    )

    Garaje.add_node("Ventanas_3",
                    attach_to = "Vehiculo_3",
                    mesh = Mesh_Ventanas,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.016, 0.8, 0.941],
                                specular = [0.116, 0.9, 1],
                                shininess = 32
                    )
                    )

    Garaje.add_node("Adornos_3",
                    attach_to = "Vehiculo_3",
                    mesh = Mesh_Adornos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.876, 0.924, 0.931],
                                specular = [0.976, 0.924, 0.931],
                                shininess = 128
                    )
                    )

    Garaje.add_node("Focos_3",
                    attach_to = "Vehiculo_3",
                    mesh = Mesh_Focos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.996, 1, 0.843],
                                diffuse = [0.98, 1, 0],
                                specular = [0.98, 1, 0],
                                shininess = 32
                    )
                    )

    Garaje.add_node("Luz_Focos_3", 
                    attach_to = "Focos_3",
                    pipeline = Color_Mesh_Lit_Pipeline,
                    rotation = [0, np.pi / 2, 0],
                    position = [1.5, 0, 0],
                    light = SpotLight(
                            diffuse = [0.996, 1, 0.843], 
                            specular = [0.996, 1, 0.843], 
                            ambient = [0.996, 1, 0.843],
                            constant = 1,
                            linear = 0.09,
                            quadratic = 0.032,
                            outerCutOff = 0.92,
                            cutOff = 0.99
                    )
                    )

    Garaje.add_node("Neumaticos_3",
                    attach_to = "Vehiculo_3",
                    mesh = Mesh_Neumaticos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = [0.1, 0.1, 0.1],
                                diffuse = [0.2, 0.216, 0.22],
                                specular = [0.2, 0.216, 0.22],
                                shininess = 2
                    )
                    )
    
    Garaje.add_node("Rines_3",
                    attach_to = "Vehiculo_3",
                    mesh = Mesh_Rines,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material(
                                ambient = np.array([0.1, 0.1, 0.1]),
                                diffuse = np.array([0.776, 0.824, 0.831]),
                                specular = np.array([0.876, 0.924, 0.931]),
                                shininess = 128
                    )
                    )

###################################################################################################################################################################
#Logica de actualizacion:
    def Circunferencia(parametro):
        x = 15 * np.cos(parametro + (np.pi / 2))
        y = 0
        z = 15 * np.sin(parametro + (np.pi / 2))

        return np.array([x,y,z])
        
    
    def Transicion_suave(dt, offset_inicial, offset_final, offset_actual):
        signo_offset_x = np.sign(offset_final[0] - offset_actual[0])
        signo_offset_z = np.sign(offset_final[2] - offset_actual[2])
    
        if signo_offset_x > 0:
            if signo_offset_z != 0:
                X_offset = np.array([offset_inicial[0], offset_final[0]], dtype = np.float32)
                Y_offset = np.array([offset_inicial[2], offset_final[2]], dtype = np.float32)
        
                offset_actual[0] += dt * 4.5
                offset_actual[2] = np.interp(offset_actual[0], X_offset, Y_offset)
            else:
                offset_actual[0] += dt * 9

        if signo_offset_x < 0:
            if signo_offset_z != 0:
                X_offset = np.array([offset_final[0], offset_inicial[0]], dtype = np.float32)
                Y_offset = np.array([offset_final[2], offset_inicial[2]], dtype = np.float32)
        
                offset_actual[0] -= dt * 4.5
                offset_actual[2] = np.interp(offset_actual[0], X_offset, Y_offset)
            else:
                offset_actual[0] -= dt * 9
        

        return offset_actual
    
    def Elevacion_Camara():
        pass
    
    def update(dt):
        camera = Ventana.program_state["camera"]
        Ventana.program_state["Key_Cool_Down"] += dt

        if Ventana.program_state["Key_Cool_Down"] >= 10.0:
            Ventana.program_state["Key_Cool_Down"] = 0.01 #Para que el numero no se vaya a la cresta xD

        if not Ventana.program_state["transicion"]:
            coseno = abs(np.cos(camera.phi))  #Por mejorar

            if coseno < 0.75:
                coseno = 0.75

            camera.distancia = 7.75 * coseno
    
            camera.phi += dt / 2

            if camera.phi >= np.pi * 2:
                camera.phi = 0

        if Ventana.is_key_pressed(pyglet.window.key.SPACE) and Ventana.program_state["Key_Cool_Down"] >= 0.5 and not Ventana.program_state["transicion"]:
        
            if Ventana.program_state["seleccion"] == 0:
                Ventana.program_state["Offset_Inicial"] = np.array([0, 0, 15])
                Ventana.program_state["Offset_Final"] = np.array([-12.99, 0, -7.5])

                Ventana.program_state["Parametro_Vista_Final"] = 2 / 3
                
                camera.angle_offset = -2 * np.pi / 3
        
            elif Ventana.program_state["seleccion"] == 1:
                Ventana.program_state["Offset_Inicial"] = np.array([-12.99, 0, -7.5])
                Ventana.program_state["Offset_Final"] = np.array([12.99, 0, -7.5])

                Ventana.program_state["Parametro_Vista_Final"] = 4 / 3
                
                camera.angle_offset = -4 * np.pi / 3

            else:
                Ventana.program_state["Offset_Inicial"] = np.array([12.99, 0, -7.5])
                Ventana.program_state["Offset_Final"] = np.array([0, 0, 15])

                Ventana.program_state["Parametro_Vista_Final"] = 2
                
                camera.angle_offset = 0

            Ventana.program_state["seleccion"] += 1

            if Ventana.program_state["seleccion"] > 2:
                Ventana.program_state["seleccion"] = 0

            camera.focus = Ventana.program_state["Offset_Final"]
            #camera.phi = 3 * np.pi / 4

            Ventana.program_state["Key_Cool_Down"] = 0

        #################################################################################

        if np.sqrt(np.square(Ventana.program_state["Offset_Final"][0] - Ventana.program_state["Offset_Actual"][0]) + np.square(Ventana.program_state["Offset_Final"][2] - Ventana.program_state["Offset_Actual"][2])) > 0.1:
        #Ejecutamos si la distancia entre el offset actual y el final es mayor a 0.1 (Es decir, debemos desplazarnos)

            #Logica para mover suavemente el centro de la camara
            Ventana.program_state["transicion"] = True
            Ventana.program_state["Offset_Actual"] = Transicion_suave(dt, Ventana.program_state["Offset_Inicial"], 
                                                                        Ventana.program_state["Offset_Final"], 
                                                                        Ventana.program_state["Offset_Actual"],
                                                                    )
            
            camera.center_offset = Ventana.program_state["Offset_Actual"]

            #Logica para voltear la camara de manera suave
            delta_parametro = Ventana.program_state["Parametro_Vista_Final"] - Ventana.program_state["Parametro_Vista_Actual"]

            if delta_parametro >= 0.01:
                Ventana.program_state["Parametro_Vista_Actual"] += dt / 4

            else:
                camera.focus = Circunferencia(Ventana.program_state["Parametro_Vista_Final"] * np.pi)

            camera.focus = Circunferencia(Ventana.program_state["Parametro_Vista_Actual"] * np.pi)


        else:
            Ventana.program_state["transicion"] = False
            camera.center_offset = Ventana.program_state["Offset_Final"]

            if Ventana.program_state["seleccion"] == 0:
                Ventana.program_state["Parametro_Vista_Actual"] = 0

        print(Ventana.program_state["Parametro_Vista_Actual"])
        camera.update()

    @Ventana.event
    def on_resize(width, height):
        Ventana.program_state["camera"].resize(width, height)

    # draw loop
    @Ventana.event
    def on_draw():
        Ventana.clear()
        Garaje.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
