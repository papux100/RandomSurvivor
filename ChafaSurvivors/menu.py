#menu
from variable_global import *
import waza

def dibujar_cajas():
    for nombre, rect in Bloques_Menu.items():
        if estado_bloques[nombre]: 
            pygame.draw.rect(declaraciones["screen"], RED, rect)
            
            button_font_size = int(rect.height * 0.6)
            if button_font_size < 12:
                button_font_size = 12
            button_font = pygame.font.SysFont(None, button_font_size)
            
            texto = button_font.render(Texto_Bloques[nombre], True, WHITE)
            text_rect = texto.get_rect(center=rect.center)
            declaraciones["screen"].blit(texto, text_rect)

def menu():
    screen_width, screen_height = Variables_Globales["RESOLUTION"]

    # Dibujar fondo si existe
    if declaraciones["background"]:
        declaraciones["screen"].blit(declaraciones["background"], (0, 0))
    else:
        # Fondo de color si no hay imagen
        declaraciones["screen"].fill((20, 10, 30))  # Color morado oscuro
    
    dibujar_cajas()
    
    # Dibujar checkbox de pantalla completa si estamos en opciones
    if estado_bloques["rect4"]:
        font_size = int(screen_height * 0.04)
        font_pequena = pygame.font.SysFont(None, font_size)
        
        texto_pantalla = font_pequena.render("Pantalla completa:", True, WHITE)
        texto_x = screen_width // 2 + screen_width * 0.05
        texto_y = screen_height * 0.45
        declaraciones["screen"].blit(texto_pantalla, (texto_x, texto_y))
        
        checkbox_size = int(screen_height * 0.03)
        checkbox_rect = pygame.Rect(
            texto_x + texto_pantalla.get_width() + 20,
            texto_y,
            checkbox_size,
            checkbox_size
        )
        pygame.draw.rect(declaraciones["screen"], WHITE, checkbox_rect, 2)
        
        if Variables_Globales["FULLSCREEN"]:
            pygame.draw.line(declaraciones["screen"], WHITE, 
                           (checkbox_rect.left + 5, checkbox_rect.centery),
                           (checkbox_rect.right - 5, checkbox_rect.centery), 3)
            pygame.draw.line(declaraciones["screen"], WHITE,
                           (checkbox_rect.centerx, checkbox_rect.top + 5),
                           (checkbox_rect.centerx, checkbox_rect.bottom - 5), 3)
    
    # Solo mostrar derechos de autor si estamos en menú principal
    if not Variables_Globales["STARTGAME"]:
        derechos_x = screen_width - declaraciones["TextoDerechos"].get_width() - 20
        derechos_y = screen_height - declaraciones["TextoDerechos"].get_height() - 20
        declaraciones["screen"].blit(declaraciones["TextoDerechos"], (derechos_x, derechos_y))
    
    # Mostrar texto seleccionado
    if declaraciones["selected_text"] and not Variables_Globales["STARTGAME"]:
        # Fondo semitransparente para el texto
        text_surface = declaraciones["font"].render(declaraciones["selected_text"], True, WHITE)
        text_width = text_surface.get_width() + 20
        text_height = text_surface.get_height() + 10
        text_x = screen_width // 2 - text_width // 2
        text_y = screen_height * 0.85
        
        # Fondo para el texto
        text_bg = pygame.Surface((text_width, text_height), pygame.SRCALPHA)
        text_bg.fill((0, 0, 0, 150))
        pygame.draw.rect(text_bg, (255, 255, 255, 100), text_bg.get_rect(), 2)
        declaraciones["screen"].blit(text_bg, (text_x, text_y))
        
        # Texto
        declaraciones["screen"].blit(text_surface, (text_x + 10, text_y + 5))
        
def menu_eventos(event, running):
    screen_width, screen_height = Variables_Globales["RESOLUTION"]
    
    for nombre, rect in Bloques_Menu.items():
        if rect.collidepoint(event.pos):
            
            if nombre == "rect1":  # START GAME
                Variables_Globales["STARTGAME"] = True
                # Limpiar estadísticas anteriores
                Variables_Globales["ESTADISTICAS_PARTIDA"] = {}
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
    
    # Verificar clic en checkbox de pantalla completa
    if estado_bloques["rect4"]:
        font_size = int(screen_height * 0.04)
        font_pequena = pygame.font.SysFont(None, font_size)
        texto_pantalla = font_pequena.render("Pantalla completa:", True, WHITE)
        
        checkbox_size = int(screen_height * 0.03)
        checkbox_rect = pygame.Rect(
            screen_width // 2 + screen_width * 0.05 + texto_pantalla.get_width() + 20,
            screen_height * 0.45,
            checkbox_size,
            checkbox_size
        )
        
        if checkbox_rect.collidepoint(event.pos):
            Variables_Globales["FULLSCREEN"] = not Variables_Globales["FULLSCREEN"]
            
            was_in_game = Variables_Globales["STARTGAME"]
            
            if Variables_Globales["FULLSCREEN"]:
                Variables_Globales["RESOLUTION"] = Variables_Globales["FULLSCREEN_RES"]
                declaraciones["screen"] = pygame.display.set_mode(
                    Variables_Globales["RESOLUTION"], 
                    pygame.FULLSCREEN
                )
            else:
                Variables_Globales["RESOLUTION"] = Variables_Globales["WINDOWED_RES"]
                declaraciones["screen"] = pygame.display.set_mode(Variables_Globales["RESOLUTION"])
            
            # Recargar fondo con nueva resolución
            try:
                posibles_rutas = [
                    os.path.join("ChafaSurvivors", "images", "fondo.png"),
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
                        print(f"Fondo recargado desde: {ruta}")
                        break
                else:
                    declaraciones["background"] = None
                    
            except Exception as e:
                print(f"Error recargando fondo: {e}")
                declaraciones["background"] = None
            
            new_font_size = int(Variables_Globales["RESOLUTION"][1] * 0.05)
            declaraciones["font"] = pygame.font.SysFont(None, new_font_size)
            
            derechos_font_size = int(Variables_Globales["RESOLUTION"][1] * 0.03)
            derechos_font = pygame.font.SysFont(None, derechos_font_size)
            declaraciones["TextoDerechos"] = derechos_font.render("Todos los derechos reservados", True, WHITE)
            
            actualizar_tamanos_bloques()
            Variables_Globales["STARTGAME"] = was_in_game
    
    return running

def ejecutar_juego():
    """Función que ejecuta el juego principal"""
    pygame.quit()
    pygame.init()
    waza.main()