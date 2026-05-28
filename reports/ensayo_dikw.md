# Jerarquia DIKW aplicada al analisis de plataformas de streaming

## Introduccion

Las plataformas de streaming manejan miles de titulos y necesitan entender cuales generan mayor audiencia. Sin embargo, tener muchos datos no garantiza buenas decisiones. Para que los datos realmente sirvan, tienen que pasar por un proceso de transformacion que los convierte primero en informacion, luego en conocimiento y finalmente en sabiduria. Este proceso se conoce como la jerarquia DIKW (por sus siglas en ingles: Data, Information, Knowledge, Wisdom). El sistema desarrollado en este proyecto aplica esa jerarquia al catalogo de contenido de diez plataformas de streaming, con el objetivo de predecir cuales titulos tendran exito comercial.

## El Dato

En la base de la jerarquia estan los datos crudos. En este caso, cada titulo registrado en el sistema tiene asociado un conjunto de hechos: el nombre, la plataforma en que esta disponible, el genero principal, el ano de lanzamiento, la clasificacion de contenido, el presupuesto estimado, los votos del publico en sitios de resenas y la cantidad de horas que fue visto. Por si solos, estos numeros y textos no dicen nada. Saber que un titulo tiene una calificacion de 7.2 o que fue lanzado en 2018 no permite tomar ninguna decision concreta. Son simplemente registros aislados que necesitan contexto para tener valor.

## La Informacion

Cuando los datos se limpian, se combinan y se organizan, se convierten en informacion. Por ejemplo, al agrupar los titulos por plataforma se puede calcular el promedio de calificacion de cada una, el porcentaje de titulos exitosos o la distribucion de generos disponibles. Un titulo con 7.2 de calificacion dentro de una plataforma donde el promedio es 6.5 ya tiene un significado diferente al mismo titulo en una plataforma donde el promedio es 8.0. Ese contexto es lo que transforma el dato en informacion. En este proyecto, esa etapa incluye la limpieza de registros incompletos, la creacion de variables derivadas como la antiguedad del titulo o el tamano del elenco, y la generacion de resumenes por plataforma, genero y pais.

## El Conocimiento

La informacion, cuando se analiza en conjunto, permite descubrir patrones. Ahi es donde entra el conocimiento. A traves de modelos de clasificacion y agrupacion, el sistema identifica que combinaciones de caracteristicas tienden a producir titulos con alta audiencia. Por ejemplo, se puede observar que ciertos generos en determinadas plataformas concentran mas horas vistas, o que los titulos con mayor numero de premios no siempre coinciden con los mas vistos. Estos patrones no son obvios mirando los datos uno por uno; emergen del analisis del conjunto completo. El conocimiento generado permite entender la logica detras del exito de un titulo, no solo describirlo.

## La Sabiduria

El nivel mas alto de la jerarquia ocurre cuando el conocimiento se usa para tomar decisiones. En este sistema, esa etapa se materializa en una herramienta interactiva donde es posible ingresar las caracteristicas de un titulo que aun no existe y obtener una estimacion de si tendra exito o no. Un productor de contenido o un ejecutivo de una plataforma puede usar esa herramienta para comparar opciones antes de invertir en una produccion. Ya no se trata de describir lo que paso, sino de orientar lo que va a pasar. Eso es sabiduria aplicada: usar lo aprendido para resolver el problema que dio origen al proyecto.

## Conclusion

El recorrido desde el dato crudo hasta la sabiduria no es automatico. Requiere decisions sobre como limpiar los datos, que variables construir, que modelos usar y como presentar los resultados. Cada etapa agrega una capa de significado que la anterior no tenia. Este proyecto demuestra que el valor de los datos no esta en la cantidad sino en el proceso que los transforma en algo util para quien toma decisiones.
