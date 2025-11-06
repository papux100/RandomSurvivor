from personajes import Personaje
import animaciones

class Enemigo(Personaje):
    
    def __init__(self, experiencia, vida, velocidad, animaciones_dict, follow=None, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, animaciones_dict)
        self.follow = follow
    
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
                self.cambiar_animacion("quieto")
    
    def setFollow(self, nuevoFollow):
        self.follow = nuevoFollow
    
    def getFollow(self):
        return self.follow