import pygame
import os

# NO inicializar Pygame aquí, solo definir rutas
RUTA_IMAGENES = os.path.join("ChafaSurvivors", "images")

# Variables globales
_placeholder_font = None
_texturas_jugador_cache = None

def cargar_imagen(nombre_archivo, tamaño=None, usar_default=True):
    """Carga una imagen y la devuelve como superficie de Pygame"""
    ruta_completa = os.path.join(RUTA_IMAGENES, nombre_archivo)
    
    # Si no tiene extensión, agregar .png
    if not ruta_completa.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
        ruta_completa += ".png"
    
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta_completa):
            print(f"Archivo no encontrado: {ruta_completa}")
            if usar_default:
                # Cargar texturas del jugador como base
                return cargar_textura_jugador_como_default(nombre_archivo, tamaño)
            else:
                return crear_superficie_placeholder(nombre_archivo, tamaño)
            
        imagen = pygame.image.load(ruta_completa)
        
        # Redimensionar si se especifica un tamaño
        if tamaño:
            imagen = pygame.transform.scale(imagen, tamaño)
        
        # Optimizar la imagen
        if imagen.get_alpha():
            imagen = imagen.convert_alpha()
        else:
            imagen = imagen.convert()
            
        return imagen
    except pygame.error as e:
        print(f"No se pudo cargar la imagen: {ruta_completa}")
        print(f"Error: {e}")
        if usar_default:
            # Cargar texturas del jugador como base
            return cargar_textura_jugador_como_default(nombre_archivo, tamaño)
        else:
            return crear_superficie_placeholder(nombre_archivo, tamaño)

def cargar_textura_jugador_como_default(nombre_archivo, tamaño=None):
    """Carga una textura del jugador como base y la modifica según el tipo de enemigo"""
    # Primero intentar cargar texturas del jugador
    texturas_jugador = obtener_texturas_jugador()
    
    if tamaño is None:
        tamaño = (320, 320)
    
    # Determinar qué tipo de textura necesitamos basado en el nombre
    if 'idle' in nombre_archivo.lower() or 'quieto' in nombre_archivo.lower():
        # Usar textura idle del jugador
        if 'izquierda' in nombre_archivo.lower():
            base_surface = texturas_jugador['quieto_izquierda'][0]
        else:
            base_surface = texturas_jugador['quieto_derecha'][0]
    elif 'mov' in nombre_archivo.lower() or 'caminar' in nombre_archivo.lower():
        # Usar textura mov del jugador
        if 'izquierda' in nombre_archivo.lower():
            base_surface = texturas_jugador['caminar_izquierda'][0]
        else:
            base_surface = texturas_jugador['caminar_derecha'][0]
    else:
        # Por defecto usar idle derecha
        base_surface = texturas_jugador['quieto_derecha'][0]
    
    # Crear una copia de la superficie base
    surface = base_surface.copy()
    
    # Redimensionar si es necesario
    if tamaño != surface.get_size():
        surface = pygame.transform.scale(surface, tamaño)
    
    # Aplicar filtro de color según el tipo de enemigo
    surface = aplicar_filtro_color(surface, nombre_archivo)
    
    return surface

def aplicar_filtro_color(surface, nombre_archivo):
    """Aplica un filtro de color a la superficie según el tipo de enemigo"""
    # Crear una superficie temporal para aplicar el filtro
    filtered_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    filtered_surface.blit(surface, (0, 0))
    
    # Determinar filtro según el nombre del archivo o tipo de enemigo
    if 'zombie' in nombre_archivo.lower():
        # Filtro verde para zombie
        color_filter = pygame.Surface(surface.get_size())
        color_filter.fill((50, 150, 50, 100))  # Verde semitransparente
    elif 'esqueleto' in nombre_archivo.lower():
        # Filtro gris/blanco para esqueleto
        color_filter = pygame.Surface(surface.get_size())
        color_filter.fill((200, 200, 200, 100))  # Gris semitransparente
    elif 'brujo' in nombre_archivo.lower():
        # Filtro púrpura para brujo
        color_filter = pygame.Surface(surface.get_size())
        color_filter.fill((150, 50, 200, 100))  # Púrpura semitransparente
    elif 'momia' in nombre_archivo.lower():
        # Filtro marrón para momia
        color_filter = pygame.Surface(surface.get_size())
        color_filter.fill((150, 100, 50, 100))  # Marrón semitransparente
    elif 'escorpion' in nombre_archivo.lower():
        # Filtro naranja para escorpión
        color_filter = pygame.Surface(surface.get_size())
        color_filter.fill((200, 100, 50, 100))  # Naranja semitransparente
    elif 'gusano' in nombre_archivo.lower():
        # Filtro morado para gusano
        color_filter = pygame.Surface(surface.get_size())
        color_filter.fill((100, 50, 100, 100))  # Morado semitransparente
    elif 'templario' in nombre_archivo.lower():
        # Filtro azul para templario
        color_filter = pygame.Surface(surface.get_size())
        color_filter.fill((100, 150, 200, 100))  # Azul semitransparente
    elif 'angel_oscuro' in nombre_archivo.lower():
        # Filtro azul oscuro para ángel oscuro
        color_filter = pygame.Surface(surface.get_size())
        color_filter.fill((50, 50, 100, 100))  # Azul oscuro semitransparente
    elif 'sacerdote' in nombre_archivo.lower():
        # Filtro amarillo para sacerdote
        color_filter = pygame.Surface(surface.get_size())
        color_filter.fill((200, 200, 100, 100))  # Amarillo semitransparente
    else:
        # Sin filtro para tipos desconocidos
        return filtered_surface
    
    # Aplicar el filtro
    filtered_surface.blit(color_filter, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    return filtered_surface

def crear_superficie_placeholder(nombre, tamaño=None):
    """Crea una superficie de marcador de posición simple (para debugging)"""
    if tamaño is None:
        tamaño = (320, 320)
    
    surf = pygame.Surface(tamaño, pygame.SRCALPHA)
    
    # Colores diferentes para diferentes tipos de animación
    if 'idle' in nombre or 'quieto' in nombre:
        color = (255, 0, 0, 128)  # Rojo para idle
    elif 'mov' in nombre or 'caminar' in nombre:
        color = (0, 0, 255, 128)  # Azul para movimiento
    else:
        color = (0, 255, 0, 128)  # Verde para otros
    
    surf.fill(color)
    
    # Texto
    try:
        if _placeholder_font is None:
            _placeholder_font = pygame.font.Font(None, 20)
        
        text = _placeholder_font.render(nombre, True, (255, 255, 255))
        text_rect = text.get_rect(center=(tamaño[0]//2, tamaño[1]//2))
        surf.blit(text, text_rect)
    except:
        pass
    
    return surf

def invertir_imagen(imagen):
    """Invierte horizontalmente una imagen"""
    if isinstance(imagen, pygame.Surface):
        return pygame.transform.flip(imagen, True, False)
    return imagen

# Definir el tamaño deseado para las imágenes
TAMAÑO_PERSONAJE = (320, 320)
TAMAÑO_ENEMIGO = (320, 320)

def obtener_texturas_jugador():
    """Obtiene y cachea las texturas del jugador"""
    global _texturas_jugador_cache
    
    if _texturas_jugador_cache is not None:
        return _texturas_jugador_cache
    
    # Cargar texturas del jugador
    try:
        texturas_personaje = {
            'quieto_derecha': [
                cargar_imagen('idle1', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('idle2', TAMAÑO_PERSONAJE, usar_default=False), 
                cargar_imagen('idle3', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('idle4', TAMAÑO_PERSONAJE, usar_default=False)
            ],
            'quieto_izquierda': [
                invertir_imagen(cargar_imagen('idle1', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('idle2', TAMAÑO_PERSONAJE, usar_default=False)), 
                invertir_imagen(cargar_imagen('idle3', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('idle4', TAMAÑO_PERSONAJE, usar_default=False))
            ],
            'caminar_derecha': [
                cargar_imagen('mov1', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('mov2', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('mov3', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('mov4', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('mov5', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('mov6', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('mov7', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('mov8', TAMAÑO_PERSONAJE, usar_default=False)
            ],
            'caminar_izquierda': [
                invertir_imagen(cargar_imagen('mov1', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('mov2', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('mov3', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('mov4', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('mov5', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('mov6', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('mov7', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('mov8', TAMAÑO_PERSONAJE, usar_default=False))
            ],
        }
        
        # Verificar que todas las texturas sean superficies válidas
        for animacion, frames in texturas_personaje.items():
            for i, imagen in enumerate(frames):
                if not isinstance(imagen, pygame.Surface):
                    # Crear placeholder si no se cargó correctamente
                    print(f"Creando placeholder para {animacion} frame {i}")
                    texturas_personaje[animacion][i] = crear_superficie_placeholder(animacion, TAMAÑO_PERSONAJE)
        
        _texturas_jugador_cache = texturas_personaje
        print("Texturas del jugador cargadas correctamente")
        
    except Exception as e:
        print(f"Error cargando texturas del jugador: {e}")
        print("Creando texturas básicas del jugador...")
        
        # Crear texturas básicas si falla la carga
        _texturas_jugador_cache = {
            'quieto_derecha': [crear_superficie_placeholder('quieto_derecha', TAMAÑO_PERSONAJE)],
            'quieto_izquierda': [invertir_imagen(crear_superficie_placeholder('quieto_derecha', TAMAÑO_PERSONAJE))],
            'caminar_derecha': [crear_superficie_placeholder('caminar_derecha', TAMAÑO_PERSONAJE)],
            'caminar_izquierda': [invertir_imagen(crear_superficie_placeholder('caminar_derecha', TAMAÑO_PERSONAJE))]
        }
    
    return _texturas_jugador_cache

def inicializar_texturas():
    """Inicializa las texturas después de que Pygame esté inicializado"""
    # Simplemente devolver las texturas del jugador
    return obtener_texturas_jugador()

def obtener_textura_enemigo(tipo_enemigo):
    """Obtiene las texturas para un tipo específico de enemigo como diccionario de LISTAS"""
    # Primero obtener las texturas base del jugador
    texturas_base = obtener_texturas_jugador()
    
    # Crear un diccionario con texturas del jugador modificadas para el enemigo
    textura_correcta = {}
    
    for key, frames in texturas_base.items():
        # Aplicar filtro de color a cada frame según el tipo de enemigo
        frames_modificados = []
        for frame in frames:
            # Crear copia del frame
            frame_modificado = frame.copy()
            
            # Aplicar filtro de color según el tipo de enemigo
            frame_modificado = aplicar_filtro_color(frame_modificado, tipo_enemigo)
            
            frames_modificados.append(frame_modificado)
        
        textura_correcta[key] = frames_modificados
    
    return textura_correcta