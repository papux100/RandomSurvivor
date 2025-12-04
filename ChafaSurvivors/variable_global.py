#variables_globales
import pygame, sys
import os

# Dimensiones por defecto
WINDOWED_RESOLUTION = (1280, 720)
FULLSCREEN_RESOLUTION = (1920, 1200)

# Declaracion de colores para el menu
WHITE = (255, 255, 255)
RED   = (54, 20, 14)

# Colores de fondo para los mundos
COLORES_MUNDOS = {
    "bosque": (34, 139, 34),           # Bosque verde
    "desierto": (243, 198, 74),        # Desierto amarillo
    "catedral": (245, 245, 245),       # Catedral blanco grisáceo
    "endless": (20, 20, 40)           # Modo endless (oscuro)
}

# Tamaño de mosaico para fondos (se puede ajustar)
TAMAÑO_MOSAICO = 1500  # Tamaño base de cada mosaico, ajustable
MAX_ENEMIGOS = 40
# Rutas de fondos por mundo
RUTAS_FONDOS = {
    "bosque": os.path.join("ChafaSurvivors", "images", "Bosque", "Bosque.png"),
    "desierto": os.path.join("ChafaSurvivors", "images", "Desierto", "Desierto.png"),
    "catedral": os.path.join("ChafaSurvivors", "images", "Catedral", "Catedral.png"),
    "endless": os.path.join("ChafaSurvivors", "images", "Bosque", "Bosque.png")  # Usa catedral para endless
}

Variables_Globales = {
    "STARTGAME": False,
    "FULLSCREEN": False,
    "RESOLUTION": WINDOWED_RESOLUTION,
    "WINDOWED_RES": WINDOWED_RESOLUTION,
    "FULLSCREEN_RES": FULLSCREEN_RESOLUTION,
    "MUNDO_ACTUAL": "bosque",           # Mundo actual
    "MUNDO_ANTERIOR": None,             # Para volver atrás
    "EN_ENDLESS": False,                # Si está en modo endless
    "PARTIDA_COMPLETADA": False,        # Si completó la partida normal
    "ESTADISTICAS_PARTIDA": {},          # Estadísticas al finalizar
    "nivel_juego": 1,  # Nueva variable para dificultad global
    "TAMAÑO_MOSAICO": TAMAÑO_MOSAICO 
}

Volum_Global = {
    "VOL" : 1.0,
    "SFX" : 1.0
}

# Diccionario de bloques del menú
def get_scaled_rect(x_percent, y_percent, width_percent, height_percent, screen_width, screen_height):
    return pygame.Rect(
        int(screen_width * x_percent),
        int(screen_height * y_percent),
        int(screen_width * width_percent),
        int(screen_height * height_percent)
    )

Bloques_Menu = {}

colores = {
    "rect1": RED,
    "rect2": RED,
    "rect3": RED,
    "rect4": RED,
    "rect5": RED,
    "rect6": RED,
    "rect7": RED,
    "rect8": RED,   
}

Texto_Bloques = {
     "rect1":"START",
     "rect2":"OPTIONS",
     "rect3":"EXIT",
     "rect4": "SONIDO",
     "rect5": "HARDMODE",
     "rect6": "EXIT",
     "rect7": "VOLUMEN",
     "rect8": "EXIT"
}

estado_bloques = {
    "rect1": True,
    "rect2": True,
    "rect3": True,
    "rect4": False,
    "rect5": False,
    "rect6": False,
    "rect7": False,
    "rect8": False
}

declaraciones = {
    "screen": None,
    "font": None,
    "selected_text" : "",
    "TextoDerechos" : None,
    "background": None
}

# Enemigos por mundo
ENEMIGOS_POR_MUNDO = {
    "bosque": ["zombie", "esqueleto", "brujo"],
    "desierto": ["escorpion", "momia", "gusano"],
    "catedral": ["angel_oscuro", "sacerdote", "templario"],
    "endless": ["zombie", "esqueleto", "brujo", "escorpion", "momia", "gusano", "angel_oscuro", "sacerdote", "templario"]
}

# Requisitos para avanzar de mundo
REQUISITOS_MUNDO = {
    "bosque": {"nivel": 20, "mundo_siguiente": "desierto"},
    "desierto": {"nivel": 40, "mundo_siguiente": "catedral"},
    "catedral": {"nivel": 60, "mundo_siguiente": "endless"}
}
MUSICA_MUNDO = {
    "Menu": "ChafaSurvivors\sounds\Menu.mp3",
    "bosque": "ChafaSurvivors\sounds\Bosque.mp3",
    "desierto": "ChafaSurvivors\sounds\Desierto.mp3",
    "catedral": "ChafaSurvivors\sounds\Catedral.mp3"
}
musica_actual = None
unavez = False

def cambiar_musica(tipo):
    """Carga y reproduce música sólo si no está ya sonando.
    Busca la clave en MUSICA_MUNDO ignorando mayúsculas/minúsculas.
    """
    global musica_actual

    # buscar clave en MUSICA_MUNDO de forma case-insensitive
    clave = None
    for k in MUSICA_MUNDO.keys():
        if k.lower() == str(tipo).lower():
            clave = k
            break
    if not clave:
        # key no encontrada
        print(f"[audio] Mundo '{tipo}' no corresponde a ninguna pista.")
        return

    # si ya suena, no hacer nada
    if musica_actual == clave:
        return

    try:
        pygame.mixer.music.load(MUSICA_MUNDO[clave])
        pygame.mixer.music.play(-1)
        musica_actual = clave
        # opcional: ajustar volumen por defecto
        pygame.mixer.music.set_volume(0.5)
        print(f"[audio] Reproduciendo: {clave}")
    except Exception as e:
        print(f"[audio] Error al cargar {MUSICA_MUNDO[clave]}: {e}")
       

def actualizar_tamanos_bloques():
    """Actualiza los tamaños de los bloques según la resolución actual"""
    screen_width, screen_height = Variables_Globales["RESOLUTION"]
    
    Bloques_Menu["rect1"] = get_scaled_rect(0.1, 0.4, 0.2, 0.1, screen_width, screen_height)
    Bloques_Menu["rect2"] = get_scaled_rect(0.1, 0.55, 0.2, 0.1, screen_width, screen_height)
    Bloques_Menu["rect3"] = get_scaled_rect(0.1, 0.7, 0.2, 0.1, screen_width, screen_height)
    Bloques_Menu["rect4"] = get_scaled_rect(0.1, 0.4, 0.2, 0.1, screen_width, screen_height)
    Bloques_Menu["rect5"] = get_scaled_rect(0.1, 0.55, 0.2, 0.1, screen_width, screen_height)
    Bloques_Menu["rect6"] = get_scaled_rect(0.7, 0.7, 0.2, 0.1, screen_width, screen_height)
    Bloques_Menu["rect7"] = get_scaled_rect(0.1, 0.5, 0.2, 0.1, screen_width, screen_height)
    Bloques_Menu["rect8"] = get_scaled_rect(0.1, 0.7, 0.2, 0.1, screen_width, screen_height)

def inicializacion_menu():
    # Configuración de pantalla
    if Variables_Globales["FULLSCREEN"]:
        Variables_Globales["RESOLUTION"] = Variables_Globales["FULLSCREEN_RES"]
        declaraciones["screen"] = pygame.display.set_mode(
            Variables_Globales["RESOLUTION"], 
            pygame.FULLSCREEN
        )
    else:
        Variables_Globales["RESOLUTION"] = Variables_Globales["WINDOWED_RES"]
        declaraciones["screen"] = pygame.display.set_mode(Variables_Globales["RESOLUTION"])
    
    pygame.display.set_caption("Puras holadas")
    
    # Crear fuente escalable
    screen_width, screen_height = Variables_Globales["RESOLUTION"]
    font_size = int(screen_height * 0.05)
    declaraciones["font"] = pygame.font.SysFont(None, font_size)
    
    # Actualizar tamaños de bloques
    actualizar_tamanos_bloques()

    
    # Cargar fondo.png si existe
    try:
        fondo_path = os.path.join("ChafaSurvivors", "images", "fondo.png")
        if os.path.exists(fondo_path):
            declaraciones["background"] = pygame.image.load(fondo_path)
            declaraciones["background"] = pygame.transform.scale(
                declaraciones["background"], 
                Variables_Globales["RESOLUTION"]
            )
            print(f"Fondo cargado desde: {fondo_path}")
        else:
            # Intentar otras rutas posibles
            posibles_rutas = [
                "fondo.png",
                "images/fondo.png",
                "ChafaSurvivors/images/fondo.png",
                "ChafaSurvivors/fondo.png"
            ]
            
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    declaraciones["background"] = pygame.image.load(ruta)
                    declaraciones["background"] = pygame.transform.scale(
                        declaraciones["background"], 
                        Variables_Globales["RESOLUTION"]
                    )
                    print(f"Fondo cargado desde: {ruta}")
                    break
            else:
                # Si no se encuentra, crear fondo de color
                declaraciones["background"] = None
                print("No se encontró fondo.png, usando color de fondo por defecto")
                
    except Exception as e:
        print(f"Error cargando fondo.png: {e}")
        declaraciones["background"] = None
    
    # Texto de derechos
    font_derechos_size = int(screen_height * 0.03)
    font_derechos = pygame.font.SysFont(None, font_derechos_size)
    declaraciones["TextoDerechos"] = font_derechos.render("Todos los derechos reservados", True, WHITE)