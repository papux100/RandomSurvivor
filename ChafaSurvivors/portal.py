import pygame
import math
from herramientas import Actor

class Portal:
    def __init__(self, x, y, tipo="azul", mundo_destino=None, activo=True):
        self.x = x
        self.y = y
        self.tipo = tipo  # "azul" o "rojo"
        self.mundo_destino = mundo_destino
        self.activo = activo
        self.radio = 40
        self.tiempo_animacion = 0
        self.velocidad_animacion = 0.05
        
        # Colores según tipo
        if tipo == "azul":
            self.color_interior = (100, 150, 255)
            self.color_exterior = (50, 100, 200)
        else:  # rojo
            self.color_interior = (255, 100, 100)
            self.color_exterior = (200, 50, 50)
    
    def update(self, dt):
        """Actualiza la animación del portal"""
        self.tiempo_animacion += dt * self.velocidad_animacion
    
    def draw(self, screen, offset_x=0, offset_y=0):
        """Dibuja el portal en la pantalla"""
        if not self.activo:
            return
            
        screen_x = self.x + offset_x
        screen_y = self.y + offset_y
        
        # Dibujar círculos concéntricos animados
        for i in range(3):
            radio = self.radio * (0.7 + 0.3 * math.sin(self.tiempo_animacion + i * 1.0))
            alpha = 150 - i * 50
            
            # Crear superficie con alpha
            surf = pygame.Surface((int(radio*2), int(radio*2)), pygame.SRCALPHA)
            color = list(self.color_exterior if i == 0 else self.color_interior)
            color_with_alpha = color + [alpha]
            
            pygame.draw.circle(surf, color_with_alpha, 
                             (int(radio), int(radio)), 
                             int(radio))
            pygame.draw.circle(surf, (255, 255, 255, alpha), 
                             (int(radio), int(radio)), 
                             int(radio), 2)
            
            screen.blit(surf, (screen_x - radio, screen_y - radio))
        
        # Dibujar icono según tipo
        icon_size = 20
        if self.tipo == "azul":
            # Flecha hacia adelante
            points = [
                (screen_x - icon_size//2, screen_y - icon_size),
                (screen_x + icon_size//2, screen_y),
                (screen_x - icon_size//2, screen_y + icon_size)
            ]
            pygame.draw.polygon(screen, (255, 255, 255), points)
        else:
            # Puerta/casa (icono de salida)
            pygame.draw.rect(screen, (255, 255, 255), 
                           (screen_x - icon_size//2, screen_y - icon_size//2, 
                            icon_size, icon_size), 2)
            pygame.draw.line(screen, (255, 255, 255),
                           (screen_x, screen_y - icon_size//2),
                           (screen_x, screen_y - icon_size//4), 2)
    
    def verificar_colision(self, jugador_x, jugador_y):
        """Verifica si el jugador colisiona con el portal"""
        if not self.activo:
            return False
            
        distancia = math.hypot(jugador_x - self.x, jugador_y - self.y)
        return distancia < self.radio + 30  # Radio del jugador
    
    def get_info(self):
        """Devuelve información del portal"""
        if self.tipo == "azul":
            return f"Portal a {self.mundo_destino.capitalize()}"
        else:
            return "Portal de salida"
    
    def set_posicion(self, x, y):
        """Establece la posición del portal"""
        self.x = x
        self.y = y
    
    def set_activo(self, activo):
        """Activa o desactiva el portal"""
        self.activo = activo