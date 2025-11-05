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

    def crear_placeholder(self):
        """Crea una superficie de marcador de posición"""
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        surf.fill((255, 255, 0, 128))  # Amarillo semitransparente
        return surf

    def draw(self, surface):
        # Actualizar posición del rectángulo antes de dibujar
        self.rect.center = (self.x, self.y)
        surface.blit(self.image, self.rect)

    def collides_with_point(self, point):
        return self.rect.collidepoint(point)