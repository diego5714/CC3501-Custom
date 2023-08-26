#version 330

in vec3 fragColor;
in float fragIntensity; //Definimos las variables que recibimos y devolvemos.
out vec4 outColor;

void main()
{
    outColor = fragIntensity * vec4(fragColor, 1.0f); //Aplicamos la intensidad sobre el vector de color (4 coordenadas, la 4ta es la transparencia)
}