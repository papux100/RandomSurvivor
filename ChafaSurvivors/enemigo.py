from personajes import Personaje
import animaciones
import random
import math

class Enemigo(Personaje):
    
    def __init__(self, experiencia, vida, velocidad, animaciones_dict, follow=None, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, animaciones_dict)
        self.follow = follow
        self.vida_max = vida
        self.daño = 5
        self.velocidad_ataque = 1.0
        self.tiempo_ultimo_ataque = 0
        self.oro = random.randint(1, 5)
        self.tipo = "enemigo_base"
        self.experiencia_otorgada = experiencia  # XP que otorga al morir
        
        # Ajustar XP según tipo de enemigo (se sobrescribirá en clases hijas)
        self.ajustar_xp_segun_tipo()
        
        # Obtener la primera textura de la primera animación
        primera_animacion = list(animaciones_dict.keys())[0]
        primera_textura = animaciones_dict[primera_animacion][0]
        
        self.actor_animado = animaciones.ActorAnimado(
            primera_textura,
            pos,
            animaciones_dict,
            primera_animacion,
            0.1
        )
        
        # Establecer posición inicial del mundo
        self.x = pos[0]
        self.y = pos[1]
    
    def ajustar_xp_segun_tipo(self):
        """Ajusta la experiencia otorgada según el tipo de enemigo"""
        # XP base según tipo (se sobrescribirá en clases específicas)
        if self.tipo == "zombie":
            self.experiencia_otorgada = 10
        elif self.tipo == "esqueleto":
            self.experiencia_otorgada = 15
        elif self.tipo == "brujo":
            self.experiencia_otorgada = 25
        elif self.tipo == "momia":
            self.experiencia_otorgada = 20
        elif self.tipo == "escorpion":
            self.experiencia_otorgada = 12
        elif self.tipo == "gusano":
            self.experiencia_otorgada = 8
        elif self.tipo == "templario":
            self.experiencia_otorgada = 40
        elif self.tipo == "angel_oscuro":
            self.experiencia_otorgada = 60
        elif self.tipo == "sacerdote":
            self.experiencia_otorgada = 35
        else:
            self.experiencia_otorgada = 10
    
    def update(self, dt):
        super().update(dt)
        
        if self.follow:
            self.SeguirObjetivo()
    
    def SeguirObjetivo(self):
        """Sigue al objetivo en coordenadas del MUNDO"""
        if self.follow:
            # Calcular diferencia en coordenadas del mundo
            fx = self.follow.x - self.x
            fy = self.follow.y - self.y
            
            # Calcular distancia en el mundo
            distancia = math.sqrt(fx**2 + fy**2)
            
            if distancia > 5:  # Sólo moverse si está lejos
                # Normalizar dirección
                if distancia > 0:
                    fx = fx / distancia
                    fy = fy / distancia
                
                # Mover en dirección al objetivo (coordenadas del mundo)
                self.x += fx * self.velocidad
                self.y += fy * self.velocidad
                
                # Cambiar animación basada en la dirección horizontal
                if fx > 0.1:  # Moviéndose a la derecha
                    self.cambiar_animacion("caminar_derecha")
                elif fx < -0.1:  # Moviéndose a la izquierda
                    self.cambiar_animacion("caminar_izquierda")
                else:
                    # Mantener la última animación de movimiento
                    anim_actual = self.actor_animado.get_animacion_actual()
                    if "izquierda" in anim_actual:
                        self.cambiar_animacion("quieto_izquierda")
                    else:
                        self.cambiar_animacion("quieto_derecha")
            else:
                # Está cerca, poner animación de quieto
                anim_actual = self.actor_animado.get_animacion_actual()
                if "izquierda" in anim_actual:
                    self.cambiar_animacion("quieto_izquierda")
                else:
                    self.cambiar_animacion("quieto_derecha")
    
    def recibir_daño(self, cantidad):
        """Recibe daño del jugador"""
        self.vida -= cantidad
        return self.vida <= 0
    
    def atacar(self, jugador, tiempo_actual):
        """Intenta atacar al jugador, devuelve True si atacó"""
        if tiempo_actual - self.tiempo_ultimo_ataque > self.velocidad_ataque:
            # Calcular distancia en coordenadas del mundo
            distancia = math.sqrt((self.x - jugador.x)**2 + (self.y - jugador.y)**2)
            
            if distancia < 30:  # Rango de ataque en el mundo
                self.tiempo_ultimo_ataque = tiempo_actual
                return jugador.recibir_daño(self.daño)
        return False
    
    def soltar_recompensa(self):
        """Devuelve la recompensa al morir"""
        return {
            "experiencia": self.experiencia_otorgada,
            "oro": self.oro,
            "tipo": self.tipo
        }
    
    def setFollow(self, nuevoFollow):
        self.follow = nuevoFollow
    
    def getFollow(self):
        return self.follow