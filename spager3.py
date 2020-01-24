import logging
import argparse
import re
from copy import deepcopy
from tempfile import mkstemp
from os import fdopen, remove, walk, listdir
from shutil import move, copymode

class ParameterManager:
    format = r'^([a-zA-Z_]+)\s*\=\s*([^\s]+)$'
    valid_parameters = ["source_path", "whitelist_relative_path", "blacklist_relative_path", "log_path", "log_format"]
    splitted_parameters = {
        "whitelist_relative_path": {"key": "relative_paths", "subkey": "whitelist"},
        "blacklist_relative_path": {"key": "relative_paths", "subkey": "blacklist"}
        }

    """
    Permite obtener todos los parametros del archivo de configuracion presentes en la ruta
    `config/parameters.config` que seran usados como referencia para agregar o eliminar dominios.
    """
    @staticmethod
    def get_parameters(source):
        parameters = {
            "source_path": '/home/re000444/mail/imaco.cl/',
            "relative_paths": {
                "whitelist": '/.spamassassin/whitelist',
                "blacklist": '/.spamassassin/blacklist'
            },
            "log_path": "log/history.log",
            "log_format": "[%(levelname)s:%(name)s:%(asctime)s]: %(message)s"
        }
        
        with open(source) as file:
            for parameter in file:
                parameter = parameter.strip()

                if parameter == '':
                    continue

                tokenized_parameter = re.match(ParameterManager.format, parameter)

                if not tokenized_parameter:
                    raise Exception("La configuracion presenta problemas en la sintaxis. Asegurese de escribir en cada linea el formato PARAMETRO=VALOR.")

                tokenized_parameter = {"name": tokenized_parameter.groups()[0], "value": tokenized_parameter.groups()[1]}

                if tokenized_parameter["name"] not in ParameterManager.valid_parameters:
                    raise Exception(f"El parametro {tokenized_parameter['name']} no existe, solo son validos los siguientes: {ParameterManager.valid_parameters}")
                
                if tokenized_parameter["name"] in ParameterManager.splitted_parameters.keys():
                    key = ParameterManager.splitted_parameters[tokenized_parameter["name"]]["key"]
                    subkey = ParameterManager.splitted_parameters[tokenized_parameter["name"]]["subkey"]
                    parameters[key][subkey] = tokenized_parameter["value"]
                else:
                    parameters[tokenized_parameter["name"]] = tokenized_parameter["value"]
                
        return parameters

class SpamManager:
    parameters = ParameterManager.get_parameters("config/parameters.config")
    logging_functions = {"info": logging.info, "warning": logging.warning, "error": logging.error}

    def __init__(self):
        logging.basicConfig(
            filename = SpamManager.parameters["log_path"],
            format = SpamManager.parameters["log_format"],
            level = logging.DEBUG)
        self.users = next(walk(SpamManager.parameters["source_path"]))[1]

    """
    Permite registrar en el archivo log un mensaje de cierto tipo, ya sea warning, error o info.
    """
    @staticmethod
    def log_and_print(message, kind):
        SpamManager.logging_functions[kind](message)
        print(message)
    
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

            users, domains = set(users), set(domains)

            """
            Simula un left join que excluye cualquier elemento del lado derecho, es decir, obtenemos los elementos que no están
            presentes en el lado derecho para asi ver si estamos tratando con un usuario que no existe.
            """
            if len(domains) != len(users.intersection(domains)):
                raise Exception("Uno o más usuarios que trata de filtrar no existen dentro del dominio.")
            
            if key == "allow":
                users = list(domains)
            else:
                users = list(users.difference(domains))
                
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
            paths = {key: f"{SpamManager.parameters['source_path']}{user}{SpamManager.parameters['relative_paths'][key]}" for key in lists.keys()}
            inserted_domains = {key: deepcopy(lists[key]) for key in ["whitelist", "blacklist"]}
            repeated_domains = {key: [] for key in ["whitelist", "blacklist"]}

            for key, path in paths.items():
                last_line_character = ''
                
                with open(path, 'r+') as file:          
                    for domain in file:
                        last_line_character = domain[-1]
                        domain = domain.strip()
                        
                        if domain == '':
                            continue

                        if domain in inserted_domains[key]:
                            inserted_domains[key].remove(domain)
                            repeated_domains[key].append(domain)
                
                with open(path, 'a+') as file:
                    prepend = ''
                    domains_concat_by_breaklines = '\n'.join(inserted_domains[key])
                    
                    if len(inserted_domains[key]) != 0 and last_line_character != '\n':
                        prepend = '\n'
                        
                    file.write(prepend + domains_concat_by_breaklines)

            summary = f'Usuario: {user}\n'
            
            for key in ["whitelist", "blacklist"]:
                summary += f"\tLista: {key}\n"
                summary += f"\t\tAgregados: {inserted_domains[key]}\n"
                summary += f"\t\tRepetidos: {repeated_domains[key]}\n"

            SpamManager.log_and_print(summary, "info")

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
            paths = {key: f"{SpamManager.parameters['source_path']}{user}{SpamManager.parameters['relative_paths'][key]}" for key in undesirables.keys()}
            dropped_domains = {"whitelist": [], "blacklist": []}
            
            for key, path in paths.items():
                temporal_file, absolute_temporal_file_path = mkstemp()
                
                with fdopen(temporal_file, 'w') as new_file:
                    with open(path) as old_file:
                        for domain in old_file:
                            domain = domain.strip()
                            
                            if domain == '':
                                continue
                            
                            if domain not in undesirables[key]:
                                new_file.write(f'{domain}\n')
                            else:
                                dropped_domains[key].append(domain)
                                
                copymode(path, absolute_temporal_file_path)
                remove(path)
                move(absolute_temporal_file_path, path)

            summary = f'Usuario: {user}\n'

            for key in ["whitelist", "blacklist"]:
                summary += f'\tLista: {key}\n'
                summary += f'\t\tEliminados: {dropped_domains[key]}\n'

            SpamManager.log_and_print(summary, "info")

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
                    help="La ruta absoluta o relativa del archivo que contiene todos los dominios que se desean agregar a la lista blanca. Estos deben estar separados por un un salto de linea y pueden ser de la forma '*@dominio', o bien, 'dominio' (sin comillas).")
parser.add_argument("--blacklist",
                    default="",
                    type=str,
                    help="La ruta absoluta o relativa del archivo que contiene todos los dominios que se desean agregar a la lista negra. Estos deben estar separados por un un salto de linea y pueden ser de la forma '*@dominio', o bien, 'dominio' (sin comillas).")
parser.add_argument("--allow",
                    type=str,
                    default="",
                    help="La ruta absoluta o relativa del archivo que contiene todos los usuarios a los que se desea aplicar estos nuevos dominios. Todos estos deben estar separados por un salto de linea.")
parser.add_argument("--deny",
                    type=str,
                    default="",
                    help="La ruta absoluta o relativa del archivo que contiene todos los usuarios a los que no se desea aplicar estos nuevos dominios. Todos estos deben estar separados por un salto de linea.")
parser.add_argument("--auto",
                    type=str,
                    default="",
                    help="Permite asociar automáticamente la lista blanca, negra, los usuarios denegados y/o permitidos y ejecutar la actualización de dominios. Como parámetro debe ser una una ruta relativa o absoluta de la carpeta que tenga todos los archivos anteriormente mencionados. Estos deben llamarse estrictamente whitelist, blacklist, deny y allow.")

args = parser.parse_args()

"""
Se elige la accion de acuerdo al parametro provisto en la consola. En caso de que uno de los archivos no exista,
se genera una excepcion y no se realiza nada.
"""
try:
    if not args.add and not args.remove:
        raise Exception("Asegurese de indicar los flags correspondientes.")
    if args.add and args.remove:
        raise Exception("Solo se permite agregar o remover dominios a la lista blanca y/o negra, pero no ambas opciones al mismo tiempo.")
    if args.auto == "" and args.whitelist == "" and args.blacklist == "":
        raise Exception("No se esta indicando ningun archivo para el cual agregar/remover dominios en la lista blanca o negra")
    if args.whitelist or args.blacklist or args.allow or args.deny:
        raise Exception("No puede usar los parámetros whitelist, blacklist, allow o deny cuando el parámetro auto está activo.")

    list_filenames = {"whitelist": args.whitelist, "blacklist": args.blacklist}
    filter_filenames = {"allow": args.allow, "deny": args.deny}

    not_empty_filenames = {key: filename for (key, filename) in list_filenames.items() if filename != ""}
    not_empty_filters = {key: filename for (key, filename) in filter_filenames.items() if filename != ""}
        
    lists = {}
    filters = {}

    manager = SpamManager()

    """
    Cuando el parametro auto esta activado, se tomaran todos los archivos con nombres 
    """
    if args.auto != "":
        listnames = listdir(args.auto)
        available_listnames = ["whitelist", "blacklist"]
        available_filternames = ["allow", "deny"]

        if args.auto[-1] != "/":
            args.auto += "/"
        
        for listname in listnames:
            filename = f"{args.auto}{listname}"
            
            if listname in available_listnames:
                not_empty_filenames[listname] = filename
            if listname in available_filternames:
                not_empty_filters[listname] = filename

    for key, filename in not_empty_filenames.items():
        lists[key] = SpamManager.tokenize(filename)

    for key, filename in not_empty_filters.items():
        filters[key] = SpamManager.tokenize(filename)

    if args.add:
        manager.add(lists, filters)
    elif args.remove:
        manager.remove(lists, filters)
        
except FileNotFoundError:
    parser.error("Una o muchas rutas de los archivos son invalidas.")
except Exception as error:
    parser.error(error)
