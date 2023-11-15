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
                                "seleccion": 0, 
                                "Key_Cool_Down": 0,
                                "transicion": False,
                                "Offset_Inicial": None,
                                "Offset_Final": np.array([0, 0, 15], dtype=np.float32),
                                "Offset_Actual": np.array([0, 0, 15], dtype=np.float32),
                                "Parametro_Vista_Final": 0,
                                "Parametro_Vista_Actual": 0,
                                "Angulo_Final": np.pi
                            }
                                 #valores por defecto de la posicion del centro de la camera, y a donde miramos.
        self.init()

    def init(self):
        GL.glClearColor(0.118, 0.122, 0.11, 1.0) #Gris
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)
    
    def is_key_pressed(self, key):
        return self.key_handler[key]

class Camara_Orbital(Camera):
    def __init__(self, distancia, tipo = "perspective", ancho = ANCHO, alto = ALTO, center_offset = np.array([0, 0, 0], dtype=np.float32)):
        super().__init__(tipo, ancho, alto)
        self.distancia = distancia
        self.center_offset = center_offset
        self.phi = 0
        self.theta = np.pi / 2.7
        self.update()

    def update(self):
        if self.theta > np.pi:
            self.theta = np.pi
        elif self.theta < 0:
            self.theta = 0.0001

        self.position[0] = self.distancia * np.sin(self.theta) * np.sin(-1 * self.phi + np.pi) + self.center_offset[0]
        self.position[1] = self.distancia * np.cos(self.theta) + self.center_offset[1]
        self.position[2] = self.distancia * np.sin(self.theta) * np.cos(-1 * self.phi + np.pi) + self.center_offset[2]

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

    print("##########################################")
    print("##########################################")
    print("Cambiar vehiculo seleccionado con ESPACIO")
    print("##########################################")
    print("##########################################")
    
    Ventana = Ventana(ANCHO, ALTO, "Tarea #2")

    #Cargamos los archivos de shader y e inicializamos el pipeline
    Color_Mesh_Lit_Pipeline = init_pipeline(
        get_path("auxiliares/shaders/color_mesh_lit.vert"),
        get_path("auxiliares/shaders/color_mesh_lit.frag"))


    #Creamos y configuramos la camara con sus parametros iniciales
    Ventana.program_state["camera"] = Camara_Orbital(7, ancho = Ventana.ancho, alto = Ventana.alto)
    Ventana.program_state["camera"].theta = np.pi / 2.7
    Ventana.program_state["camera"].phi = 0
    
    Ventana.program_state["camera"].center_offset = Ventana.program_state["Offset_Actual"]
    Ventana.program_state["camera"].focus = np.array([0, 0, 15])
    

    #Importamos el vehiculo y el escenario

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

    #Materiales:

    Color_Material_Cromo = np.array([np.array([0.25, 0.25, 0.25]), np.array([0.4, 0.4, 0.4]), np.array([0.774597, 0.774597, 0.774597])])
    Color_Material_Goma_Negra = np.array([np.array([0.02, 0.02, 0.02]), np.array([0.01, 0.01, 0.01]), np.array([0.4, 0.4, 0.4])])
    Color_Material_Oro_Pulido = np.array([np.array([0.24725, 0.2245, 0.0645]), np.array([0.34615, 0.3143, 0.0903]), np.array([0.797357, 0.723991, 0.208006])])
    Color_Material_Rubi = np.array([np.array([0.1745, 0.01175, 0.01175]), np.array([0.61424, 0.04136, 0.04136]), np.array([0.727811, 0.626959, 0.626959])])
    Color_Material_Esmeralda = np.array([np.array([0.0215, 0.1745, 0.0215]), np.array([0.07568, 0.61424, 0.07568]), np.array([0.633, 0.727811, 0.633])])
    Color_Material_Ventanas = np.array([np.array([0.1, 0.1, 0.1]), np.array([0.016, 0.8, 0.941]), np.array([0.116, 0.9, 1])])
    Color_Material_Plata = np.array([np.array([0.19225, 0.19225, 0.19225]), np.array([0.50754, 0.50754, 0.50754]), np.array([0.508273, 0.508273, 0.508273])])

    Color_Luz_Focos = np.array([np.array([0.98, 1, 0.843]), np.array([0.98, 1, 0.843]), np.array([0.98, 1, 0.843])])
    Material_Focos = Material(Color_Luz_Focos[0], Color_Luz_Focos[1], Color_Luz_Focos[2])
    
    Color_Luces_Plataforma = np.array([np.array([1, 1, 1]), np.array([1, 1, 1]), np.array([1, 1, 1])])
    Material_Marcadores_Luz = Material(Color_Luces_Plataforma[0], Color_Luces_Plataforma[1], Color_Luces_Plataforma[2])

    Material_Cromo = Material(Color_Material_Cromo[0], Color_Material_Cromo[1], Color_Material_Cromo[2], 76.8)
    Material_Goma_Negra = Material(Color_Material_Goma_Negra[0], Color_Material_Goma_Negra[1], Color_Material_Goma_Negra[2], 10)
    Material_Oro_Pulido = Material(Color_Material_Oro_Pulido[0], Color_Material_Oro_Pulido[1], Color_Material_Oro_Pulido[2], 83.2)
    Material_Rubi = Material(Color_Material_Rubi[0], Color_Material_Rubi[1], Color_Material_Rubi[2], 76.8)
    Material_Esmeralda = Material(Color_Material_Esmeralda[0], Color_Material_Esmeralda[1], Color_Material_Esmeralda[2], 76.8)
    Material_Ventanas = Material(Color_Material_Ventanas[0], Color_Material_Ventanas[1], Color_Material_Ventanas[2], 8)
    Material_Plata = Material(Color_Material_Plata[0], Color_Material_Plata[1], Color_Material_Plata[2], 51.2)

###################################################################################################################################################################
#Grafo de escena

    Garaje = SceneGraph(Ventana)

    
    Garaje.add_node("Luz_global",
                    pipeline = Color_Mesh_Lit_Pipeline,
                    rotation = np.array([0, 0, np.pi/2]),
                    light = DirectionalLight(
                            ambient = np.array([0.1, 0.1, 0.1]),
                            diffuse = np.array([0.1, 0.1, 0.1]),
                            specular = np.array([0.1, 0.1, 0.1])
                            ),
                    )
    

    Garaje.add_node("garaje", 
                    mesh = Mesh_Cilindro, 
                    pipeline = Color_Mesh_Lit_Pipeline,
                    transform = tr.translate(0, 6, 0) @ tr.scale(25, 6, 25),
                    material = Material(
                                ambient = np.array([0.2, 0.2, 0.2]),
                                diffuse = np.array([0.5, 0.4, 0.4]),
                                specular = np.array([0.6, 0.5, 0.5])
                                ),
                    cull_face = False)

    ###############################################################################################################################################################
    #Primer Vehiculo:

    Garaje.add_node("Plataforma_1",
                    transform = tr.translate(0, 0, 15)
                    ) 

    
    Garaje.add_node("Luz_Vehiculo_A1", 
                    attach_to = "Plataforma_1",
                    pipeline = Color_Mesh_Lit_Pipeline, 
                    position = np.array([5, 5, 2.5]),
                    light = PointLight(
                            ambient = Color_Luces_Plataforma[0],
                            diffuse = Color_Luces_Plataforma[1], 
                            specular = Color_Luces_Plataforma[2], 
                            constant = 1,
                            linear = 0.14,
                            quadratic = 0.07,
                    )
                    )

    Garaje.add_node("Luz_Vehiculo_B1", 
                    attach_to = "Plataforma_1",
                    pipeline = Color_Mesh_Lit_Pipeline, 
                    position = np.array([5, 5, -2.5]),
                    light = PointLight(
                            ambient = Color_Luces_Plataforma[0],
                            diffuse = Color_Luces_Plataforma[1], 
                            specular = Color_Luces_Plataforma[2], 
                            constant = 1,
                            linear = 0.12,
                            quadratic = 0.05,
                    )
                    )

    Garaje.add_node("Luz_Vehiculo_C1", 
                    attach_to = "Plataforma_1",
                    pipeline = Color_Mesh_Lit_Pipeline, 
                    position = np.array([-5, 5, 2.5]),
                    light = PointLight(
                            ambient = Color_Luces_Plataforma[0],
                            diffuse = Color_Luces_Plataforma[1], 
                            specular = Color_Luces_Plataforma[2], 
                            constant = 1,
                            linear = 0.12,
                            quadratic = 0.05,
                    )
                    )

    Garaje.add_node("Luz_Vehiculo_D1", 
                    attach_to = "Plataforma_1",
                    pipeline = Color_Mesh_Lit_Pipeline, 
                    position = np.array([-5, 5, -2.5]),
                    light = PointLight(
                            ambient = Color_Luces_Plataforma[0],
                            diffuse = Color_Luces_Plataforma[1], 
                            specular = Color_Luces_Plataforma[2], 
                            constant = 1,
                            linear = 0.12,
                            quadratic = 0.05,
                    )
                    )

    Garaje.add_node("Marcador_A1",
                    attach_to = "Luz_Vehiculo_A1",
                    #mesh = Mesh_marcador,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Marcadores_Luz,
                    )

    Garaje.add_node("Marcador_B1",
                    attach_to = "Luz_Vehiculo_B1",
                    #mesh = Mesh_marcador,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Marcadores_Luz,
                    )

    Garaje.add_node("Marcador_C1",
                    attach_to = "Luz_Vehiculo_C1",
                    #mesh = Mesh_marcador,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Marcadores_Luz,
                    )

    Garaje.add_node("Marcador_D1",
                    attach_to = "Luz_Vehiculo_D1",
                    #mesh = Mesh_marcador,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Marcadores_Luz,
                    )

    
    Garaje.add_node("Cilindro_1", 
                    attach_to = "Plataforma_1",
                    mesh = Mesh_Cilindro, 
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Cromo,
                    transform = tr.scale(6, 0.15, 6)
                    )

    Garaje.add_node("Vehiculo_1",
                    attach_to = "Plataforma_1",
                    rotation = [0, - np.pi / 2, 0],
                    transform = tr.translate(0, 1.66, 0)
                    )
    
    Garaje.add_node("Chasis_1",
                    attach_to = "Vehiculo_1",
                    mesh = Mesh_Chasis,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Rubi,
                    )

    Garaje.add_node("Ventanas_1",
                    attach_to = "Vehiculo_1",
                    mesh = Mesh_Ventanas,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Ventanas,
                    )

    Garaje.add_node("Adornos_1",
                    attach_to = "Vehiculo_1",
                    mesh = Mesh_Adornos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Plata,
                    )

    Garaje.add_node("Focos_1",
                    attach_to = "Vehiculo_1",
                    mesh = Mesh_Focos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Focos,
                    )

    Garaje.add_node("Luz_Focos_1", 
                    attach_to = "Focos_1",
                    pipeline = Color_Mesh_Lit_Pipeline,
                    rotation = [0, np.pi / 2, 0],
                    position = [2, 0, 0],
                    light = SpotLight(
                            ambient = Color_Luz_Focos[0],
                            diffuse = Color_Luz_Focos[1], 
                            specular = Color_Luz_Focos[2], 
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
                    material = Material_Goma_Negra,
                    )
    
    Garaje.add_node("Rines_1",
                    attach_to = "Vehiculo_1",
                    mesh = Mesh_Rines,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Plata,
                    )

    ###############################################################################################################################################################
    #Segundo Vehiculo:

    Garaje.add_node("Plataforma_2",
                    transform = tr.translate(-12.99, 0, -7.5)
                    ) 

    Garaje.add_node("Luz_Vehiculo_A2", 
                    attach_to = "Plataforma_2",
                    pipeline = Color_Mesh_Lit_Pipeline, 
                    position = np.array([5, 5, 2.5]),
                    light = PointLight(
                            ambient = Color_Luces_Plataforma[0],
                            diffuse = Color_Luces_Plataforma[1], 
                            specular = Color_Luces_Plataforma[2], 
                            constant = 1,
                            linear = 0.14,
                            quadratic = 0.07,
                    )
                    )

    Garaje.add_node("Luz_Vehiculo_B2", 
                    attach_to = "Plataforma_2",
                    pipeline = Color_Mesh_Lit_Pipeline, 
                    position = np.array([5, 5, -2.5]),
                    light = PointLight(
                            ambient = Color_Luces_Plataforma[0],
                            diffuse = Color_Luces_Plataforma[1], 
                            specular = Color_Luces_Plataforma[2],
                            constant = 1,
                            linear = 0.12,
                            quadratic = 0.05,
                    )
                    )

    Garaje.add_node("Luz_Vehiculo_C2", 
                    attach_to = "Plataforma_2",
                    pipeline = Color_Mesh_Lit_Pipeline, 
                    position = np.array([-5, 5, 2.5]),
                    light = PointLight(
                            ambient = Color_Luces_Plataforma[0],
                            diffuse = Color_Luces_Plataforma[1], 
                            specular = Color_Luces_Plataforma[2], 
                            constant = 1,
                            linear = 0.12,
                            quadratic = 0.05,
                    )
                    )

    Garaje.add_node("Luz_Vehiculo_D2", 
                    attach_to = "Plataforma_2",
                    pipeline = Color_Mesh_Lit_Pipeline, 
                    position = np.array([-5, 5, -2.5]),
                    light = PointLight(
                            ambient = Color_Luces_Plataforma[0],
                            diffuse = Color_Luces_Plataforma[1], 
                            specular = Color_Luces_Plataforma[2], 
                            constant = 1,
                            linear = 0.12,
                            quadratic = 0.05,
                    )
                    )

    Garaje.add_node("Marcador_A2",
                    attach_to = "Luz_Vehiculo_A2",
                    #mesh = Mesh_marcador,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Marcadores_Luz,
                    )

    Garaje.add_node("Marcador_B2",
                    attach_to = "Luz_Vehiculo_B2",
                    #mesh = Mesh_marcador,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Marcadores_Luz,
                    )

    Garaje.add_node("Marcador_C2",
                    attach_to = "Luz_Vehiculo_C2",
                    #mesh = Mesh_marcador,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Marcadores_Luz,
                    )

    Garaje.add_node("Marcador_D2",
                    attach_to = "Luz_Vehiculo_D2",
                    #mesh = Mesh_marcador,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Marcadores_Luz,
                    )
    
    
    Garaje.add_node("Cilindro_2", 
                    attach_to = "Plataforma_2",
                    mesh = Mesh_Cilindro, 
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Cromo,
                    transform = tr.scale(6, 0.15, 6)
                    )

    Garaje.add_node("Vehiculo_2",
                    attach_to = "Plataforma_2",
                    rotation = [0,  5 * np.pi / 6, 0],
                    transform = tr.translate(0, 1.66, 0)
                    )
    
    Garaje.add_node("Chasis_2",
                    attach_to = "Vehiculo_2",
                    mesh = Mesh_Chasis,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Oro_Pulido,
                    )

    Garaje.add_node("Ventanas_2",
                    attach_to = "Vehiculo_2",
                    mesh = Mesh_Ventanas,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Ventanas,
                    )

    Garaje.add_node("Adornos_2",
                    attach_to = "Vehiculo_2",
                    mesh = Mesh_Adornos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Plata,
                    )

    Garaje.add_node("Focos_2",
                    attach_to = "Vehiculo_2",
                    mesh = Mesh_Focos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Focos,
                    )

    Garaje.add_node("Luz_Focos_2", 
                    attach_to = "Focos_2",
                    pipeline = Color_Mesh_Lit_Pipeline,
                    rotation = [0, np.pi / 2, 0],
                    position = [1.5, 0, 0],
                    light = SpotLight( 
                            ambient = Color_Luz_Focos[0],
                            diffuse = Color_Luz_Focos[1],
                            specular = Color_Luz_Focos[2], 
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
                    material = Material_Goma_Negra,
                    )
    
    Garaje.add_node("Rines_2",
                    attach_to = "Vehiculo_2",
                    mesh = Mesh_Rines,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Plata,
                    )

    ##############################################################################################################################################################
    #Tercer Vehiculo:

    Garaje.add_node("Plataforma_3",
                    transform = tr.translate(12.99, 0, -7.5) 
                    ) 

    Garaje.add_node("Luz_Vehiculo_A3", 
                    attach_to = "Plataforma_3",
                    pipeline = Color_Mesh_Lit_Pipeline, 
                    position = np.array([5, 5, 2.5]),
                    light = PointLight(
                            ambient = Color_Luces_Plataforma[0],
                            diffuse = Color_Luces_Plataforma[1], 
                            specular = Color_Luces_Plataforma[2],
                            constant = 1,
                            linear = 0.14,
                            quadratic = 0.07,
                    )
                    )

    Garaje.add_node("Luz_Vehiculo_B3", 
                    attach_to = "Plataforma_3",
                    pipeline = Color_Mesh_Lit_Pipeline, 
                    position = np.array([5, 5, -2.5]),
                    light = PointLight(
                            ambient = Color_Luces_Plataforma[0],
                            diffuse = Color_Luces_Plataforma[1], 
                            specular = Color_Luces_Plataforma[2],
                            constant = 1,
                            linear = 0.12,
                            quadratic = 0.05,
                    )
                    )

    Garaje.add_node("Luz_Vehiculo_C3", 
                    attach_to = "Plataforma_3",
                    pipeline = Color_Mesh_Lit_Pipeline, 
                    position = np.array([-5, 5, 2.5]),
                    light = PointLight(
                            ambient = Color_Luces_Plataforma[0],
                            diffuse = Color_Luces_Plataforma[1], 
                            specular = Color_Luces_Plataforma[2],
                            constant = 1,
                            linear = 0.12,
                            quadratic = 0.05,
                    )
                    )

    Garaje.add_node("Luz_Vehiculo_D3", 
                    attach_to = "Plataforma_3",
                    pipeline = Color_Mesh_Lit_Pipeline, 
                    position = np.array([-5, 5, -2.5]),
                    light = PointLight(
                            ambient = Color_Luces_Plataforma[0],
                            diffuse = Color_Luces_Plataforma[1], 
                            specular = Color_Luces_Plataforma[2],
                            constant = 1,
                            linear = 0.12,
                            quadratic = 0.05,
                    )
                    )

    Garaje.add_node("Marcador_A3",
                    attach_to = "Luz_Vehiculo_A3",
                    #mesh = Mesh_marcador,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Marcadores_Luz,
                    )

    Garaje.add_node("Marcador_B3",
                    attach_to = "Luz_Vehiculo_B3",
                    #mesh = Mesh_marcador,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Marcadores_Luz,
                    )

    Garaje.add_node("Marcador_C3",
                    attach_to = "Luz_Vehiculo_C3",
                    #mesh = Mesh_marcador,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Marcadores_Luz,
                    )

    Garaje.add_node("Marcador_D3",
                    attach_to = "Luz_Vehiculo_D3",
                    #mesh = Mesh_marcador,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Marcadores_Luz,
                    )
    
    
    Garaje.add_node("Cilindro_3", 
                    attach_to = "Plataforma_3",
                    mesh = Mesh_Cilindro, 
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Cromo,
                    transform = tr.scale(6, 0.15, 6)
                    )

    Garaje.add_node("Vehiculo_3",
                    attach_to = "Plataforma_3",
                    rotation = [0, np.pi / 6, 0],
                    transform = tr.translate(0, 1.66, 0)
                    )
    
    Garaje.add_node("Chasis_3",
                    attach_to = "Vehiculo_3",
                    mesh = Mesh_Chasis,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Esmeralda,
                    )

    Garaje.add_node("Ventanas_3",
                    attach_to = "Vehiculo_3",
                    mesh = Mesh_Ventanas,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Ventanas,
                    )

    Garaje.add_node("Adornos_3",
                    attach_to = "Vehiculo_3",
                    mesh = Mesh_Adornos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Plata,
                    )

    Garaje.add_node("Focos_3",
                    attach_to = "Vehiculo_3",
                    mesh = Mesh_Focos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Focos,
                    )

    Garaje.add_node("Luz_Focos_3", 
                    attach_to = "Focos_3",
                    pipeline = Color_Mesh_Lit_Pipeline,
                    rotation = [0, np.pi / 2, 0],
                    position = [1.5, 0, 0],
                    light = SpotLight(
                            ambient = Color_Luz_Focos[0],
                            diffuse = Color_Luz_Focos[1], 
                            specular = Color_Luz_Focos[2], 
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
                    material = Material_Goma_Negra,
                    )
    
    Garaje.add_node("Rines_3",
                    attach_to = "Vehiculo_3",
                    mesh = Mesh_Rines,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Plata,
                    )

###################################################################################################################################################################
#Logica de actualizacion:
    def Circunferencia(parametro):
        x = 15 * np.cos(parametro + (np.pi / 2))
        y = 0
        z = 15 * np.sin(parametro + (np.pi / 2))

        return np.array([x,y,z])
        
    
    def Mov_Suave(dt, offset_inicial, offset_final, offset_actual):
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
    
    def update(dt):
        camera = Ventana.program_state["camera"]
        Auto_1 = Garaje.__getitem__("Vehiculo_1")
        Auto_2 = Garaje.__getitem__("Vehiculo_2")
        Auto_3 = Garaje.__getitem__("Vehiculo_3")

        Ventana.program_state["Key_Cool_Down"] += dt

        if Ventana.program_state["Key_Cool_Down"] >= 10.0:
            Ventana.program_state["Key_Cool_Down"] = 0.01 #Para que el numero no se vaya a la cresta el valor xD

        if not Ventana.program_state["transicion"]:
            if Ventana.program_state["seleccion"] == 0:
                
                Auto_1["rotation"][1] += dt / 2
                Auto_2["rotation"][1] = 5 * np.pi / 6
                Auto_3["rotation"][1] = np.pi / 6 

                coseno = abs(2.3 * np.cos(Auto_1["rotation"][1] - np.pi / 2)) + 5

                if coseno <= 5.6:
                    coseno = 5.6

                if coseno >= 7.2:
                    coseno = 7.2
                
                camera.distancia = coseno

            elif Ventana.program_state["seleccion"] == 1:
                Auto_1["rotation"][1] = - np.pi / 2
                Auto_2["rotation"][1] += dt / 2
                Auto_3["rotation"][1] = np.pi / 6

                
                coseno = abs(2.3 * np.cos(Auto_2["rotation"][1] + np.pi / 6)) + 5

                if coseno <= 5.6:
                    coseno = 5.6

                if coseno >= 7.2:
                    coseno = 7.2
                
                camera.distancia = coseno
                

            else:
                Auto_1["rotation"][1] = - np.pi / 2
                Auto_2["rotation"][1] = - np.pi / 6
                Auto_3["rotation"][1] += dt / 2

                
                coseno = abs(2.3 * np.cos(Auto_3["rotation"][1] + 5 * np.pi / 6)) + 5

                if coseno <= 5.6:
                    coseno = 5.6

                if coseno >= 7.2:
                    coseno = 7.2
                
                camera.distancia = coseno
                

        if Ventana.is_key_pressed(pyglet.window.key.SPACE) and Ventana.program_state["Key_Cool_Down"] >= 0.5 and not Ventana.program_state["transicion"]:
            #Logica si se presiona el boton de cambio de vehiculo

            Ventana.program_state["seleccion"] += 1
            
            if Ventana.program_state["seleccion"] > 2:
                Ventana.program_state["seleccion"] = 0

            if Ventana.program_state["seleccion"] == 1:
                Ventana.program_state["Offset_Inicial"] = np.array([0, 0, 15])
                Ventana.program_state["Offset_Final"] = np.array([-12.99, 0, -7.5])

                Ventana.program_state["Parametro_Vista_Final"] = 2 / 3
                Ventana.program_state["Angulo_Final"] = 2 * np.pi / 3
                
        
            elif Ventana.program_state["seleccion"] == 2:
                Ventana.program_state["Offset_Inicial"] = np.array([-12.99, 0, -7.5])
                Ventana.program_state["Offset_Final"] = np.array([12.99, 0, -7.5])

                Ventana.program_state["Parametro_Vista_Final"] = 4 / 3
                Ventana.program_state["Angulo_Final"] =  4 * np.pi / 3
            

            else:
                Ventana.program_state["Offset_Inicial"] = np.array([12.99, 0, -7.5])
                Ventana.program_state["Offset_Final"] = np.array([0, 0, 15])

                Ventana.program_state["Parametro_Vista_Final"] = 2
                Ventana.program_state["Angulo_Final"] =  2 * np.pi 

            Ventana.program_state["Key_Cool_Down"] = 0

        ####################################################################################################################################################

        distancia_offsets = np.sqrt(np.square(Ventana.program_state["Offset_Final"][0] - Ventana.program_state["Offset_Actual"][0]) + np.square(Ventana.program_state["Offset_Final"][2] - Ventana.program_state["Offset_Actual"][2]))
        
        if distancia_offsets > 0.1:
        #Ejecutamos si la distancia entre el offset actual y el final es mayor a 0.1 (Es decir, debemos desplazarnos)
            
            Ventana.program_state["transicion"] = True
            
            if camera.distancia < 7.2:
                camera.distancia += dt
            else:
                camera.distancia = 7.2

            #Logica para mover suavemente el centro de la camara
            Ventana.program_state["Offset_Actual"] = Mov_Suave(dt, Ventana.program_state["Offset_Inicial"], 
                                                                            Ventana.program_state["Offset_Final"], 
                                                                            Ventana.program_state["Offset_Actual"],
                                                                        )
            
            camera.center_offset = Ventana.program_state["Offset_Actual"]

            #Logica para trasladar la camara de manera suave
            delta_parametro = Ventana.program_state["Parametro_Vista_Final"] - Ventana.program_state["Parametro_Vista_Actual"]

            if delta_parametro >= dt / 10000:
                Ventana.program_state["Parametro_Vista_Actual"] += dt / 3.5

            camera.focus = Circunferencia(Ventana.program_state["Parametro_Vista_Actual"] * np.pi)
            #camera.phi = Ventana.program_state["Parametro_Vista_Actual"]

            #Logica para ajustar el angulo de rotacion de la camara (phi):
            delta_angulo = Ventana.program_state["Angulo_Final"] - camera.phi

            if delta_angulo > 0.01:
                camera.phi -= - 0.728 * dt  #No cuadra al 100% pero es good enough, para hacerlo bien habria que interpolar


        else:
            Ventana.program_state["transicion"] = False
            camera.center_offset = Ventana.program_state["Offset_Final"]
            camera.phi = Ventana.program_state["Angulo_Final"]
            camera.focus = Ventana.program_state["Offset_Final"]


            if Ventana.program_state["seleccion"] == 0:
                Ventana.program_state["Parametro_Vista_Actual"] = 0
                camera.phi = 0
        
        #print(camera.distancia)
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
