import pygame
import os

# NO inicializar Pygame aquí, solo definir rutas
RUTA_IMAGENES = os.path.join("ChafaSurvivors", "images")

def cargar_imagen(nombre_archivo, tamaño=None):
    """Carga una imagen y la devuelve como superficie de Pygame"""
    ruta_completa = os.path.join(RUTA_IMAGENES, f"{nombre_archivo}.png")
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta_completa):
            print(f"Archivo no encontrado: {ruta_completa}")
            return crear_superficie_placeholder(nombre_archivo, tamaño)
            
        imagen = pygame.image.load(ruta_completa)
        # Convertir después de cargar
        if imagen.get_alpha():
            imagen = imagen.convert_alpha()
        else:
            imagen = imagen.convert()
        
        # Redimensionar si se especifica un tamaño
        if tamaño:
            imagen = pygame.transform.scale(imagen, tamaño)
            
        return imagen
    except pygame.error as e:
        print(f"No se pudo cargar la imagen: {ruta_completa}")
        print(f"Error: {e}")
        return crear_superficie_placeholder(nombre_archivo, tamaño)

def invertir_imagen(imagen):
    """Invierte horizontalmente una imagen"""
    return pygame.transform.flip(imagen, True, False)

def crear_superficie_placeholder(nombre, tamaño=None):
    """Crea una superficie de marcador de posición"""
    if tamaño is None:
        tamaño = (50, 50)
    
    surf = pygame.Surface(tamaño, pygame.SRCALPHA)
    
    # Colores diferentes para diferentes tipos de animación
    if 'idle' in nombre:
        color = (255, 0, 0, 128)  # Rojo para idle
    elif 'mov' in nombre:
        color = (0, 0, 255, 128)  # Azul para movimiento
    else:
        color = (0, 255, 0, 128)  # Verde para otros
    
    surf.fill(color)
    
    # Añadir texto para identificar
    font = pygame.font.Font(None, 20)
    text = font.render(nombre, True, (255, 255, 255))
    text_rect = text.get_rect(center=(tamaño[0]//2, tamaño[1]//2))
    surf.blit(text, text_rect)
    
    return surf

# Definir el tamaño deseado para las imágenes
TAMAÑO_PERSONAJE = (320, 320)  # Puedes ajustar este valor

texturas_personaje = {
    'quieto_derecha': [
        cargar_imagen('idle1', TAMAÑO_PERSONAJE),
        cargar_imagen('idle2', TAMAÑO_PERSONAJE), 
        cargar_imagen('idle3', TAMAÑO_PERSONAJE),
        cargar_imagen('idle4', TAMAÑO_PERSONAJE)
    ],
    'quieto_izquierda': [
        invertir_imagen(cargar_imagen('idle1', TAMAÑO_PERSONAJE)),
        invertir_imagen(cargar_imagen('idle2', TAMAÑO_PERSONAJE)), 
        invertir_imagen(cargar_imagen('idle3', TAMAÑO_PERSONAJE)),
        invertir_imagen(cargar_imagen('idle4', TAMAÑO_PERSONAJE))
    ],
    'caminar_derecha': [
        cargar_imagen('mov1', TAMAÑO_PERSONAJE),
        cargar_imagen('mov2', TAMAÑO_PERSONAJE),
        cargar_imagen('mov3', TAMAÑO_PERSONAJE),
        cargar_imagen('mov4', TAMAÑO_PERSONAJE),
        cargar_imagen('mov5', TAMAÑO_PERSONAJE),
        cargar_imagen('mov6', TAMAÑO_PERSONAJE),
        cargar_imagen('mov7', TAMAÑO_PERSONAJE),
        cargar_imagen('mov8', TAMAÑO_PERSONAJE)
    ],
    'caminar_izquierda': [
        invertir_imagen(cargar_imagen('mov1', TAMAÑO_PERSONAJE)),
        invertir_imagen(cargar_imagen('mov2', TAMAÑO_PERSONAJE)),
        invertir_imagen(cargar_imagen('mov3', TAMAÑO_PERSONAJE)),
        invertir_imagen(cargar_imagen('mov4', TAMAÑO_PERSONAJE)),
        invertir_imagen(cargar_imagen('mov5', TAMAÑO_PERSONAJE)),
        invertir_imagen(cargar_imagen('mov6', TAMAÑO_PERSONAJE)),
        invertir_imagen(cargar_imagen('mov7', TAMAÑO_PERSONAJE)),
        invertir_imagen(cargar_imagen('mov8', TAMAÑO_PERSONAJE))
    ],
}

print("Texturas cargadas correctamente")