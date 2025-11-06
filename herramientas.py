import pygame

class Actor(pygame.sprite.Sprite):
    def __init__(self, image, pos=(0, 0)):
        super().__init__()
        
        # Manejar diferentes tipos de entrada para image
        if isinstance(image, str):
            # Si es string, cargar la imagen
            try:
                self.image = pygame.image.load(image)
                if self.image.get_alpha():
                    self.image = self.image.convert_alpha()
                else:
                    self.image = self.image.convert()
            except:
                # Si falla, crear placeholder
                self.image = self.crear_placeholder()
        elif isinstance(image, pygame.Surface):
            # Si ya es una superficie, usarla directamente
            self.image = image
        else:
            # Por defecto, crear placeholder
            self.image = self.crear_placeholder()
            
        self.rect = self.image.get_rect(center=pos)
        self.x = pos[0]
        self.y = pos[1]
        
        # Hitbox por defecto (mismo tamaño que la imagen)
        self.hitbox = self.rect.copy()
        
        # Offset de la hitbox (para ajustar posición relativa)
        self.hitbox_offset = (0, 0)

    def crear_placeholder(self):
        """Crea una superficie de marcador de posición"""
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        surf.fill((255, 255, 0, 128))  # Amarillo semitransparente
        return surf

    def set_hitbox(self, tamaño, offset=(0, 0)):
        """
        Define una hitbox personalizada
        tamaño: (ancho, alto) de la hitbox
        offset: (x, y) desplazamiento desde el centro del sprite
        """
        self.hitbox_offset = offset
        # Crear nueva hitbox centrada en la posición actual con el tamaño especificado
        center_x = self.x + offset[0]
        center_y = self.y + offset[1]
        self.hitbox = pygame.Rect(0, 0, tamaño[0], tamaño[1])
        self.hitbox.center = (center_x, center_y)

    def set_hitbox_relative(self, rect_relativo):
        """
        Define una hitbox basada en coordenadas relativas a la imagen
        rect_relativo: (x, y, ancho, alto) relativo al centro del sprite
        """
        center_x = self.x + rect_relativo[0]
        center_y = self.y + rect_relativo[1]
        self.hitbox = pygame.Rect(0, 0, rect_relativo[2], rect_relativo[3])
        self.hitbox.center = (center_x, center_y)
        self.hitbox_offset = (rect_relativo[0], rect_relativo[1])

    def update_hitbox(self):
        """Actualiza la posición de la hitbox cuando el sprite se mueve"""
        self.hitbox.center = (self.x + self.hitbox_offset[0], 
                             self.y + self.hitbox_offset[1])

    def draw(self, surface):
        # Actualizar posición del rectángulo antes de dibujar
        self.rect.center = (self.x, self.y)
        self.update_hitbox()  # Actualizar hitbox también
        surface.blit(self.image, self.rect)

    def draw_hitbox(self, surface, color=(255, 0, 0)):
        """Dibuja la hitbox para debugging"""
        pygame.draw.rect(surface, color, self.hitbox, 2)  # Rectángulo rojo de 2px

    def collides_with_point(self, point):
        return self.hitbox.collidepoint(point)

    def collides_with_actor(self, other_actor):
        """Verifica colisión con otro Actor (usando hitboxes)"""
        return self.hitbox.colliderect(other_actor.hitbox)

    def collides_with_rect(self, rect):
        """Verifica colisión con un rectángulo"""
        return self.hitbox.colliderect(rect)