import yaml

# Cargar configuración desde config.yaml
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Exportar config para otros módulos que lo necesiten
__all__ = ['config', 'USER_BD', 'PASS_BD', 'SERVER_BD', 'BD', 'PORT', 'MODE_DEBUG', 
           'NAME_EMPRESA', 'NAME_USER', 'LOGO', 'RUBRO_EMPRESA', 'PAGE_TITLE_PREFIX',
           'DRIVE_ID_CARPETA_STORAGE', 'FOLDER_ID_CARPETA_STORAGE', 
           'MICROSOFT_GRAPH_TENANT_ID', 'MICROSOFT_GRAPH_CLIENT_ID', 'MICROSOFT_GRAPH_CLIENT_SECRET']

#CONEXION BD
USER_BD = config['database']['user']
PASS_BD = config['database']['password']
SERVER_BD = config['database']['server']
BD = config['database']['name']




#CONFIG APP
PORT = config['app']['port']
MODE_DEBUG = config['app']['debug']
NAME_EMPRESA = config['empresa']['name']
NAME_USER = config['empresa']['name_user']
LOGO = config['app']['logo']
RUBRO_EMPRESA = config['empresa']['rubro']


PAGE_TITLE_PREFIX = "BI | "

# OneDrive/SharePoint Configuration
DRIVE_ID_CARPETA_STORAGE = config.get('onedrive', {}).get('drive_id', "b!M5ucw3aa_UqBAcqv3a6affR7vTZM2a5ApFygaKCcATxyLdOhkHDiRKl9EvzaYbuR")
FOLDER_ID_CARPETA_STORAGE = config.get('onedrive', {}).get('folder_id', "01XOBWFSBLVGULAQNEKNG2WR7CPRACEN7Q")

# Microsoft Graph API Configuration  
MICROSOFT_GRAPH_TENANT_ID = config.get('microsoft_graph', {}).get('tenant_id')
MICROSOFT_GRAPH_CLIENT_ID = config.get('microsoft_graph', {}).get('client_id')
MICROSOFT_GRAPH_CLIENT_SECRET = config.get('microsoft_graph', {}).get('client_secret')