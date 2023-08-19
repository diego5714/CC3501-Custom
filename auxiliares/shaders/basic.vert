#version 330

in vec2 position;
in vec3 color;        //Definimos las variables de entrada (Los vertices que vienen de la CPU)
in float intensity;

out vec3 fragColor;
out float fragIntensity;   //Definimos parámetros de salida para la GPU

void main()
{
    fragColor = color;   //Pasamos el color como variable en la GPU al resto del pipeline
    fragIntensity = intensity;  //Pasamos la intensidad en GPU al pipeline
    gl_Position = vec4(position, 0.0f, 1.0f); //Seteamos la posición pero no la pasamos al resto del pipeline
}