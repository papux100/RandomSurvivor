#variables_globales
import pygame, sys
# Dimensiones de pantalla
WIDTH, HEIGHT = 800, 600

# Declaracion de colores para el menu
WHITE = (255, 255, 255)
RED   = (54, 20, 14)

Variables_Globales = {
    "STARTGAME": False
    
}

Volum_Global = {
    "VOL" : 1.0,
    "SFX" : 1.0
}

# Diccionario de bloques del menú
#todos estos son los bloques de menu
#r1 -start , r2 - options , - r3 exit.
#r4-Hardmode, r5, volumen, r6 exit.
# r7 - volumen general, r8 - exit.
Bloques_Menu = {
    "rect1": pygame.Rect(75, 250, 250, 75),
    "rect2": pygame.Rect(75, 250 +(100*1), 250, 75),
    "rect3": pygame.Rect(75,  250 +(100*2), 250, 75),
    "rect4": pygame.Rect(75,  250, 250, 75),
    "rect5": pygame.Rect(75,  250 +(100*1), 250, 75),
    "rect6": pygame.Rect(550,  250 +(100*2), 250, 75),
    "rect7": pygame.Rect(75,  250 +(150), 250, 75),
    "rect8": pygame.Rect(75,  250 +(100*2), 250, 75),
}

# Diccionario de colores para cada bloque
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

def inicializacion_menu():
    # Configuración de pantalla
    declaraciones["screen"]  = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Puras holadas")
    declaraciones["font"] = pygame.font.SysFont(None, 48)
    declaraciones["background"] = pygame.image.load("ChafaSurvivors\images\\fondo.jpg")  
    declaraciones["background"] = pygame.transform.scale(declaraciones["background"], (WIDTH, HEIGHT))
    declaraciones["TextoDerechos"] =  declaraciones["font"].render("Todos los derechos recervados", True, WHITE)