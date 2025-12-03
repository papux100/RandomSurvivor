import pygame
import animaciones
from poder import PoderFactory
import random

class Personaje:  
    def __init__(self, experiencia, vida, velocidad, animaciones_dict):
        self.experiencia = experiencia
        self.vida = vida
        self.vida_max = vida
        self.velocidad = velocidad
        self.velocidad_base = velocidad
        self.nivel = 1
        self.oro = 0
        self.poderes = []
        self.efectos_activos = []
        self.invulnerable = False
        self.tiempo_invulnerable = 0

        # Asegurarse de que animaciones_dict tiene la estructura correcta
        if not isinstance(animaciones_dict, dict):
            animaciones_dict = {}
        
        # Obtener la primera textura de la primera animación
        primera_animacion = list(animaciones_dict.keys())[0] if animaciones_dict else 'quieto_derecha'
        
        # Verificar que la primera animación tenga texturas
        if primera_animacion in animaciones_dict and animaciones_dict[primera_animacion]:
            primera_textura = animaciones_dict[primera_animacion][0]
        else:
            # Crear textura por defecto si no hay
            primera_textura = pygame.Surface((50, 50))
            primera_textura.fill((255, 0, 0))
        
        self.actor_animado = animaciones.ActorAnimado(
            primera_textura,  # imagen inicial
            (100, 300),      # posición inicial  
            animaciones_dict, # diccionario de animaciones
            primera_animacion, # animación inicial
            0.15            # velocidad
        )
    
    def draw(self, surface):
        self.actor_animado.draw(surface)

    def draw_con_offset(self, surface, offset_x=0, offset_y=0, centrado=False):
        """Dibuja el personaje aplicando el offset de la cámara"""
        self.actor_animado.draw_con_offset(surface, offset_x, offset_y, centrado)
    
    def update(self, dt):
        self.actor_animado.update(dt)
        
        # Actualizar invulnerabilidad
        if self.invulnerable:
            self.tiempo_invulnerable -= dt
            if self.tiempo_invulnerable <= 0:
                self.invulnerable = False
    
    def cambiar_animacion(self, nombre_animacion):
        return self.actor_animado.cambiar_animacion(nombre_animacion)
    
    # Métodos para hitbox
    def set_hitbox(self, tamaño, offset=(0, 0)):
        """Define la hitbox del personaje"""
        self.actor_animado.actor.set_hitbox(tamaño, offset)
    
    def draw_hitbox(self, surface, color=(255, 0, 0), offset_x=0, offset_y=0, centrado=False):
        """Dibuja la hitbox para debugging con offset"""
        self.actor_animado.actor.draw_hitbox(surface, color, offset_x, offset_y, centrado)
    
    # Sistema de poderes
    def agregar_poder(self, poder):
        """Agrega un nuevo poder al jugador"""
        if not hasattr(self, 'poderes'):
            self.poderes = []
        
        # Verificar si ya tiene este poder para stackear
        for p in self.poderes:
            if type(p) == type(poder):
                if hasattr(p, 'puede_staquear') and p.puede_staquear() and p.stacks < p.max_stacks:
                    p.stacks += 1
                    if hasattr(p, 'actualizar_estadisticas'):
                        p.actualizar_estadisticas()
                    return f"Stackeado: {poder.nombre} (x{p.stacks})"
                else:
                    if hasattr(p, 'subir_nivel') and p.subir_nivel():
                        return f"Subido de nivel: {poder.nombre} (Nv.{p.nivel})"
                    else:
                        return f"{poder.nombre} ya está al máximo nivel"
        
        # Si no lo tiene, agregarlo
        self.poderes.append(poder)
        return f"Nuevo poder: {poder.nombre}"
    
    def ganar_poder_aleatorio(self):
        """Gana o mejora un poder aleatorio"""
        if not hasattr(self, 'poderes'):
            self.poderes = []
        
        # Crear un poder aleatorio
        poder_nuevo = PoderFactory.crear_poder_aleatorio()
        if not poder_nuevo:
            return "No se pudo crear poder"
        
        # Verificar si ya existe para stackear o subir de nivel
        for poder in self.poderes:
            if type(poder) == type(poder_nuevo):
                if hasattr(poder, 'puede_staquear') and poder.puede_staquear() and random.random() < 0.5:
                    if poder.stacks < poder.max_stacks:
                        poder.stacks += 1
                        if hasattr(poder, 'actualizar_estadisticas'):
                            poder.actualizar_estadisticas()
                        return f"Stackeado: {poder.nombre} (x{poder.stacks})"
                
                if random.random() < 0.7:  # 70% de chance de subir nivel
                    if hasattr(poder, 'subir_nivel') and poder.subir_nivel():
                        return f"Subido de nivel: {poder.nombre} (Nv.{poder.nivel})"
                    else:
                        return f"{poder.nombre} ya está al máximo nivel"
        
        # Si no lo tiene o no se pudo stackear/mejorar, agregar nuevo
        self.poderes.append(poder_nuevo)
        return f"Nuevo poder: {poder_nuevo.nombre}"
    
    # Sistema de daño
    def recibir_daño(self, cantidad):
        """Recibe daño de un enemigo"""
        if not self.invulnerable:
            self.vida -= cantidad
            self.invulnerable = True
            self.tiempo_invulnerable = 0.5
            return self.vida <= 0
        return False
    
    def curar(self, cantidad):
        """Cura al jugador"""
        self.vida = min(self.vida + cantidad, self.vida_max)
    
    def ganar_experiencia(self, cantidad):
        """Gana experiencia y sube de nivel si es necesario"""
        self.experiencia += cantidad
        exp_necesaria = self.nivel * 100
        if self.experiencia >= exp_necesaria:
            self.subir_nivel()
            return True
        return False
    
    def subir_nivel(self):
        """Sube de nivel el jugador"""
        self.nivel += 1
        self.vida_max += 20
        self.vida = self.vida_max
        self.velocidad_base += 0.1
        self.velocidad = self.velocidad_base
        return True
    
    # Propiedades para posición
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
    
    @property
    def hitbox(self):
        return self.actor_animado.actor.hitbox