#Libreria con la implementacion del grafo de escena de la pista de carreras.

import pyglet
from OpenGL import GL
import numpy as np
import sys
import trimesh as tm
from trimesh.scene.scene import Scene
from Box2D import b2PolygonShape, b2World

if sys.path[0] != "":
    sys.path.insert(0, "")
sys.path.append('../')

import grafica.transformations as tr
import auxiliares.utils.shapes as shapes
from auxiliares.utils.camera import Camera, FreeCamera
from auxiliares.utils.scene_graph import SceneGraph
from auxiliares.utils.drawables import Model, Texture, DirectionalLight, PointLight, SpotLight, Material
from auxiliares.utils.helpers import init_axis, init_pipeline, mesh_from_file, get_path

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

#Cargamos los archivos de shader y e inicializamos el pipeline
Color_Mesh_Lit_Pipeline = init_pipeline(
    get_path("auxiliares/shaders/color_mesh_lit.vert"),
    get_path("auxiliares/shaders/color_mesh_lit.frag"))

Textured_Mesh_Lit_Pipeline = init_pipeline(
        get_path("auxiliares/shaders/textured_mesh_lit.vert"),
        get_path("auxiliares/shaders/textured_mesh_lit.frag"))

#Modelos

Mesh_Cilindro = mesh_from_file_custom("Tarea-3/Models/Cilindro(Radio = 1, Altura = 2, Centrado).stl", escalar = False)[0]["mesh"]

Mesh_Chasis = mesh_from_file_custom("Tarea-3/Models/Chevrolet_Camaro_SS_Chasis.stl", escalar = False)[0]["mesh"]
Mesh_Ventanas = mesh_from_file_custom("Tarea-3/Models/Chevrolet_Camaro_SS_Ventanas.stl", escalar = False)[0]["mesh"]
Mesh_Adornos = mesh_from_file_custom("Tarea-3/Models/Chevrolet_Camaro_SS_Adornos_Metalicos.stl", escalar = False)[0]["mesh"]
Mesh_Focos = mesh_from_file_custom("Tarea-3/Models/Chevrolet_Camaro_SS_Focos_Delanteros.stl", escalar = False)[0]["mesh"]
    
Mesh_Neumaticos = mesh_from_file_custom("Tarea-3/Models/Chevrolet_Camaro_SS_Neumaticos.stl", escalar = False)[0]["mesh"]
Mesh_Rines = mesh_from_file_custom("Tarea-3/Models/Chevrolet_Camaro_SS_Rines.stl", escalar = False)[0]["mesh"]

Cubo = Model(shapes.Cube["position"], shapes.Cube["uv"], shapes.Cube["normal"], index_data=shapes.Cube["indices"])

#Materiales

Color_Material_Cromo = np.array([np.array([0.25, 0.25, 0.25]), np.array([0.4, 0.4, 0.4]), np.array([0.774597, 0.774597, 0.774597])])
Color_Material_Goma_Negra = np.array([np.array([0.02, 0.02, 0.02]), np.array([0.01, 0.01, 0.01]), np.array([0.4, 0.4, 0.4])])
Color_Material_Oro_Pulido = np.array([np.array([0.24725, 0.2245, 0.0645]), np.array([0.77, 0.70, 0.22]), np.array([0.797357, 0.723991, 0.208006])])
Color_Material_Rubi = np.array([np.array([0.1745, 0.01175, 0.01175]), np.array([0.61424, 0.04136, 0.04136]), np.array([0.727811, 0.626959, 0.626959])])
Color_Material_Esmeralda = np.array([np.array([0.0215, 0.1745, 0.0215]), np.array([0.07568, 0.61424, 0.07568]), np.array([0.633, 0.727811, 0.633])])
Color_Material_ventanas = np.array([np.array([0.1, 0.1, 0.1]), np.array([0.016, 0.8, 0.941]), np.array([0.116, 0.9, 1])])
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
Material_ventanas = Material(Color_Material_ventanas[0], Color_Material_ventanas[1], Color_Material_ventanas[2], 8)
Material_Plata = Material(Color_Material_Plata[0], Color_Material_Plata[1], Color_Material_Plata[2], 51.2)

#Texturas:

textura_pista = Texture("Tarea-3/Textures/pista.jpg", maxFilterMode = GL.GL_NEAREST) #Textura de la pista.

#Grafo de escena

def crear_pista(ventana):

    #Parte grafica

    pista = SceneGraph(ventana)

    pista.add_node("Luz_global",
                pipeline = [Color_Mesh_Lit_Pipeline, Textured_Mesh_Lit_Pipeline],
                rotation = np.array([-np.pi / 4, 0, 0]),
                position = np.array([0, 4, 0]),
                light = DirectionalLight(
                        ambient = np.array([0.2, 0.2, 0.2]),
                        diffuse = np.array([1, 1, 1]),
                        specular = np.array([0.5, 0.5, 0.5])
                        ),
                )

    pista.add_node("pista",
                   mesh = Cubo,
                   position = np.array([0, -0.5, 0]),
                   transform = tr.scale(200, 1, 200),
                   pipeline = Textured_Mesh_Lit_Pipeline,
                   texture = textura_pista,
                   material = Material(
                          diffuse = [1, 1, 1],
                          specular = [1, 1, 1],
                          ambient = [0.1, 0.1, 0.1],
                          shininess = 128
                     ))

    
    pista.add_node("Vehiculo",
                    rotation = [0, np.pi, 0],
                    transform = tr.translate(0, 1.66, 0)
                    )

    #######################################################

    if ventana.program_state["seleccion"] == 0:
        pista.add_node("Chasis",
                        attach_to = "Vehiculo",
                        mesh = Mesh_Chasis,
                        pipeline = Color_Mesh_Lit_Pipeline,
                        material = Material_Rubi,
                        )

    elif ventana.program_state["seleccion"] == 1:
        pista.add_node("Chasis",
                        attach_to = "Vehiculo",
                        mesh = Mesh_Chasis,
                        pipeline = Color_Mesh_Lit_Pipeline,
                        material = Material_Oro_Pulido,
                        )

    else:
        pista.add_node("Chasis",
                        attach_to = "Vehiculo",
                        mesh = Mesh_Chasis,
                        pipeline = Color_Mesh_Lit_Pipeline,
                        material = Material_Esmeralda,
                        )

    ########################################################

    pista.add_node("ventanas",
                    attach_to = "Vehiculo",
                    mesh = Mesh_Ventanas,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_ventanas,
                    )

    pista.add_node("Adornos_1",
                    attach_to = "Vehiculo",
                    mesh = Mesh_Adornos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Plata,
                    )

    pista.add_node("Focos",
                    attach_to = "Vehiculo",
                    mesh = Mesh_Focos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Focos,
                    )

    pista.add_node("Luz_Focos", 
                    attach_to = "Focos",
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

    pista.add_node("Neumaticos",
                    attach_to = "Vehiculo",
                    mesh = Mesh_Neumaticos,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Goma_Negra,
                    )
    
    pista.add_node("Rines",
                    attach_to = "Vehiculo",
                    mesh = Mesh_Rines,
                    pipeline = Color_Mesh_Lit_Pipeline,
                    material = Material_Plata,
                    )

    ################################################################################
    #Parte fisica:

    world = b2World(gravity=(0, 0))

    #Cuerpos dinamicos
    vehicle_body = world.CreateDynamicBody(position=(10, -8.5))
    vehicle_body.CreatePolygonFixture(box=(4, 2.7), density=2, friction=100)
    vehicle_body.linearDamping = 1.1
    vehicle_body.angularDamping = 1.1
    
    #Objetos estaticos:
    wall1_body = world.CreateStaticBody(position=(-101, 0))
    wall1_body.CreatePolygonFixture(box=(0.5, 100), density=1, friction=1)

    wall2_body = world.CreateStaticBody(position=(101, 0))
    wall2_body.CreatePolygonFixture(box=(0.5, 100), density=1, friction=1)

    wall3_body = world.CreateStaticBody(position=(0, -101))
    wall3_body.CreatePolygonFixture(box=(100, 0.5), density=1, friction=1)

    wall4_body = world.CreateStaticBody(position=(0, 101))
    wall4_body.CreatePolygonFixture(box=(100, 0.5), density=1, friction=1)
    
    #Objetos dinamicos
    ventana.program_state["physics_world"] = world
    ventana.program_state["bodies"]["Vehiculo"] = vehicle_body

    return pista


#Funcion de actualizacion de fisicas (Se llama desde el update general)
def update_physics(dt, ventana):
    world = ventana.program_state["physics_world"]
    world.Step(
        dt, ventana.program_state["vel_iters"], ventana.program_state["pos_iters"]
    )
    
    world.ClearForces()

#Funcion update especifica para esta escena
def update_pista(dt, ventana, pista):
    # Actualización física del vehiculo
    vehicle_body = ventana.program_state["bodies"]["Vehiculo"]
    pista["Vehiculo"]["transform"] = tr.translate(vehicle_body.position[0], 2, vehicle_body.position[1]) @ tr.rotationY(-vehicle_body.angle)

    # Modificar la fuerza y el torque del vehicle con las teclas
    vehicle_forward = np.array([1500 * np.sin(-vehicle_body.angle + np.pi / 2), 2, 1500 * np.cos(-vehicle_body.angle + np.pi / 2)])
    
    if ventana.is_key_pressed(pyglet.window.key.A):
        vehicle_body.ApplyTorque(-1000, True)
    
    if ventana.is_key_pressed(pyglet.window.key.D):
        vehicle_body.ApplyTorque(1000, True)
    
    if ventana.is_key_pressed(pyglet.window.key.W):
        vehicle_body.ApplyForce((vehicle_forward[0], vehicle_forward[2]), vehicle_body.worldCenter, True)
    
    if ventana.is_key_pressed(pyglet.window.key.S):
        vehicle_body.ApplyForce((-vehicle_forward[0], -vehicle_forward[2]), vehicle_body.worldCenter, True)

    #Actualizacion de la camara
    camera = ventana.program_state["camera"]

    if ventana.program_state["current_camera"] == 0:

        camera.center_offset = [vehicle_body.position[0], 2, vehicle_body.position[1]]
        camera.focus = [vehicle_body.position[0], 2, vehicle_body.position[1]]
        camera.phi = vehicle_body.angle + np.pi / 2
        camera.distance = 10

    else:
        camera.center_offset = [vehicle_body.position[0], 2, vehicle_body.position[1]]
        camera.focus = [vehicle_body.position[0], 2, vehicle_body.position[1]]
    
    camera.update()
    update_physics(dt, ventana)