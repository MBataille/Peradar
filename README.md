# pera-over-9000
Tienes mucha pera y cada 5 minutos te metes a reclamos dim? No esperes más! Instala Pera Over 9000 (PO9), relajate y espera que una canción a elección te diga como te fue! 
# Instalación
Para correr PO9 necesitas python 2.7 y los módulos BeautifulSoup, Mechanize y Pygame. En esta sección se asumirá que tienes python 2.7 y se explicará cómo instalar los módulos mencionados
## Windows
~~1. Instala Ubuntu y mira la siguiente sección~~
1. Descargar PyPi (pip). Sigue las instrucciones [acá](https://pip.pypa.io/en/stable/installing/). Se recomienda ver [este video](https://www.youtube.com/watch?v=zPMr0lEMqpo) que explica todo paso a paso.
1. Instalar BeautifulSoup. Abre la consola (CMD) y escribe:
    '''
    python -m pip install BeautifulSoup
    '''
1. Instalar Mechanize. Repite el paso anterior con:
    '''
    python -m pip install mechanize
    '''
1. Instalar Pygame. Repite el paso anterior con:
    '''
    python -m pip install pygame
    '''
1. Descargar PO9. Descarga el contenido de este repositorio

## OS X y Linux
1. Descargar Pypi (pip). Puedes verificar si ya lo tienes abriendo la consola y escribiendo *pip*. Para descargarlo, sigue las instrucciones [acá](https://pip.pypa.io/en/stable/installing/).
1. Instalar BeautifulSoup. Abre la consola y escribe:
    '''
    pip install BeautifulSoup
    '''
1. Instalar Mechanize. Repite el paso anterior con:
   '''
   pip install mechanize
   '''
1. Instalar Pygame. Repite el paso anterior con:
    '''
    pip install pygame
    '''
1. Descargar PO9. Descarga el contenido de este repositorio
   
# Agregar tus datos

El último paso es agregar tus datos y personalizar el programa! Para esto, edita el archivo run.py siguiendo estas instrucciones:

* Usuario y Contraseña: agrega tu usuario y contraseña de u pasaporte al lado de USERNAME y PASSWORD. No tengas miedo, leyendo el resto del código puedes verificar que esos datos solo se usan para acceder a reclamos, nunca se envían a terceros.
* Control: escribe el código del control que quieres ver, C1 para Control 1, C2 para Control 2, EX para examen, etc
* Preguntas: la cantidad de preguntas del control (por defecto es 3)
* R1 y R2: En el contexto de examen, bajo R1 repruebas, entre R1 y R2 tienes que dar examen de segunda y sobre R2 pasas el ramo. Notar que R1 cambia dependiendo de tu ramo, por lo tanto hay un elemento por ramo. Entonces, dependiendo de dónde se encuentra tu nota respecto a R1 y R2, se reproducirá una canción distinta
* Ramos: Los ramos que tienes (por defecto, cálculo y álgebra).
* Musica: Nombre de las canciones a reproducir siguiendo la posición de tu nota respecto a R1 y R2.
* Start: Segundo en el que quieres que comience cada canción

# Todo  listo!
Solo te queda ejecutar el programa, o sea, correr run.py (ya sea con doble click o *python run.py*) y esperar hasta que escuches la canción!
