import pygame
import animaciones

class Personaje:  
    def __init__(self, experiencia, vida, velocidad, animaciones_dict):
        self.experiencia = experiencia
        self.vida = vida
        self.velocidad = velocidad

        # Obtener la primera textura de la primera animación
        primera_animacion = list(animaciones_dict.keys())[0]
        primera_textura = animaciones_dict[primera_animacion][0]
        
        self.actor_animado = animaciones.ActorAnimado(
            primera_textura,  # imagen inicial
            (100, 300),      # posición inicial  
            animaciones_dict, # diccionario de animaciones
            primera_animacion, # animación inicial
            0.1            # velocidad
        )
    
    def draw(self, surface):
        self.actor_animado.draw(surface)
    
    def update(self, dt):
        self.actor_animado.update(dt)
    
    def cambiar_animacion(self, nombre_animacion):
        self.actor_animado.cambiar_animacion(nombre_animacion)
    
    # Propiedades para acceder a posición (getters y setters)
    @property
    def x(self):
        return self.actor_animado.actor.x
    
    @x.setter
    def x(self, value):
        self.actor_animado.actor.x = value
    
    @property
    def y(self):
        return self.actor_animado.actor.y
    
    @y.setter
    def y(self, value):
        self.actor_animado.actor.y = value