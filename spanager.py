import logging
import argparse
import datetime
from copy import deepcopy
from tempfile import mkstemp
from os import fdopen, remove, walk
from shutil import move, copymode

"""
Configuraciones basicas para el archivo log
"""
logging.basicConfig(filename="history.log", level=logging.DEBUG, format='[%(levelname)s:%(name)s:%(asctime)s]: %(message)s')

class SpamManager:
    relative_paths = {
            "whitelist": '/.spamassassin/whitelist',
            "blacklist": '/.spamassassin/blacklist'
        }
    
    def __init__(self, source_path):
        self.source_path = source_path
        self.users = folders = next(walk(source_path))[1]
        
    """
    Permite almacenar todas las lineas de un archivo como elementos de una lista,
    saltandose todas aquellas que estan vacias.
    Parametros:
        - absolute_path: La ruta absoluta del archivo
    """
    @staticmethod
    def tokenize(absolute_path):
        result = []
        
        with open(absolute_path) as file:
            for line in file:
                line = line.strip()
                if line == '':
                    continue
                result.append(line)
                
        return result
    """
    Permite filtrar que usuarios seran afectados por los cambios hechos en la lista blanca y/o negra.
    Parametros:
        - users: La lista de usuarios que se pretende filtrar.
        - filter: Es un diccionario que puede contener las llaves "allow" y "deny", y junto a ello, las listas
        de todos los usuarios.
            -- Si "allow" esta presente, significa que solo los usuarios enlistados son afectados por los cambios.
            -- Si "deny" esta presente, significa que todos los usuarios seran afectados por los cambios, excepto
            los enlistados
    """
    @staticmethod
    def filter_as(users, filter):
        for key, domains in filter.items():
            if key not in ["allow", "deny"]:
                raise Exception("Llaves mal provistas en la funcion filter_as; Solo se permiten las siguientes: allow o deny.")

            if key == "allow":
                users = domains
            else:
                users = list( set(users).difference( set(domains) ))
                
        return users

    """
    Permite agregar nuevos dominios tanto para la lista blanca como negra de los usuarios, verificando
    si estos ya se encuentran presentes en las listas actuales; si ocurre una coincidencia, se lanza
    una excepcion y simplemente se elimina de los nuevos dominios a agregar. Note que el metodo puede
    agregar solo itemes a la lista blanca, negra o ambas.
    Parametros:
        - lists: Un diccionario que puede contener las llaves "whitelist" y "blacklist" junto las listas
        de todos los posibles dominios a agregar.
        - filter_as: Un diccionario que puede contener las llaves "allow" o "deny" junto con todos
        los dominios a filtrar.
            -- Si la llave es "allow", solo se agregaran los nuevos dominios a esos usuarios.
            -- Si la llave es "deny", se agregaran los dominios a todos los usuarios exceptos a los que
            indique el filtro de dominios.
    """
    def add(self, lists, filter = {}):
        users = SpamManager.filter_as(self.users, filter)
            
        for user in users:
            paths = {key: f"{self.source_path}{user}{SpamManager.relative_paths[key]}" for key in lists.keys()}

            for key, path in paths.items():
                temporal_lists = deepcopy(lists)
                last_line_character = ''
                
                with open(path, 'r+') as file:          
                    for domain in file:
                        last_line_character = domain[-1]
                        domain = domain.strip()
                        
                        if domain == '':
                            continue
                        
                        try:
                            if domain in temporal_lists[key]:
                                raise Exception(f'El dominio {domain} en la lista {key} ya existe en el usuario {user}')
                        except Exception as error:
                            temporal_lists[key].remove(domain)
                            print(error)
                            logging.warning(error)

                with open(path, 'a+') as file:
                    prepend = ''
                    domains_concat_by_commas = ', '.join(temporal_lists[key]) if len(temporal_lists[key]) > 0 else 'Ninguno'
                    domains_concat_by_breaklines = '\n'.join(temporal_lists[key])
                    
                    if len(temporal_lists[key]) != 0 and last_line_character != '\n':
                        prepend = '\n'
                        
                    file.write(prepend + domains_concat_by_breaklines)
                    print(f"Dominios agregados al usuario {user} en la lista {key}: {domains_concat_by_commas}")
                    logging.info(f"Dominios agregados al usuario {user} en la lista {key}: {domains_concat_by_commas}")

    """
    Permite eliminar dominios de la lista blanca y negra de los usuarios. Note que el metodo puede hacerlo solo para
    itemes de la lista blanca, negra o ambos.
    Parametros:
        - Undesirables: Diccionario que puede contener las llaves "whitelist" y "blacklist" junto con una lista de todos
        los posibles dominios a eliminar.
        - Filter: Un diccionario que puede contener las llaves "allow" o "deny" junto con todos
        los dominios a filtrar.
            -- Si la llave es "allow", solo se agregaran los nuevos dominios a esos usuarios.
            -- Si la llave es "deny", se agregaran los dominios a todos los usuarios exceptos a los que
            indique el filtro de dominios.
    """
    def remove(self, undesirables, filter = {}):
        users = SpamManager.filter_as(self.users, filter)

        for user in users:
            paths = {key: f"{self.source_path}{user}{SpamManager.relative_paths[key]}" for key in undesirables.keys()}
            
            for key, path in paths.items():
                temporal_file, absolute_temporal_file_path = mkstemp()
                stragglers = []
                
                with fdopen(temporal_file, 'w') as new_file:
                    with open(path) as old_file:
                        for domain in old_file:
                            domain = domain.strip()
                            
                            if domain == '':
                                continue
                            
                            if domain not in undesirables[key]:
                                new_file.write(f'{domain}\n')
                            else:
                                stragglers.append(domain)
                                
                copymode(path, absolute_temporal_file_path)
                remove(path)
                move(absolute_temporal_file_path, path)

                stragglers_concat_by_commas = ', '.join(stragglers) if len(stragglers) > 0 else 'Ninguno'
                
                print(f"Dominios eliminados al usuario {user}de la lista {key}: {stragglers_concat_by_commas}")
                logging.info(f"Dominios eliminados al usuario {user}de la lista {key}: {stragglers_concat_by_commas}")

"""
Se definen todos los parametros para ser ejectuado el script en consola: add, remove, whitelist, blacklist, allow y deny.
    - add: Es un booleano que indica si la accion principal es agregar dominios a la lista negra y/o blanca.
    remove: Es un booleano que indica si la accion principal es eliminar dominios de la lista negra y/o blanca.
    whitelist: Ruta del archivo que contiene todos los dominios a agregar. Siguen el formato:
        *@dominio1
        *@dominio2
        ...
        dominiok
        dominiok+1
        ...
    - blacklist: Ruta del archivo que contiene todos los dominios a agregar. Sigue el formato:
        *@dominio1
        *@dominio2
        ...
        dominiok
        dominiok+1
        ...
    - allow: Ruta del archivo que contiene todos los usuarios que seran afectados por los cambios. Sigue el formato:
        usuario1
        usuario2
        ...
    - deny: Ruta del archivo que contiene todos los usuarios que NO seran afectados por los cambios. Sigue el formato:
        usuario1
        usuario2
        ...
    Note que no esta permitido tener los flags add y remove activos al mismo tiempo.
"""
parser = argparse.ArgumentParser()

parser.add_argument("--add",
                    help="Permite agregar dominios a la lista blanca y/o negra.",
                    action="store_true")
parser.add_argument("--remove",
                    help="Permite eliminar dominios de la lista blanca y/o negra",
                    action="store_true")
parser.add_argument("--whitelist",
                    default="",
                    type=str,
                    help="La ruta absoluta del archivo que contiene todos los dominios que se desean agregar a la lista blanca. Estos deben estar separados por un un salto de linea y pueden ser de la forma '*@dominio', o bien, 'dominio' (sin comillas).")
parser.add_argument("--blacklist",
                    default="",
                    type=str,
                    help="La ruta absoluta del archivo que contiene todos los dominios que se desean agregar a la lista negra. Estos deben estar separados por un un salto de linea y pueden ser de la forma '*@dominio', o bien, 'dominio' (sin comillas).")
parser.add_argument("--allow",
                    type=str,
                    default="",
                    help="La ruta absoluta del archivo que contiene todos los usuarios a los que se desea aplicar estos nuevos dominios. Todos estos deben estar separados por un salto de linea.")
parser.add_argument("--deny",
                    type=str,
                    default="",
                    help="La ruta absoluta del archivo que contiene todos los usuarios a los que no se desea aplicar estos nuevos dominios. Todos estos deben estar separados por un salto de linea.")

args = parser.parse_args()

"""
Se transforman a una lista todos los archivos provistos en las rutas.
"""
list_filenames = {"whitelist": args.whitelist, "blacklist": args.blacklist}
filter_filenames = {"allow": args.allow, "deny": args.deny}

not_empty_filenames = {key: filename for (key, filename) in list_filenames.items() if filename != ""}
not_empty_filters = {key: filename for (key, filename) in filter_filenames.items() if filename != ""}
    
lists = {}
filters = {}

"""
Se elige la accion de acuerdo al parametro provisto en la consola. En caso de que uno de los archivos no exista,
se genera una excepcion y no se realiza nada.
"""
try:
    for key, filename in not_empty_filenames.items():
        lists[key] = SpamManager.tokenize(filename)

    for key, filename in not_empty_filters.items():
        filters[key] = SpamManager.tokenize(filename)
    
    source_path = '/home/re000444/mail/imaco.cl/'
    manager = SpamManager(source_path)

    if not args.add and not args.remove:
        raise Exception("Asegurese de indicar los flags correspondientes.")
    if args.add and args.remove:
        raise Exception("Solo se permite agregar o remover dominios a la lista blanca y/o negra, pero no ambas opciones al mismo tiempo.")
    if args.add and args.whitelist == "" and args.blacklist == "" or \
       args.remove and args.whitelist == "" and args.blacklist == "":
        raise Exception("No se esta indicando ningun archivo para el cual agregar/remover dominios en la lista blanca o negra")

    if args.add:
        manager.add(lists, filters)
    elif args.remove:
        manager.remove(lists, filters)
        
except FileNotFoundError:
    error = "Una o muchas rutas de los archivos son invalidas, o bien, alguno de los usuarios que se desea filtrar no existe."
    parser.error(error)
    logging.error(error)
except Exception as error:
    parser.error(error)
    logging.error(error)
