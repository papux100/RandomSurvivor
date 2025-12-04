import pygame
import animaciones
from poder import PoderFactory,AuraSagrada
import random
import math

class Personaje:  
    def __init__(self, experiencia, vida, velocidad, animaciones_dict):
        self.experiencia = experiencia
        self.experiencia_total = experiencia
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
        self.subiendo_nivel = False  # Bandera para prevenir bucles
        
        # Sistema de experiencia
        self.exp_para_proximo_nivel = self.calcular_exp_requerida(self.nivel + 1)
        self.exp_para_nivel_actual = self.calcular_exp_requerida(self.nivel)

        if not isinstance(animaciones_dict, dict):
            animaciones_dict = {}
        
        primera_animacion = list(animaciones_dict.keys())[0] if animaciones_dict else 'quieto_derecha'
        
        if primera_animacion in animaciones_dict and animaciones_dict[primera_animacion]:
            primera_textura = animaciones_dict[primera_animacion][0]
        else:
            primera_textura = pygame.Surface((50, 50))
            primera_textura.fill((255, 0, 0))
        
        self.actor_animado = animaciones.ActorAnimado(
            primera_textura,
            (100, 300),
            animaciones_dict,
            primera_animacion,
            0.15
        )
    
    def calcular_exp_requerida(self, nivel):
        """Calcula la experiencia requerida para alcanzar un nivel"""
        # Fórmula: 10 * nivel^1.5 (progresión exponencial)
        return int(10 * math.pow(nivel, 1.5))
    
    def ganar_experiencia(self, cantidad):
        """Gana experiencia y sube de nivel si es necesario - VERSIÓN SIMPLIFICADA"""
        # Evitar recursión
        if hasattr(self, '_procesando_experiencia') and self._procesando_experiencia:
            return False
        
        self._procesando_experiencia = True
        
        try:
            self.experiencia += cantidad
            self.experiencia_total += cantidad
            
            # Verificar si alcanzó el siguiente nivel
            if self.experiencia >= self.exp_para_proximo_nivel:
                nivel_antes = self.nivel
                
                # Solo subir un nivel
                self.nivel += 1
                
                # Mejoras por nivel (simplificado)
                self.vida_max += 0
                self.vida = self.vida_max
                self.velocidad_base += 0.05
                self.velocidad = self.velocidad_base
                
                # Actualizar requisitos de XP
                self.exp_para_proximo_nivel = self.calcular_exp_requerida(self.nivel + 1)
                self.exp_para_nivel_actual = self.calcular_exp_requerida(self.nivel)
                
                # Intentar dar poder (pero no bloquear si falla)
                try:
                    resultado_poder = self.ganar_poder_por_nivel_simple()
                    # No hacer nada con el resultado para evitar problemas
                except:
                    pass  # Silenciar error
                
                self._procesando_experiencia = False
                return True  # Subió de nivel
            else:
                self._procesando_experiencia = False
                return False  # No subió de nivel
                
        except Exception as e:
            print(f"Error en ganar_experiencia: {e}")
            self._procesando_experiencia = False
            return False

    def ganar_poder_por_nivel_simple(self):
        """Versión simplificada de ganar poder por nivel"""
        if not hasattr(self, 'poderes'):
            self.poderes = []
        
        # Solo crear poder básico para evitar problemas
        poder_nuevo = PoderFactory.crear_poder_aleatorio(self.nivel)
        if poder_nuevo:
            self.poderes.append(poder_nuevo)
            return "Nuevo poder básico"
        
        return "Sin poder nuevo"
    
    def get_progreso_nivel(self):
        """Devuelve el progreso hacia el siguiente nivel (0.0 a 1.0)"""
        if self.nivel == 1:
            exp_en_este_nivel = self.experiencia
        else:
            exp_en_este_nivel = self.experiencia - self.exp_para_nivel_actual
        
        exp_necesaria_para_subir = self.exp_para_proximo_nivel - self.exp_para_nivel_actual
        
        if exp_necesaria_para_subir <= 0:
            return 1.0
            
        return exp_en_este_nivel / exp_necesaria_para_subir
    
    def subir_nivel(self):
        """Sube de nivel el jugador y otorga recompensas"""
        self.nivel += 1
        
        # Mejoras por nivel
        self.vida_max += 20 + (self.nivel * 2)
        self.vida = self.vida_max
        self.velocidad_base += 0.05
        self.velocidad = self.velocidad_base
        
        # Obtener un poder aleatorio al subir de nivel
        resultado_poder = self.ganar_poder_por_nivel()
        
        # NO devolver diccionario complejo que pueda causar problemas
        return resultado_poder
    
    def ganar_poder_por_nivel(self):
        """Obtiene un poder aleatorio al subir de nivel"""
        if not hasattr(self, 'poderes'):
            self.poderes = []
        
        # Crear un poder aleatorio con nivel apropiado
        try:
            poder_nuevo = PoderFactory.crear_poder_aleatorio(self.nivel)
            if not poder_nuevo:
                return None
        except:
            # Si hay error al crear poder, usar uno simple
            poder_nuevo = PoderFactory.crear_poder("bola_fuego", 1)
            if not poder_nuevo:
                return None
        
        # Verificar si ya existe para stackear o subir de nivel
        for poder in self.poderes:
            if type(poder) == type(poder_nuevo):
                # Primero intentar subir de nivel
                if hasattr(poder, 'subir_nivel'):
                    if poder.subir_nivel():
                        return f"Subido de nivel: {poder.nombre} (Nv.{poder.nivel})"
                
                # Si no pudo subir nivel, intentar stackear
                if hasattr(poder, 'puede_staquear') and poder.puede_staquear():
                    if poder.stacks < poder.max_stacks:
                        poder.stacks += 1
                        if hasattr(poder, 'actualizar_estadisticas'):
                            poder.actualizar_estadisticas()
                        return f"Stackeado: {poder.nombre} (x{poder.stacks})"
                
                # Si ya está al máximo, devolver mensaje
                return f"{poder.nombre} ya está al máximo"
        
        # Si no lo tiene, agregarlo
        self.poderes.append(poder_nuevo)
        return f"Nuevo poder: {poder_nuevo.nombre}"

    def draw(self, surface):
        self.actor_animado.draw(surface)

    def draw_con_offset(self, surface, offset_x=0, offset_y=0, centrado=False):
        self.actor_animado.draw_con_offset(surface, offset_x, offset_y, centrado)
    
    def update(self, dt):
        self.actor_animado.update(dt)
        
        if self.invulnerable:
            self.tiempo_invulnerable -= dt
            if self.tiempo_invulnerable <= 0:
                self.invulnerable = False
    
    def cambiar_animacion(self, nombre_animacion):
        return self.actor_animado.cambiar_animacion(nombre_animacion)
    
    def set_hitbox(self, tamaño, offset=(0, 0)):
        self.actor_animado.actor.set_hitbox(tamaño, offset)
    
    def draw_hitbox(self, surface, color=(255, 0, 0), offset_x=0, offset_y=0, centrado=False):
        self.actor_animado.actor.draw_hitbox(surface, color, offset_x, offset_y, centrado)
    
    def agregar_poder(self, poder):
        """Agrega un nuevo poder al jugador"""
        if not hasattr(self, 'poderes'):
            self.poderes = []
        
            # Si es Aura Sagrada, activarla inmediatamente
        if isinstance(poder, AuraSagrada):
            # Activar la aura inmediatamente
            tiempo_actual = pygame.time.get_ticks() / 1000.0
            efectos = poder.usar(self, [], tiempo_actual)
        
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
        try:
            poder_nuevo = PoderFactory.crear_poder_aleatorio(self.nivel)
            if not poder_nuevo:
                return "No se pudo crear poder"
        except:
            poder_nuevo = PoderFactory.crear_poder("bola_fuego", 1)
            if not poder_nuevo:
                return "No se pudo crear poder"
        
        # Verificar si ya existe para stackear o subir de nivel
        for poder in self.poderes:
            if type(poder) == type(poder_nuevo):
                if hasattr(poder, 'puede_staquear') and poder.puede_staquear():
                    if poder.stacks < poder.max_stacks:
                        poder.stacks += 1
                        if hasattr(poder, 'actualizar_estadisticas'):
                            poder.actualizar_estadisticas()
                        return f"Stackeado: {poder.nombre} (x{poder.stacks})"
                
                if hasattr(poder, 'subir_nivel') and poder.subir_nivel():
                    return f"Subido de nivel: {poder.nombre} (Nv.{poder.nivel})"
                else:
                    return f"{poder.nombre} ya está al máximo nivel"
        
        # Si no lo tiene, agregar nuevo
        self.poderes.append(poder_nuevo)
        return f"Nuevo poder: {poder_nuevo.nombre}"
    
    def recibir_daño(self, cantidad):
        if not self.invulnerable:
            self.vida -= cantidad
            self.invulnerable = True
            self.tiempo_invulnerable = 0.5
            return self.vida <= 0
        return False
    
    def curar(self, cantidad):
        self.vida = min(self.vida + cantidad, self.vida_max)
    
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