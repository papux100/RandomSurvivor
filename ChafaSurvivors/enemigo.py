from personajes import Personaje
import animaciones
import random

class Enemigo(Personaje):
    
    def __init__(self, experiencia, vida, velocidad, animaciones_dict, follow=None, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, animaciones_dict)
        self.follow = follow
        self.vida_max = vida
        self.daño = 5  # Daño base
        self.velocidad_ataque = 1.0
        self.tiempo_ultimo_ataque = 0
        self.oro = random.randint(1, 5)
        self.tipo = "enemigo_base"
        
        # Obtener la primera textura de la primera animación
        primera_animacion = list(animaciones_dict.keys())[0]
        primera_textura = animaciones_dict[primera_animacion][0]
        
        self.actor_animado = animaciones.ActorAnimado(
            primera_textura,  # imagen inicial
            pos,              # posición inicial  
            animaciones_dict, # diccionario de animaciones
            primera_animacion, # animación inicial
            0.1              # velocidad
        )
    
    def update(self, dt):
        super().update(dt)
        
        if self.follow:
            self.SeguirObjetivo()
    
    def SeguirObjetivo(self):
        if self.follow:
            fx = self.follow.x - self.x
            fy = self.follow.y - self.y

            if abs(fx) > 5:
                if fx > 0:
                    self.x += self.velocidad
                    self.cambiar_animacion("caminar_derecha")
                else:
                    self.x -= self.velocidad
                    self.cambiar_animacion("caminar_izquierda")   
            
            if abs(fy) > 5:
                if fy > 0:    
                    self.y += self.velocidad
                else:
                    self.y -= self.velocidad
                    
            if abs(fx) < 10 and abs(fy) < 10:
                # Determinar animación de quieto basada en la dirección actual
                anim_actual = self.actor_animado.get_animacion_actual()
                if "derecha" in anim_actual:
                    self.cambiar_animacion("quieto_derecha")
                else:
                    self.cambiar_animacion("quieto_izquierda")
    
    def recibir_daño(self, cantidad):
        """Recibe daño del jugador"""
        self.vida -= cantidad
        return self.vida <= 0
    
    def atacar(self, jugador, tiempo_actual):
        """Intenta atacar al jugador, devuelve True si atacó"""
        if tiempo_actual - self.tiempo_ultimo_ataque > self.velocidad_ataque:
            distancia = ((self.x - jugador.x)**2 + (self.y - jugador.y)**2)**0.5
            if distancia < 30:  # Rango de ataque
                self.tiempo_ultimo_ataque = tiempo_actual
                jugador.recibir_daño(self.daño)
                return True
        return False
    
    def soltar_recompensa(self):
        """Devuelve la recompensa al morir"""
        return {
            "experiencia": self.experiencia,
            "oro": self.oro,
            "tipo": self.tipo
        }
    
    def setFollow(self, nuevoFollow):
        self.follow = nuevoFollow
    
    def getFollow(self):
        return self.follow