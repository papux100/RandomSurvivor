#menu
from variable_global import *
import waza  # Importamos el módulo waza

# Función para dibujar los rectángulos
def dibujar_cajas():
    for nombre, rect in Bloques_Menu.items():
        if estado_bloques[nombre]: 
            pygame.draw.rect(declaraciones["screen"], RED, rect)
            texto = declaraciones["font"].render(Texto_Bloques[nombre], True, WHITE)
            text_rect = texto.get_rect(center=rect.center)
            declaraciones["screen"].blit(texto, text_rect)

def menu():
    if declaraciones["background"]:
        declaraciones["screen"].blit(declaraciones["background"], (0, 0))
    else:
        declaraciones["screen"].fill((0, 0, 0))  # Fondo negro si no hay imagen
    dibujar_cajas()  # Dibujar los rectángulos
    
    if not Variables_Globales["STARTGAME"]:
        texto_original = declaraciones["font"].render("Todos los derechos reservados", True, WHITE)    
        texto_escalado = pygame.transform.scale(texto_original, (300, 100))
        declaraciones["TextoDerechos"] = texto_escalado
        declaraciones["screen"].blit(declaraciones["TextoDerechos"], (WIDTH -300, HEIGHT- 90))
    
    # Mostrar texto si se ha seleccionado
    if declaraciones["selected_text"] and not Variables_Globales["STARTGAME"]:
        text_surface = declaraciones["font"].render(declaraciones["selected_text"], True, WHITE)
        declaraciones["screen"].blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, 450))
        
def menu_eventos(event, running):
    for nombre, rect in Bloques_Menu.items():
        if rect.collidepoint(event.pos):
            
            if nombre == "rect1":  # START GAME
                Variables_Globales["STARTGAME"] = True
                # No cambiamos el estado de los bloques aquí, lo hará main.py
                # cuando realmente entre al juego
                return running
            
            if nombre == "rect2":  # OPTIONS
                estado_bloques["rect1"] = False
                estado_bloques["rect2"] = False
                estado_bloques["rect3"] = False
                estado_bloques["rect4"] = True
                estado_bloques["rect5"] = True
                estado_bloques["rect6"] = True
            
            if nombre == "rect3":  # EXIT
                return False

            if nombre == "rect4":  # SONIDO
                pass
            
            if nombre == "rect5":  # HARDMODE
                pass
            
            if nombre == "rect6":  # EXIT (de opciones)
                estado_bloques["rect1"] = True
                estado_bloques["rect2"] = True
                estado_bloques["rect3"] = True
                estado_bloques["rect4"] = False
                estado_bloques["rect5"] = False
                estado_bloques["rect6"] = False
    
    return running

def ejecutar_juego():
    """Función que ejecuta el juego principal"""
    # Reiniciar Pygame (opcional, dependiendo de cómo lo maneje waza.py)
    pygame.quit()
    pygame.init()
    
    # Ejecutar el juego principal desde waza.py
    waza.main()  # Si waza.py tiene una función main()