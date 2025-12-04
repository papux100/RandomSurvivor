import pygame
import os
import re

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
TAMAÑO_PERSONAJE = (60, 60)
TAMAÑO_ENEMIGO = (60, 60)

def obtener_texturas_jugador():
    """Obtiene y cachea las texturas del jugador"""
    global _texturas_jugador_cache
    
    if _texturas_jugador_cache is not None:
        return _texturas_jugador_cache
    
    # Cargar texturas del jugador
    try:
        texturas_personaje = {
            'quieto_derecha': [
                cargar_imagen('Caballero\idle\idle0.png', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('Caballero\idle\idle1.png', TAMAÑO_PERSONAJE, usar_default=False), 
                cargar_imagen('Caballero\idle\idle0.png', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('Caballero\idle\idle1.png', TAMAÑO_PERSONAJE, usar_default=False) 
            ],
            'quieto_izquierda': [
                invertir_imagen(cargar_imagen('Caballero\idle\idle0.png', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('Caballero\idle\idle1.png', TAMAÑO_PERSONAJE, usar_default=False)), 
                invertir_imagen(cargar_imagen('Caballero\idle\idle0.png', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('Caballero\idle\idle1.png', TAMAÑO_PERSONAJE, usar_default=False)) 
            ],
            'caminar_derecha': [
                cargar_imagen('Caballero\mov\mov0.png', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('Caballero\mov\mov1.png', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('Caballero\mov\mov2.png', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('Caballero\mov\mov3.png', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('Caballero\mov\mov4.png', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('Caballero\mov\mov5.png', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('Caballero\mov\mov6.png', TAMAÑO_PERSONAJE, usar_default=False),
                cargar_imagen('Caballero\mov\mov7.png', TAMAÑO_PERSONAJE, usar_default=False)
            ],
            'caminar_izquierda': [
                invertir_imagen(cargar_imagen('Caballero\mov\mov0.png', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('Caballero\mov\mov1.png', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('Caballero\mov\mov2.png', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('Caballero\mov\mov3.png', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('Caballero\mov\mov4.png', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('Caballero\mov\mov5.png', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('Caballero\mov\mov6.png', TAMAÑO_PERSONAJE, usar_default=False)),
                invertir_imagen(cargar_imagen('Caballero\mov\mov7.png', TAMAÑO_PERSONAJE, usar_default=False))
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

def obtener_texturas_enemigo(tipo_enemigo):
    """Obtiene las texturas para un tipo específico de enemigo desde carpetas"""
    
    # Mapeo de nombres de carpetas
    carpetas_enemigos = {
        "zombie": "Zombi",
        "esqueleto": "Esqueleto",
        "brujo": "Mago",
        "momia": "Momia",
        "escorpion": "Escorpion",
        "gusano": "Gusano",
        "templario": "Vampiro",
        "angel_oscuro": "AngelOscuro",
        "sacerdote": "Sacerdote",
    }
    
    # Obtener nombre de carpeta
    nombre_carpeta = carpetas_enemigos.get(tipo_enemigo.lower())
    if not nombre_carpeta:
        print(f"Tipo de enemigo '{tipo_enemigo}' no reconocido. Usando texturas por defecto.")
        return obtener_texturas_jugador()  # Fallback a texturas del jugador
    
    texturas_enemigo = {
        'quieto_derecha': [],
        'quieto_izquierda': [],
        'caminar_derecha': [],
        'caminar_izquierda': []
    }
    
    try:
        # Cargar animación idle (quieto)
        ruta_idle = os.path.join(RUTA_IMAGENES, nombre_carpeta, "idle")
        if os.path.exists(ruta_idle):
            archivos_idle = sorted([f for f in os.listdir(ruta_idle) 
                                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
            
            for archivo in archivos_idle:
                # Construir ruta relativa para cargar_imagen
                ruta_relativa = os.path.join(nombre_carpeta, "idle", archivo)
                try:
                    # Usar cargar_imagen que ya maneja tamaño y errores
                    imagen = cargar_imagen(ruta_relativa, TAMAÑO_ENEMIGO, usar_default=False)
                    texturas_enemigo['quieto_derecha'].append(imagen)
                    texturas_enemigo['quieto_izquierda'].append(invertir_imagen(imagen))
                except Exception as e:
                    print(f"Error cargando {ruta_relativa}: {e}")
                    # Crear placeholder si falla
                    placeholder = crear_superficie_placeholder(f"{tipo_enemigo}_idle", TAMAÑO_ENEMIGO)
                    texturas_enemigo['quieto_derecha'].append(placeholder)
                    texturas_enemigo['quieto_izquierda'].append(invertir_imagen(placeholder))
        else:
            print(f"Advertencia: No se encontró carpeta 'idle' en {os.path.join(RUTA_IMAGENES, nombre_carpeta)}")
            # Crear frames por defecto
            for i in range(4):
                placeholder = crear_superficie_placeholder(f"{tipo_enemigo}_idle_{i}", TAMAÑO_ENEMIGO)
                texturas_enemigo['quieto_derecha'].append(placeholder)
                texturas_enemigo['quieto_izquierda'].append(invertir_imagen(placeholder))
        
        # Cargar animación mov (caminar)
        ruta_mov = os.path.join(RUTA_IMAGENES, nombre_carpeta, "mov")
        if os.path.exists(ruta_mov):
            archivos_mov = sorted([f for f in os.listdir(ruta_mov) 
                                 if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
            
            for archivo in archivos_mov:
                # Construir ruta relativa para cargar_imagen
                ruta_relativa = os.path.join(nombre_carpeta, "mov", archivo)
                try:
                    # Usar cargar_imagen que ya maneja tamaño y errores
                    imagen = cargar_imagen(ruta_relativa, TAMAÑO_ENEMIGO, usar_default=False)
                    texturas_enemigo['caminar_derecha'].append(imagen)
                    texturas_enemigo['caminar_izquierda'].append(invertir_imagen(imagen))
                except Exception as e:
                    print(f"Error cargando {ruta_relativa}: {e}")
                    # Crear placeholder si falla
                    placeholder = crear_superficie_placeholder(f"{tipo_enemigo}_mov", TAMAÑO_ENEMIGO)
                    texturas_enemigo['caminar_derecha'].append(placeholder)
                    texturas_enemigo['caminar_izquierda'].append(invertir_imagen(placeholder))
        else:
            print(f"Advertencia: No se encontró carpeta 'mov' en {os.path.join(RUTA_IMAGENES, nombre_carpeta)}")
            # Crear frames por defecto
            for i in range(8):
                placeholder = crear_superficie_placeholder(f"{tipo_enemigo}_mov_{i}", TAMAÑO_ENEMIGO)
                texturas_enemigo['caminar_derecha'].append(placeholder)
                texturas_enemigo['caminar_izquierda'].append(invertir_imagen(placeholder))
        
        # Verificar que tenemos al menos un frame en cada animación
        for animacion in texturas_enemigo:
            if len(texturas_enemigo[animacion]) == 0:
                print(f"Advertencia: Animación {animacion} vacía para {tipo_enemigo}")
                placeholder = crear_superficie_placeholder(f"{tipo_enemigo}_{animacion}", TAMAÑO_ENEMIGO)
                texturas_enemigo[animacion].append(placeholder)
        
        print(f"Texturas de {tipo_enemigo} cargadas correctamente desde carpetas")
        return texturas_enemigo
        
    except Exception as e:
        print(f"Error cargando texturas para {tipo_enemigo}: {e}")
        print("Usando texturas del jugador como fallback")
        return obtener_texturas_jugador()
    
def cargar_imagen_desde_ruta(ruta_completa, tamaño=None, usar_default=True):
    """Carga una imagen desde una ruta completa"""
    try:
        if not os.path.exists(ruta_completa):
            if usar_default:
                return crear_superficie_placeholder(os.path.basename(ruta_completa), tamaño)
            else:
                raise FileNotFoundError(f"Archivo no encontrado: {ruta_completa}")
        
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
            return crear_superficie_placeholder(os.path.basename(ruta_completa), tamaño)
        else:
            raise

def inicializar_texturas():
    """Inicializa las texturas después de que Pygame esté inicializado"""
    # Simplemente devolver las texturas del jugador
    return obtener_texturas_jugador()

def obtener_textura_enemigo(tipo_enemigo):
    """Obtiene las texturas para un tipo específico de enemigo como diccionario de LISTAS"""
    
    # Primero intentar cargar desde carpetas específicas
    texturas_cargadas = obtener_texturas_enemigo(tipo_enemigo)
    
    # Si se cargaron correctamente desde carpetas, devolverlas
    if texturas_cargadas and len(texturas_cargadas['quieto_derecha']) > 0:
        return texturas_cargadas
    
    # Fallback: usar el método antiguo (texturas del jugador con filtro de color)
    print(f"Usando fallback para {tipo_enemigo}...")
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


def obtener_archivos_animacion(ruta_carpeta):
    """Obtiene los archivos de animación ordenados de una carpeta"""
    if not os.path.exists(ruta_carpeta):
        return []
    
    archivos = []
    for archivo in os.listdir(ruta_carpeta):
        if archivo.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            archivos.append(archivo)
    
    # Ordenar naturalmente (para que frame1, frame2, frame10 se ordenen correctamente)
    archivos.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
    return archivos

def crear_animacion_desde_secuencia(tipo_enemigo, nombre_animacion, cantidad_frames, tamaño=None):
    """Crea una animación desde una secuencia de frames numerados"""
    if tamaño is None:
        tamaño = TAMAÑO_ENEMIGO
    
    frames = []
    for i in range(1, cantidad_frames + 1):
        # Intentar diferentes formatos de nombres
        posibles_nombres = [
            f"{nombre_animacion}{i}.png",
            f"{nombre_animacion}_{i}.png",
            f"frame{i}.png",
            f"{i}.png"
        ]
        
        frame_cargado = False
        for nombre_archivo in posibles_nombres:
            ruta_completa = os.path.join(RUTA_IMAGENES, tipo_enemigo, nombre_animacion, nombre_archivo)
            if os.path.exists(ruta_completa):
                try:
                    imagen = cargar_imagen_desde_ruta(ruta_completa, tamaño, usar_default=False)
                    frames.append(imagen)
                    frame_cargado = True
                    break
                except:
                    continue
        
        # Si no se pudo cargar, crear placeholder
        if not frame_cargado:
            placeholder = crear_superficie_placeholder(f"{tipo_enemigo}_{nombre_animacion}_{i}", tamaño)
            frames.append(placeholder)
    
    return frames