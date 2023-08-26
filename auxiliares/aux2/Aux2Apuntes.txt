Apuntes AUX 3 Gráfica:
	
	OpenGL y Transformaciones:
		
		OpenGL es una API para interactuar con la GPU
		
		Pyglet abstrae openGL y permite manejar elementos de input y ventana
		
		Siempre hay un pipeline por detrás del proceso de graficado
		
			Se le pasa vertex y fragment shader.
			
			
Creación del pipeline: (En OpenGL)
	
	vert_shader = glCreateShader(GL_VERTEX_SHADER)   //Asigna espacio en memoria vacio para un shader, y devuelve el pointer.
	glShaderSource()
	...
	
	
En OpenGL hay que ser explícito paso a paso sobre lo que quiero hacer 

vao = glGenVertexArrays(1) //genero un VAO (Vertex array object, la lista de vertices, pero vacía)

glBindVertexArray(vao) //Lo selecciono

vbo = glGenBuffers(1) //genero un VBO (Vertex buffer object, la lista con los datos de los vertices)
glBindBuffer(GL_ARRAY_BUFFER,)




Cambiar los buffers es costoso, para definir variables que no cambian usamos Uniforms

			Uniform: Variable global para todas las ejecuciones del shader
			
				Se definen:  uniform [tipo] [Nombre]  en el codigo del shader.
				
				Se puede acceder a ellos desde el codigo de python tambien (Pyglet ayuda con esto.)
				
				
Transformaciones:
				
				*Traslacion: Suma de vectores
				
				Se hace en coordenadas homogeneas (con un 1 adicional en las coordenadas)
				
				*Rotaciones 2D y 3D 
				
				Las transformaciones se pueden concatenar, multiplicando sus matrices
				
				El orden importa, se hace con las matrices de derecha a izquierda.
				
				 
				  
				   
Como se usan las transformaciones en OpenGL?

 		En el vertex shader:
 				-Se crea uniform del tipo de matriz de 4x4 (mat4 en GLSL)
 				-Se multiplica la matriz por el punto.
 				
 		En python:
 				 -Se genera la matriz transformacion
 				 -Se pasan los datos al uniform
 				 
 				 
 				 
 El aux usa un ModelControler que es una clase que maneja los datos del modelo, sus propiedades y transformaciones.
 

 				 
				
				


