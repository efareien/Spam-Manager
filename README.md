# Spam Manager

## Descripción

Permite manejar la inserción o eliminación de dominios para un manejador de spam a través de la consola, brindado la capacidad de afectar ciertos usuarios en concreto, o bien, a todos excepto unos cuantos. Cada operación realizada es registrada mediante un archivo *log*. 

## Uso

### Agregar dominios

Para agregar un o más dominios, le debe indicar al programa el parámetro `--add` y complementarlo con los siguientes parámetros:

* `--whitelist ruta/del/whitelist`: Una ruta relativa o absoluta de dónde se encuentra el archivo que contiene los posibles dominios a **agregar a la lista blanca**. Tenga en cuenta que el programa no agregará dominios repetidos puesto que cuenta con una verificación previa de estos.
* `--blacklist ruta/del/blacklist`: Una ruta relativa o absoluta de dónde se encuentra el archivo que contiene los posibles dominios a **agregar a la lista negra**. Tenga en cuenta que el programa no agregará dominios repetidos por las mismas razones anteriormente mencionadas.

El programa debe recibir **al menos** uno de los dos parámetros indicados anteriormente. Usted puede agregar (si así lo desea) solo dominios a la lista blanca, solo dominios a la lista negra, o bien, a ambas.

Por ejemplo, si sólo se quiere **agregar** dominios a la lista blanca y suponiendo que se cuenta con un archivo en `/home/list/whitelist.txt` escribiríamos lo siguiente:

```bash
./spanager.py --add --whitelist /home/list/whitelist.txt
```

O bien, si nos encontramos en `/home/list/` simplemente escribimos

```bash
./spanager.py --add --whitelist whitelist.txt
```

Aunque en este ejemplo el archivo tenía extensión `.txt`, da lo mismo para efectos del programa, siempre y cuando sean caracteres del alfabeto anglosajón (¡y no instrucciones de máquina!)

Por otra parte, si sólo queremos **agregar** dominios a la lista negra y suponiendo que se cuenta con un archivo en `/home/list/blacklist.txt` escribiríamos lo siguiente:

```bash
./spanager.py --add --blacklist /home/list/blacklist.txt
```

Y finalmente, si se quiere realizar ambas operaciones considerando los archivos mencionados anteriormente, anotaríamos:

```bash
./spanager.py --add --whitelist /home/list/whitelist.txt --blacklist /home/list/blacklist.txt
```

### Eliminar dominios

Para eliminar uno o más dominios le indicamos al programa el parámetro `--remove` y lo complementamos con los siguientes parámetros:

* `--whitelist ruta/del/whitelist`: Una ruta relativa o absoluta de dónde se encuentra el archivo que contiene los posibles dominios a **eliminar de la lista blanca**. Tenga en cuenta que el programa no agregará dominios repetidos puesto que cuenta con una verificación previa de estos.
* `--blacklist ruta/del/blacklist`: Una ruta relativa o absoluta de dónde se encuentra el archivo que contiene los posibles dominios a **eliminar de la lista negra**. Tenga en cuenta que el programa no agregará dominios repetidos por las mismas razones anteriormente mencionadas.

El programa debe recibir **al menos** uno de los dos parámetros indicados anteriormente. Usted puede eliminar (si así lo desea) solo dominios de la lista blanca, solo dominios de la lista negra, o bien, de ambas.

Por ejemplo, si sólo se quiere **eliminar** dominios de la lista blanca y suponiendo que se cuenta con un archivo en `/home/list/whitelist.txt` escribiríamos lo siguiente:

```bash
./spanager.py --remove --whitelist /home/list/whitelist.txt
```

O bien, si nos encontramos en `/home/list/` simplemente escribimos

```bash
./spanager.py --remove --whitelist whitelist.txt
```

Como mencionamos una sección atrás, la extensión es irrelevante.

Por otra parte, si sólo queremos **eliminar** dominios de la lista negra y suponiendo que se cuenta con un archivo en `/home/list/blacklist.txt` escribiríamos lo siguiente:

```
./spanager.py --remove --blacklist /home/list/blacklist.txt
```

Y finalmente, si se quiere realizar ambas operaciones considerando los archivos mencionados anteriormente, anotaríamos:

```bash
./spanager.py --remove --whitelist /home/list/whitelist.txt --blacklist /home/list/blacklist.txt
```

### Permitir que solo unos usuarios sean afectados por los nuevos dominios a agregar

Para hacer que a unos usuarios en concreto solo les afecten los cambios a realizar tanto en su lista blanca como negra dejando al resto igual que antes, debemos agregar el parámetro `--allow` junto con la **ruta relativa** o **ruta absoluta** del archivo que contiene todos los usuarios deseados.

Por ejemplo, si sólo queremos actualizar la lista blanca y negra del usuario "franco", tendríamos en primer lugar un archivo de texto **arbitrariamente** llamado *allow.txt* con el siguiente contenido (recuerde que la extensión es irrelevante siempre y cuando cumpla el formato):

```
franco
```

Supongamos que se encuentra en otra carpeta llamada `/home/filters/`. Luego, deberíamos indicar dónde tenemos nuestra lista blanca y negra, en este caso, supongamos que tenemos ambos archivos en `/home/list/` llamados `whitelist.txt` y `blacklist.txt`. Para aplicar los efectos bastaría escribir:

```bash
./spanager.py --add --whitelist /home/list/whitelist.txt --blacklist /home/list/blacklist.txt --allow /home/filters/allow.txt
```

### Permitir que todos sean afectados por los nuevos dominios a agregar, excepto unos cuantos usuarios

Para hacer que todos los usuarios sean afectados por estos nuevos dominios a agregar tanto en la lista blanca como negra, **exceptuando** algunos usuarios, debemos agregar el parámetro `--deny` junto con la **ruta relativa** o **ruta absoluta** del archivo que contiene todo los usuarios no deseados.

Por ejemplo, si queremos actualizar la lista negra agregando dominios para todos los usuarios excepto para "priquelme" y "jcontreras", tendríamos en primer lugar un archivo de texto **arbitrariamente** llamado *deny.txt* con el siguiente contenido:

```
priquelme
jcontreras
```

Supongamos que este último se encuentra en una carpeta llamada `/home/filters/`. Luego, deberíamos indicar dónde tenemos nuestra lista negra, en este caso, supongamos que este archivo se encuentra en `/home/list/` llamada `blacklist.txt`. Para aplicar los cambios bastaría escribir:

```bash
./spanager.py --add --blacklist /home/list/blacklist.txt --deny /home/filters/deny.txt
```

### Agregar los dominios con un sólo comando

Si quiere agregar o eliminar dominios de la lista blanca y/o negra recuperando automáticamente los archivos y filtros, primero debe escribir qué quiere hacer, ya sea, `--add` o `--remove`, para luego anotar `--auto ruta/de/la/carpeta`. Esta ruta puede ser relativa o absoluta, y hace referencia a una carpeta que puede contener los siguientes archivos, eso sí, los nombres deben escribirse estrictamente como se mencionan a continuación:

* `whitelist`: Un archivo sin extensión que representa la lista blanca. Sigue los mismos formatos anteriormente mencionados.
* `blacklist`: Un archivo sin extensión que representa la lista negra. Sigue los mismos formatos anteriormente mencionados.
* `allow`: Un archivo sin extensión que representa los usuarios que serán afectados por los cambios en los dominios. Sigue los mismos formatos anteriormente mencionados.
* `deny`: Un archivo sin extensión que representa los usuarios que no serán afectados por los cambios en los dominios. Sigue los mismos formatos anteriormente mencionados.

Por ejemplo, supongamos que en el directorio `/home/lists` tenemos los siguientes archivos:

* `whitelist`:

  ```
  *@minvu.cl
  josecontreras@duoc.cl
  ```

  

* `blacklist`:

  ```
  *@gitlab.com
  *@tester.cl
  ```

* `allow`:

  ```
  jose
  ```

Si aplicamos el comando, actualizaría la lista blanca y negra de jose (siempre y cuando este exista en el sistema). En resumen anotaríamos:

```bash
./spanager.py --add --auto /home/lists/
```

Automáticamente el programa buscara todos los archivos con los nombres *whitelist*, *blacklist*, *allow* y *deny*. Como sólo existen tres de ellos, realiza los cambios pertinentes con esos archivos actuales.

### Formato para los archivos que contienen los dominios y usuarios

El programa basa sus inserciones y eliminaciones de **dominios** y **usuarios** usando archivos de texto. 

* Para los que **contienen dominios** (ya sea *whitelist* o *blacklist*) deben seguir el siguiente formato:

  ```
  *@dominio1
  *@dominio2
  ...
  dominio3
  dominio4
  ...
  ```

  Por ejemplo, un archivo que contiene los nuevos dominios a insertar en la lista blanca es

  ```
  *@imaco.cl
  josefuentes@minvu.cl
  ```

* Para los que **contienen usuarios** (ya sea para permitir o denegar cambios) deben seguir el siguiente formato:

  ```
  usuario1
  usuario2
  ...
  ```

  Por ejemplo, un archivo que contiene usuarios que no deben ser afectados por los cambios es:

  ```
  psanchez
  jcontreras
  ```

### Historial de cambios

El programa cuenta con un archivo *log* que registra cada cambio realizado en los dominios, los cuales siguen la estructura:

```
[TIPO_MENSAJE:QUIEN_MODIFICA:CUANDO_SE_MODIFICA] ACCION_REALIZADA
```

* `TIPO_MENSAJE`: Es *info* cuando se informan los dominios agregados a una lista concreta para un usuario concreto, o bien, *error* cuando las rutas de los archivos no existen, no se pueden abrir estos últimos o alguno de los usuarios no existe en el dominio.
* `QUIEN_MODIFICA`: Indica el usuario que realiza los cambios.
* `CUANDO_SE_MODIFICA`: Es una estampilla de tiempo de la acción concretada.
* `ACCION_REALIZADA`: Depende del `TIPO_MENSAJE`.
  * Cuando le antecede un *info* informa qué dominios se agregaron o eliminaron del usuario en concreto para ambas listas.
  * Cuando le antecede un *error* informa qué tipo de error surgió en la ejecución del programa. Para más detalles, revise la sección **Manejo de errores**.

### Configuración de parámetros iniciales

Si bien este programa fue desarrollado como un manejador de spam en concreto para la empresa *Imaco*, pueden surgir dificultades en las rutas de acceso a las listas blancas o negras, o bien, ante un cambio del directorio raíz del *software* que maneja estas listas. Estos cambios deben estar presentes en el directorio `config/parameters.config`, y deben seguir el siguiente formato:

```
parametro1=valor1
parametro2=valor2
...
```

No es necesario que estén estrictamente juntos el parámetro y el valor a la igualdad: perfectamente por estética puede escribir `parametro1 = valor1`.

Los parámetros permitidos y sus valores son:

* `source_path`: Parámetro que indica el directorio raíz donde se encuentran todos los usuarios que reciben los filtros del manejador de spam, y tiene como **valor una ruta absoluta**. Por defecto, se asume `/home/re000444/mail/imaco.cl/`.
* `whitelist_relative_path`: Parámetro que recibe como **valor la ruta relativa** respecto de `source_path` que se debe seguir desde la carpeta del usuario para encontrar la lista blanca. Por defecto, se asume la ruta relativa `/.spamassassin/whitelist`.
* `blacklist_relative_path`: Parámetro que recibe como **valor la ruta relativa** respecto de `source_path` que se debe seguir desde la carpeta del usuario para encontrar la **lista negra**. Por defecto, se asume la ruta relativa `/.spamassassin/blacklist`.
* `log_path`: Parámetro que recibe como **valor una ruta relativa o absoluta** que indica dónde se desea almacenar el *log*. Por defecto se asume `log/history.log`.
* `log_format`: Parámetro que indica cómo deben ser las salidas de los *logs*, vale decir, si se indica la fecha de modificación, quién realiza la modificación, entre otros aspectos, el cual recibe como valor una cadena que sigue los formatos de la librería *logging*. Por defecto es `[%(levelname)s:%(name)s:%(asctime)s]: %(message)s`.

Un archivo de ejemplo ubicado en la ruta por defecto, es decir, `config/parameters.config` sería:

```
source_path 			= C:\Users\user\Desktop\scripts\SpamManager\users\
whitelist_relative_path = \.spamassassin\whitelist
blacklist_relative_path = \.spamassassin\blacklist
```

### Manejo de errores

El programa cuenta con un moderado listado de errores frecuentes, entre ellos encontramos:

* No se indica ni el flag `--add` o `--remove`.
* Se indican ambos flags `--add` y `--remove` al mismo tiempo.
* No se indica ninguna ruta en los flags `--add`, `--remove`, `--allow` y/o `--deny`.
* Las rutas indicadas en los flags `--add` y `--remove` son erróneas.
* Los usuarios indicados en los flags `--allow` y `--deny` no existen.

### Recomendaciones

Sólo si es necesario configure el archivo `parameters.config`. También le recomendamos mantener ordenadas sus listas en alguna carpeta. Puede seguir la estructura que nosotros le proponemos, incluyendo sus listas en el directorio `lists` y creando para cada modificación una carpeta que siga el formato `mm/dd/aaaa hh:mm:ss`, en la que incluya todos los archivos que usted necesita: listas blancas, negras, usuarios permitidos y/o denegados. De esta forma usted puede usar el comando `--add` o `--remove` seguido de `--auto`, que automáticamente extraerá todos los archivos indicados en esta carpeta para agregar o remover directorios.

### Para python3 y posteriores
El proyecto originalmente fue desarrollado para python3 y se llama `spager3.py`. Prácticamente `spager.py` y `spager3.py` son lo mismo para los ojos del usuario, aunque internamente varía su sintáxis y hasta optimalidad, por lo tanto, todo el documento es perfectamente adaptable para este último script.
