#main
from menu import *
import pygame
import sys
import random
import math
import os

# Importar los módulos del juego
from personajes import Personaje
from enemigo import Enemigo
import texturas
from colisiones import manejar_colisiones
from enemigos_tipos import EnemigoFactory
from poder import PoderFactory, ProyectilFuego, EspadaOrbitante, RayoElectro, CampoMag, AuraSag,AuraSagrada, LanzaHieloProyectil
from portal import Portal  # Nueva importación
from fondo_mosaico import FondoMosaico

# Inicializar Pygame PRIMERO
pygame.init()
inicializacion_menu()

# Obtener dimensiones de pantalla desde variables globales
WIDTH, HEIGHT = Variables_Globales["RESOLUTION"]

# Importar texturas DESPUÉS de Pygame
texturas_personaje = texturas.inicializar_texturas()

# Variables del juego
running = True
en_juego = False
protagonista = None
enemigos = []
efectos_activos = []
portales = []  
mostrando_game_over = False
tiempo_ultimo_enemigo = 0
intervalo_enemigos = 3.0
actual_animacion = "quieto_derecha"
clock = pygame.time.Clock()
mensaje_poder = ""
tiempo_mensaje = 0
duracion_mensaje = 3.0
nivel_juego = 1
fondo_mosaico = None
tiempo_juego = 0
enemigos_derrotados = 0
experiencia_total = 0
enemigos_por_mundo = {}  # Llevar conteo por mundo
estadisticas_finales = {}

# Variables de cámara
camera_offset_x = 0
camera_offset_y = 0
camera_smoothness = 0.1

# Fuentes escalables
font_pequena = None
font_mediana = None
font_grande = None

def actualizar_fuentes():
    """Actualiza las fuentes según la resolución actual"""
    global font_pequena, font_mediana, font_grande
    screen_height = Variables_Globales["RESOLUTION"][1]
    
    font_pequena = pygame.font.SysFont(None, int(screen_height * 0.025))
    font_mediana = pygame.font.SysFont(None, int(screen_height * 0.04))
    font_grande = pygame.font.SysFont(None, int(screen_height * 0.06))

actualizar_fuentes()

MAX_EFECTOS_ACTIVOS = 100

# Colores para los enemigos según tipo
COLORES_ENEMIGOS = {
    "zombie": (50, 150, 50),
    "esqueleto": (200, 200, 200),
    "brujo": (150, 50, 200),
    "momia": (150, 100, 50),
    "escorpion": (200, 100, 50),
    "gusano": (100, 50, 100),
    "templario": (100, 150, 200),
    "angel_oscuro": (50, 50, 100),
    "sacerdote": (200, 200, 100)
}

def actualizar_camara():
    """Actualiza la posición de la cámara para seguir al jugador"""
    global camera_offset_x, camera_offset_y
    
    if protagonista:
        target_offset_x = WIDTH // 2 - protagonista.x
        target_offset_y = HEIGHT // 2 - protagonista.y
        
        camera_offset_x += (target_offset_x - camera_offset_x) * camera_smoothness
        camera_offset_y += (target_offset_y - camera_offset_y) * camera_smoothness

def inicializar_juego():
    global protagonista, enemigos, tiempo_ultimo_enemigo, actual_animacion
    global efectos_activos, nivel_juego, tiempo_juego, enemigos_derrotados, experiencia_total
    global camera_offset_x, camera_offset_y, portales, enemigos_por_mundo
    global mostrando_game_over, estadisticas_finales,fondo_mosaico  # Agregar estas
    
    # Resetear variables de Game Over
    mostrando_game_over = False
    estadisticas_finales = {}
    
    # Inicializar fondo mosaico
    fondo_mosaico = FondoMosaico(Variables_Globales["MUNDO_ACTUAL"])
    
    # Resetear variables
    camera_offset_x = 0
    camera_offset_y = 0
    portales = []
    enemigos_por_mundo = {mundo: 0 for mundo in ENEMIGOS_POR_MUNDO.keys()}
    
    # Crear el personaje principal
    protagonista = Personaje(0, 100, 4, texturas_personaje)
    actual_animacion = "quieto_derecha"
    
    # Posicionar al jugador
    protagonista.x = 0
    protagonista.y = 0
    
    # Ajustar velocidad según resolución
    base_speed = 4
    scale_factor = WIDTH / 1280
    protagonista.velocidad = base_speed * scale_factor * 0.8
    protagonista.velocidad_base = protagonista.velocidad
    
    # Configurar hitbox
    hitbox_width = int(30 * scale_factor)
    hitbox_height = int(40 * scale_factor)
    protagonista.set_hitbox((hitbox_width, hitbox_height), (0, int(5 * scale_factor)))
    
    # Limpiar listas
    enemigos = []
    efectos_activos = []
    
    # Reiniciar estadísticas
    nivel_juego = 1
    tiempo_juego = 0
    enemigos_derrotados = 0
    experiencia_total = 0
    
    # Establecer mundo inicial
    Variables_Globales["MUNDO_ACTUAL"] = "bosque"
    Variables_Globales["MUNDO_ANTERIOR"] = None
    Variables_Globales["EN_ENDLESS"] = False
    Variables_Globales["PARTIDA_COMPLETADA"] = False
    
    # Generar enemigos iniciales del bosque
    generar_enemigos_mundo_actual()
    
    tiempo_ultimo_enemigo = 0
    
    # Dar un poder inicial al jugador
    poder_inicial = PoderFactory.crear_poder("bola_fuego")
    resultado = protagonista.agregar_poder(poder_inicial)
    mostrar_mensaje(resultado)

def generar_enemigos_mundo_actual():
    """Genera enemigos según el mundo actual"""
    global enemigos
    
    mundo = Variables_Globales["MUNDO_ACTUAL"]
    
    # Limpiar enemigos existentes (excepto si es endless y queremos mantener algunos)
    if not Variables_Globales["EN_ENDLESS"]:
        enemigos = []
    
    # Determinar cuántos enemigos generar
    base_enemies = 5
    if Variables_Globales["EN_ENDLESS"]:
        base_enemies = 8  # Más enemigos en endless
    
    extra_enemies = int((WIDTH * HEIGHT) / (1280 * 720)) - 1
    total_enemies = base_enemies + extra_enemies
    
    # Tipos de enemigos permitidos en este mundo
    tipos_permitidos = ENEMIGOS_POR_MUNDO[mundo]
    
    for _ in range(total_enemies):
        # Solo generar si hay tipos permitidos
        if tipos_permitidos:
            tipo = random.choice(tipos_permitidos)
            enemigo = generar_enemigo_tipo(tipo)
            
            if enemigo:
                enemigos.append(enemigo)
                enemigos_por_mundo[mundo] += 1

def generar_enemigo_tipo(tipo):
    """Genera un enemigo de un tipo específico alrededor del jugador"""
    if not protagonista:
        return None
    
    # Radio de aparición
    min_radius = int(400 * (WIDTH / 1280))
    max_radius = int(800 * (WIDTH / 1280))
    radio = random.randint(min_radius, max_radius)
    
    # Ángulo aleatorio
    angulo = random.uniform(0, 2 * math.pi)
    
    # Calcular posición relativa al jugador
    x = protagonista.x + radio * math.cos(angulo)
    y = protagonista.y + radio * math.sin(angulo)
    
    # Crear el enemigo
    nuevo_enemigo = EnemigoFactory.crear_enemigo(tipo, nivel_juego, (x, y))
    
    # Ajustar velocidad según resolución
    scale_factor = WIDTH / 1280
    nuevo_enemigo.velocidad *= scale_factor * 0.8
    
    # Configurar follow y hitbox
    nuevo_enemigo.setFollow(protagonista)
    hitbox_width = int(30 * scale_factor)
    hitbox_height = int(40 * scale_factor)
    nuevo_enemigo.set_hitbox((hitbox_width, hitbox_height), (0, int(5 * scale_factor)))
    
    return nuevo_enemigo

def generar_enemigo_alrededor():
    """Genera un enemigo aleatorio del mundo actual alrededor del jugador"""
    mundo = Variables_Globales["MUNDO_ACTUAL"]
    tipos_permitidos = ENEMIGOS_POR_MUNDO[mundo]
    
    if not tipos_permitidos or not protagonista:
        return None
    
    tipo = random.choice(tipos_permitidos)
    return generar_enemigo_tipo(tipo)

def verificar_portales():
    """Verifica si se deben generar portales y gestiona los existentes"""
    global portales
    
    mundo = Variables_Globales["MUNDO_ACTUAL"]
    nivel_jugador = protagonista.nivel if protagonista else 0
    
    # Limpiar portales antiguos solo si no hay ninguno activo
    # NO limpiar si ya hay un portal generado
    if not portales:
        portales = []
    
    # Verificar si ya hay un portal del tipo que necesitamos
    portal_existente = None
    for portal in portales:
        if portal.tipo == "azul":
            portal_existente = portal
            break
    
    # Si ya existe un portal, no generar otro
    if portal_existente:
        return
    
    # Verificar si se cumplen los requisitos para avanzar
    if mundo in REQUISITOS_MUNDO:
        requisito = REQUISITOS_MUNDO[mundo]
        
        if nivel_jugador >= requisito["nivel"]:
            # Generar portal azul para avanzar (una sola vez)
            if not any(p.tipo == "azul" for p in portales):
                generar_portal_avance(requisito["mundo_siguiente"])
    
    # En catedral nivel 30, mostrar portal rojo para terminar
    if mundo == "catedral" and nivel_jugador >= 30 and not Variables_Globales["EN_ENDLESS"]:
        if not any(p.tipo == "rojo" for p in portales):
            generar_portal_salida()
            
            # En endless mode, también mostrar portal azul para volver al bosque
            if Variables_Globales["EN_ENDLESS"]:
                if not any(p.tipo == "azul" for p in portales):
                    generar_portal_avance("endless")
                    
    if mundo == "endless":
        if not any(p.tipo == "rojo" for p in portales):
            generar_portal_salida()
            

def generar_portal_avance(mundo_destino):
    """Genera un portal azul para avanzar al siguiente mundo"""
    if not protagonista:
        return
    
    # Verificar que no haya ya un portal azul
    if any(p.tipo == "azul" for p in portales):
        return
    
    # Posicionar portal a cierta distancia del jugador (posición fija)
    distancia_portal = 200  # Radio fijo
    angulo = random.uniform(0, 2 * math.pi)
    
    portal_x = protagonista.x + distancia_portal * math.cos(angulo)
    portal_y = protagonista.y + distancia_portal * math.sin(angulo)
    
    portal = Portal(portal_x, portal_y, "azul", mundo_destino)
    portales.append(portal)
    
    mostrar_mensaje(f"¡Portal a {mundo_destino.capitalize()} disponible!")

def generar_portal_salida():
    """Genera un portal rojo para terminar la partida"""
    if not protagonista:
        return
    
    # Verificar que no haya ya un portal rojo
    if any(p.tipo == "rojo" for p in portales):
        return
    
    # Posicionar portal en dirección diferente al portal azul (si existe)
    distancia_portal = 200
    angulo = random.uniform(0, 2 * math.pi)
    
    # Si hay portal azul, poner el rojo en dirección opuesta
    portal_azul = next((p for p in portales if p.tipo == "azul"), None)
    if portal_azul:
        # Calcular dirección opuesta al portal azul
        dx = portal_azul.x - protagonista.x
        dy = portal_azul.y - protagonista.y
        angulo = math.atan2(dy, dx) + math.pi  # Dirección opuesta
    
    portal_x = protagonista.x + distancia_portal * math.cos(angulo)
    portal_y = protagonista.y + distancia_portal * math.sin(angulo)
    
    portal = Portal(portal_x, portal_y, "rojo", "menu")
    portales.append(portal)
    
    mostrar_mensaje("¡Portal de salida disponible!")

def cambiar_mundo(nuevo_mundo):
    """Cambia al jugador a un nuevo mundo"""
    global enemigos, efectos_activos, portales, fondo_mosaico  # Agregar fondo_mosaico
    
    if nuevo_mundo not in ENEMIGOS_POR_MUNDO:
        return False
    
    # Guardar mundo anterior
    Variables_Globales["MUNDO_ANTERIOR"] = Variables_Globales["MUNDO_ACTUAL"]
    
    # Actualizar mundo actual
    Variables_Globales["MUNDO_ACTUAL"] = nuevo_mundo
    
    # Actualizar fondo mosaico
    if fondo_mosaico:
        fondo_mosaico.cambiar_mundo(nuevo_mundo)
    
    # Si vamos a endless mode desde catedral nivel 30
    if nuevo_mundo == "endless":
        Variables_Globales["EN_ENDLESS"] = True
        Variables_Globales["PARTIDA_COMPLETADA"] = True
        mostrar_mensaje("¡MODO ENDLESS DESBLOQUEADO!")
    elif nuevo_mundo == "bosque" and Variables_Globales["EN_ENDLESS"]:
        # En endless mode, mantener el estado endless
        pass
    
    # Limpiar enemigos y efectos
    enemigos = []
    efectos_activos = []
    portales = []  # Limpiar portales también
    
    # Generar nuevos enemigos del mundo
    generar_enemigos_mundo_actual()
    
    # Reposicionar al jugador en el centro
    if protagonista:
        protagonista.x = 0
        protagonista.y = 0
    
    mostrar_mensaje(f"Bienvenido al {nuevo_mundo.capitalize()}!")
    return True

def mostrar_mensaje(texto):
    """Muestra un mensaje temporal en pantalla"""
    global mensaje_poder, tiempo_mensaje
    mensaje_poder = texto
    tiempo_mensaje = duracion_mensaje

def actualizar_juego():
    """Actualiza la lógica del juego"""
    global tiempo_ultimo_enemigo, actual_animacion, nivel_juego, tiempo_juego
    global enemigos_derrotados, experiencia_total, tiempo_mensaje, efectos_activos
    
    dt = clock.tick(60) / 1000.0
    tiempo_juego += dt
    
    # Actualizar cámara
    actualizar_camara()
    
    # Limitar efectos activos
    if len(efectos_activos) > MAX_EFECTOS_ACTIVOS:
        efectos_activos = efectos_activos[-MAX_EFECTOS_ACTIVOS:]
    
    # Actualizar tiempo del mensaje
    if tiempo_mensaje > 0:
        tiempo_mensaje -= dt
    
    # Actualizar portales (solo animación, no posición)
    for portal in portales:
        portal.update(dt)  # Solo actualiza animación
    
    # Verificar colisiones con portales
    if protagonista:
        for portal in portales[:]:
            if portal.verificar_colision(protagonista.x, protagonista.y):
                manejar_colision_portal(portal)
                break
    
    #personaje muere
    if protagonista.vida <= 0:
        terminar_partida()
    
    # Verificar si se deben generar nuevos portales (solo cada cierto tiempo)
    # Para evitar generación constante, verificamos solo cada 2 segundos
    if tiempo_juego % 2.0 < dt:  # Aproximadamente cada 2 segundos
        verificar_portales()
    
    # Manejar entrada del teclado
    keys = pygame.key.get_pressed()
    
    # Movimiento del personaje
    movimiento = False
    if keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d]:
        movimiento = True
        if keys[pygame.K_w]:
            protagonista.y -= protagonista.velocidad
            if actual_animacion == "quieto_derecha":
                protagonista.cambiar_animacion("caminar_derecha")
            else:
                protagonista.cambiar_animacion("caminar_izquierda")
        if keys[pygame.K_a]:
            protagonista.x -= protagonista.velocidad
            actual_animacion = "quieto_izquierda"
            if actual_animacion == "quieto_derecha":
                protagonista.cambiar_animacion("caminar_derecha")
            else:
                protagonista.cambiar_animacion("caminar_izquierda")
        if keys[pygame.K_s]:
            protagonista.y += protagonista.velocidad
            if actual_animacion == "quieto_derecha":
                protagonista.cambiar_animacion("caminar_derecha")
            else:
                protagonista.cambiar_animacion("caminar_izquierda")
        if keys[pygame.K_d]:
            protagonista.x += protagonista.velocidad
            actual_animacion = "quieto_derecha"
            if actual_animacion == "quieto_derecha":
                protagonista.cambiar_animacion("caminar_derecha")
            else:
                protagonista.cambiar_animacion("caminar_izquierda")
    
    if not movimiento:
        protagonista.cambiar_animacion(actual_animacion)
    
    # Actualizar animaciones
    protagonista.update(dt)
    
    # Actualizar enemigos y verificar colisiones
    tiempo_actual = pygame.time.get_ticks() / 1000.0
    enemigos_a_eliminar = []
    xp_obtenida = 0
    
    for enemigo in enemigos:
        enemigo.update(dt)
        
        # Verificar colisión con efectos
        for efecto in efectos_activos[:]:
            if hasattr(efecto, 'x') and hasattr(efecto, 'y') and hasattr(efecto, 'radio'):
                distancia = math.hypot(efecto.x - enemigo.x, efecto.y - enemigo.y)
                if distancia < efecto.radio + 20:
                    if hasattr(efecto, 'aplicar_daño'):
                        if efecto.aplicar_daño(enemigo):
                            enemigos_a_eliminar.append(enemigo)
                            # Obtener XP del enemigo
                            xp_enemigo = getattr(enemigo, 'experiencia_otorgada', 10)
                            xp_obtenida += xp_enemigo
                            experiencia_total += xp_enemigo
                            break
        
        # Verificar ataque del enemigo al jugador
        if hasattr(enemigo, 'atacar'):
            if enemigo.atacar(protagonista, tiempo_actual):
                if protagonista.recibir_daño(enemigo.daño):
                    game_over()
                    return
    
    # Eliminar enemigos muertos y otorgar experiencia
    for enemigo in enemigos_a_eliminar:
        if enemigo in enemigos:
            # Obtener recompensa del enemigo
            recompensa = enemigo.soltar_recompensa()
            xp_enemigo = recompensa["experiencia"]
            
            # Otorgar experiencia al jugador
            subio_nivel = protagonista.ganar_experiencia(xp_enemigo)
            
            if subio_nivel:
                # El jugador subió de nivel
                nivel_actual = protagonista.nivel
                mostrar_mensaje(f"¡Nivel {nivel_actual}!")
                
                # Intentar mostrar información del poder obtenido (pero no bloquear)
                try:
                    if hasattr(protagonista, 'poderes') and protagonista.poderes:
                        # Obtener el último poder (podría ser el nuevo)
                        ultimo_poder = protagonista.poderes[-1]
                        if hasattr(ultimo_poder, 'nombre'):
                            mostrar_mensaje(f"¡Nivel {nivel_actual}! - {ultimo_poder.nombre}")
                except:
                    pass  # Si hay error, solo mostrar el nivel
            
            enemigos.remove(enemigo)
            enemigos_derrotados += 1
    
    # Mostrar XP obtenida si hay
    if xp_obtenida > 0:
        # Puedes mostrar un mensaje flotante de XP aquí si quieres
        pass
    
    # Manejar colisiones físicas
    manejar_colisiones(protagonista, enemigos)
    
    # Actualizar y usar poderes
    if hasattr(protagonista, 'poderes'):
        for poder in protagonista.poderes:
            # Manejo especial para Aura Sagrada
            if isinstance(poder, AuraSagrada):
                # Usar el método mantener_aura para asegurar que esté activa
                aura = poder.mantener_aura(protagonista)
                if aura and aura not in efectos_activos:
                    efectos_activos.append(aura)
                continue
            
            # Para otros poderes, usar normalmente
            if hasattr(poder, 'usar'):
                efectos = poder.usar(protagonista, enemigos, tiempo_actual)
                
                # Para AuraSag, reemplazar si ya existe
                if any(isinstance(ef, AuraSag) for ef in efectos):
                    efectos_activos = [ef for ef in efectos_activos if not isinstance(ef, AuraSag)]
                
                efectos_activos.extend(efectos)
    
    # Actualizar efectos activos
    efectos_a_eliminar = []
    for efecto in efectos_activos:
        # Para AuraSag, actualizar de manera especial
        if isinstance(efecto, AuraSag):
            # Siempre actualizar la aura, nunca la elimines
            efecto.update(dt, protagonista, enemigos)
            continue
        
        # Para otros efectos, usar lógica normal
        if not efecto.update(dt, protagonista, enemigos):
            efectos_a_eliminar.append(efecto)

    # Eliminar efectos muertos
    for efecto in efectos_a_eliminar:
        if efecto in efectos_activos:
            efectos_activos.remove(efecto)
    
    # Generar nuevos enemigos periódicamente
    tiempo_actual = pygame.time.get_ticks() / 1000.0
    # Calcular intervalo basado en nivel del jugador
    intervalo_base = 3.0  # 3 segundos base
    nivel_jugador = protagonista.nivel if protagonista else 1
    reduccion_por_nivel = 0.1  # Reduce 0.1 segundos por nivel
    intervalo_actual = max(0.5, intervalo_base - (nivel_jugador * reduccion_por_nivel))  # Mínimo 0.5 segundos

    if tiempo_actual - tiempo_ultimo_enemigo > intervalo_actual:
        # Generar enemigos (también aumentar cantidad según nivel)
        cantidad_base = 1
        cantidad_extra = nivel_jugador // 5  # 1 extra cada 5 niveles
        cantidad = cantidad_base + cantidad_extra
        
        for _ in range(cantidad):
            nuevo_enemigo = generar_enemigo_alrededor()
            factor_velocidad = 0.05  # 5% por nivel
            nuevo_enemigo.velocidad *= (1 + (factor_velocidad * nivel_jugador))
            if nuevo_enemigo:
                enemigos.append(nuevo_enemigo)
        
        tiempo_ultimo_enemigo = tiempo_actual
    
    # Aumentar dificultad con el tiempo
    for efecto in efectos_a_eliminar:
        if efecto in efectos_activos and not isinstance(efecto, AuraSag):
            efectos_activos.remove(efecto)
        
def manejar_colision_portal(portal):
    """Maneja la colisión del jugador con un portal"""
    if portal.tipo == "azul":
        # Portal azul: avanzar al siguiente mundo
        if cambiar_mundo(portal.mundo_destino):
            mostrar_mensaje(f"Viajando a {portal.mundo_destino.capitalize()}...")
            # Remover el portal después de usarlo
            if portal in portales:
                portales.remove(portal)
    else:
        # Portal rojo: terminar partida
        terminar_partida()  # Cambiado a terminar_partida
        # Remover el portal después de usarlo
        if portal in portales:
            portales.remove(portal)

def dibujar_enemigo_con_color(enemigo, screen):
    """Dibuja un enemigo con su textura y color identificador"""
    enemigo.draw_con_offset(screen, camera_offset_x, camera_offset_y)
    
            

def dibujar_juego():
    """Dibuja el juego en la pantalla"""
    global fondo_mosaico
    screen = declaraciones["screen"]
    
    # Dibujar fondo mosaico
    if fondo_mosaico:
        fondo_mosaico.dibujar(screen, camera_offset_x, camera_offset_y)
    else:
        # Fallback: usar color según mundo
        mundo = Variables_Globales["MUNDO_ACTUAL"]
        if Variables_Globales["EN_ENDLESS"] and mundo == "endless":
            color_fondo = COLORES_MUNDOS["endless"]
        else:
            color_fondo = COLORES_MUNDOS[mundo]
        
        screen.fill(color_fondo)
    
    # Dibujar efectos activos
    for efecto in efectos_activos:
        if hasattr(efecto, 'draw'):
            efecto.draw(screen, camera_offset_x, camera_offset_y)
    
    # Dibujar portales
    for portal in portales:
        portal.draw(screen, camera_offset_x, camera_offset_y)
    
    # Dibujar enemigos
    for enemigo in enemigos:
        dibujar_enemigo_con_color(enemigo, screen)
    
    # Dibujar protagonista
    protagonista.draw_con_offset(screen, camera_offset_x, camera_offset_y, centrado=False)
    
    # Dibujar HUD
    dibujar_hud()
    
    # Dibujar mensaje de poder
    if tiempo_mensaje > 0 and mensaje_poder:
        alpha = min(255, int(tiempo_mensaje * 300))
        texto = font_mediana.render(mensaje_poder, True, (255, 255, 100))
        texto_rect = texto.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.1)))
        
        surf = pygame.Surface((texto_rect.width + 20, texto_rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 0, 0, alpha//2), surf.get_rect(), border_radius=10)
        pygame.draw.rect(surf, (255, 255, 100, alpha), surf.get_rect(), 2, border_radius=10)
        
        screen.blit(surf, (texto_rect.x - 10, texto_rect.y - 5))
        screen.blit(texto, texto_rect)

def dibujar_hud():
    """Dibuja el HUD del juego"""
    screen = declaraciones["screen"]
    mundo = Variables_Globales["MUNDO_ACTUAL"]
    en_endless = Variables_Globales["EN_ENDLESS"]
    
    # Barra de vida
    vida_ancho = int(WIDTH * 0.2)
    vida_altura = int(HEIGHT * 0.03)
    vida_x = int(WIDTH * 0.02)
    vida_y = int(HEIGHT * 0.02)
    
    pygame.draw.rect(screen, (50, 50, 50), 
                    (vida_x, vida_y, vida_ancho, vida_altura), border_radius=5)
    
    vida_porcentaje = protagonista.vida / protagonista.vida_max
    vida_actual_ancho = vida_porcentaje * vida_ancho
    color_vida = (int(255 * (1 - vida_porcentaje)), int(255 * vida_porcentaje), 0)
    if protagonista.vida <= 0:
        color_vida = (255, 0, 0)
    pygame.draw.rect(screen, color_vida, 
                    (vida_x, vida_y, vida_actual_ancho, vida_altura), border_radius=5)
    
    vida_texto = font_pequena.render(f"Vida: {int(protagonista.vida)}/{protagonista.vida_max}", 
                                    True, (255, 255, 255))
    screen.blit(vida_texto, (vida_x + 10, vida_y))
    
    # Barra de experiencia
    exp_y = vida_y + vida_altura + 5
    exp_ancho = vida_ancho
    exp_altura = int(HEIGHT * 0.02)
    
    # Calcular progreso de experiencia
    progreso_exp = protagonista.get_progreso_nivel()
    exp_actual = protagonista.experiencia - protagonista.exp_para_nivel_actual
    exp_necesaria = protagonista.exp_para_proximo_nivel - protagonista.exp_para_nivel_actual
    
    # Fondo barra de experiencia
    pygame.draw.rect(screen, (30, 30, 60), 
                    (vida_x, exp_y, exp_ancho, exp_altura), border_radius=3)
    
    # Experiencia actual
    exp_actual_ancho = progreso_exp * exp_ancho
    pygame.draw.rect(screen, (100, 150, 255), 
                    (vida_x, exp_y, exp_actual_ancho, exp_altura), border_radius=3)
    
    # Texto de experiencia
    exp_texto = font_pequena.render(f"Nivel {protagonista.nivel}: {exp_actual}/{exp_necesaria} XP", 
                                   True, (200, 220, 255))
    screen.blit(exp_texto, (vida_x + 5, exp_y + 2))
    
    # Mundo actual
    y_offset = exp_y + exp_altura + 10
    modo = " (ENDLESS)" if en_endless else ""
    mundo_texto = font_pequena.render(f"Mundo: {mundo.capitalize()}{modo}", 
                                     True, (255, 255, 255))
    screen.blit(mundo_texto, (vida_x, y_offset))
    
    # Tiempo y nivel juego
    minutos = int(tiempo_juego // 60)
    segundos = int(tiempo_juego % 60)
    tiempo_texto = font_pequena.render(f"Tiempo: {minutos:02d}:{segundos:02d} | Nivel Juego: {nivel_juego}", 
                                      True, (255, 255, 255))
    screen.blit(tiempo_texto, (vida_x, y_offset + 25))
    
    # Estadísticas
    derrotados_texto = font_pequena.render(f"Derrotados: {enemigos_derrotados} | Exp Total: {experiencia_total}", 
                                          True, (255, 255, 255))
    screen.blit(derrotados_texto, (vida_x, y_offset + 50))
    
    # Requisitos para siguiente mundo
    if mundo in REQUISITOS_MUNDO and not en_endless:
        requisito = REQUISITOS_MUNDO[mundo]
        if protagonista.nivel < requisito["nivel"]:
            req_texto = font_pequena.render(f"Próximo mundo: Nivel {requisito['nivel']} ({protagonista.nivel}/{requisito['nivel']})", 
                                           True, (150, 255, 150))
            screen.blit(req_texto, (vida_x, y_offset + 75))
    
    # Poderes activos
    y_poder = y_offset + 100
    if hasattr(protagonista, 'poderes'):
        for poder in protagonista.poderes:
            stack_text = f" x{poder.stacks}" if poder.stacks > 1 else ""
            poder_texto = font_pequena.render(f"• {poder.nombre} Nv.{poder.nivel}{stack_text}", 
                                             True, (200, 200, 255))
            screen.blit(poder_texto, (vida_x, y_poder))
            y_poder += int(HEIGHT * 0.03)
    
    # Controles
    controles_y = HEIGHT - int(HEIGHT * 0.12)
    controles = [
        "Controles:",
        "WASD - Moverse",
        "M - Poder aleatorio",
        "E - Spawn enemigo (debug)",
        "F - Pantalla completa",
        "ESC - Volver al menú"
    ]
    
    for i, control in enumerate(controles):
        color = (255, 255, 255) if i == 0 else (200, 200, 200)
        control_texto = font_pequena.render(control, True, color)
        screen.blit(control_texto, (WIDTH - int(WIDTH * 0.3), controles_y + i * int(HEIGHT * 0.03)))
    
    # Contador de enemigos
    contador = font_pequena.render(f"Enemigos en pantalla: {len(enemigos)}", True, (255, 255, 255))
    screen.blit(contador, (WIDTH - int(WIDTH * 0.3), vida_y))

def game_over():
    """Maneja el fin del juego"""
    global en_juego, mostrando_game_over, tiempo_game_over, game_over_alpha, estadisticas_finales
    
    # Guardar estadísticas
    estadisticas_finales = {
        "tiempo_total": tiempo_juego,
        "enemigos_derrotados": enemigos_derrotados,
        "nivel_alcanzado": protagonista.nivel if protagonista else 0,
        "experiencia_total": experiencia_total,
        "poderes_obtenidos": len(protagonista.poderes) if protagonista else 0,
        "mundo_maximo": Variables_Globales["MUNDO_ACTUAL"],
        "endless_mode": Variables_Globales["EN_ENDLESS"],
        "partida_completada": Variables_Globales["PARTIDA_COMPLETADA"],
        "razon": "Derrotado"
    }
    
    # Cambiar estados
    en_juego = False
    mostrando_game_over = True
    tiempo_game_over = 0
    game_over_alpha = 0
    
    # Detener juego pero mantener pantalla
    print("GAME OVER - Presiona ENTER para volver al menú")

def terminar_partida():
    """Termina la partida por portal rojo"""
    global en_juego, mostrando_game_over, tiempo_game_over, game_over_alpha, estadisticas_finales
    mensaje="GANASTEEEEEEEEEEEE!!!!"
    if protagonista.vida<=0:
        mensaje="TE MATARON XDDDD"
    
    # Guardar estadísticas
    estadisticas_finales = {
        "tiempo_total": tiempo_juego,
        "enemigos_derrotados": enemigos_derrotados,
        "nivel_alcanzado": protagonista.nivel if protagonista else 0,
        "experiencia_total": experiencia_total,
        "poderes_obtenidos": len(protagonista.poderes) if protagonista else 0,
        "mundo_maximo": Variables_Globales["MUNDO_ACTUAL"],
        "endless_mode": Variables_Globales["EN_ENDLESS"],
        "partida_completada": Variables_Globales["PARTIDA_COMPLETADA"],
        "razon": mensaje
    }
    
    # Cambiar estados
    en_juego = False
    mostrando_game_over = True
    tiempo_game_over = 0
    game_over_alpha = 0
    
    print("PARTIDA FINALIZADA - Presiona ENTER para volver al menú")

def mostrar_estadisticas_finales():
    """Muestra las estadísticas de la partida finalizada"""
    stats = Variables_Globales["ESTADISTICAS_PARTIDA"]
    
    if not stats:
        return
    
    # Fondo semitransparente
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(surf, (0, 0, 0, 200), surf.get_rect())
    declaraciones["screen"].blit(surf, (0, 0))
    
    # Título
    titulo = "PARTIDA COMPLETADA" if stats.get("partida_completada", False) else "PARTIDA FINALIZADA"
    titulo_color = (50, 255, 50) if stats.get("partida_completada", False) else (255, 255, 100)
    titulo_texto = font_grande.render(titulo, True, titulo_color)
    titulo_rect = titulo_texto.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200))
    declaraciones["screen"].blit(titulo_texto, titulo_rect)
    
    # Estadísticas
    minutos = int(stats["tiempo_total"] // 60)
    segundos = int(stats["tiempo_total"] % 60)
    
    estadisticas = [
        f"Tiempo de supervivencia: {minutos:02d}:{segundos:02d}",
        f"Enemigos derrotados: {stats['enemigos_derrotados']}",
        f"Nivel alcanzado: {stats['nivel_alcanzado']}",
        f"Experiencia total: {stats['experiencia_total']}",
        f"Poderes obtenidos: {stats['poderes_obtenidos']}",
        f"Mundo máximo: {stats['mundo_maximo'].capitalize()}",
        f"Modo Endless: {'SÍ' if stats['endless_mode'] else 'NO'}"
    ]
    
    for i, stat in enumerate(estadisticas):
        stat_texto = font_mediana.render(stat, True, (255, 255, 255))
        stat_rect = stat_texto.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100 + i * 40))
        declaraciones["screen"].blit(stat_texto, stat_rect)
    
    # Mensaje para continuar
    continuar = font_pequena.render("Haz clic en START para jugar de nuevo", True, (200, 200, 200))
    continuar_rect = continuar.get_rect(center=(WIDTH // 2, HEIGHT - 50))
    declaraciones["screen"].blit(continuar, continuar_rect)

def mostrar_pantalla_game_over():
    """Muestra pantalla de game over"""
    # Fondo semitransparente
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(surf, (0, 0, 0, 200), surf.get_rect())
    declaraciones["screen"].blit(surf, (0, 0))
    
    # Título
    titulo = font_grande.render("GAME OVER", True, (255, 50, 50))
    titulo_rect = titulo.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    declaraciones["screen"].blit(titulo, titulo_rect)
    
    # Estadísticas
    stats = [
        f"Tiempo de supervivencia: {int(tiempo_juego//60)}:{int(tiempo_juego%60):02d}",
        f"Enemigos derrotados: {enemigos_derrotados}",
        f"Nivel alcanzado: {nivel_juego}",
        f"Experiencia total: {experiencia_total}",
        f"Poderes obtenidos: {len(protagonista.poderes) if protagonista else 0}",
        f"Mundo alcanzado: {Variables_Globales['MUNDO_ACTUAL'].capitalize()}"
    ]
    
    for i, stat in enumerate(stats):
        stat_texto = font_mediana.render(stat, True, (255, 255, 255))
        stat_rect = stat_texto.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 40))
        declaraciones["screen"].blit(stat_texto, stat_rect)
    
    # Mensaje para continuar
    continuar = font_pequena.render("Haz clic en START para jugar de nuevo", True, (200, 200, 200))
    continuar_rect = continuar.get_rect(center=(WIDTH // 2, HEIGHT - 50))
    declaraciones["screen"].blit(continuar, continuar_rect)

def cambiar_resolucion():
    """Cambia la resolución del juego"""
    global WIDTH, HEIGHT, camera_offset_x, camera_offset_y
    
    if Variables_Globales["FULLSCREEN"]:
        WIDTH, HEIGHT = Variables_Globales["FULLSCREEN_RES"]
        declaraciones["screen"] = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        WIDTH, HEIGHT = Variables_Globales["WINDOWED_RES"]
        declaraciones["screen"] = pygame.display.set_mode((WIDTH, HEIGHT))
    
    # Recargar fondo con nueva resolución
    try:
        posibles_rutas = [
            os.path.join("ChafaSurvivors", "images", "fondo.jpg"),
            "fondo.jpg",
            "images/fondo.jpg",
            "ChafaSurvivors/images/fondo.jpg",
            "ChafaSurvivors/fondo.jpg"
        ]
        
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                declaraciones["background"] = pygame.image.load(ruta)
                declaraciones["background"] = pygame.transform.scale(
                    declaraciones["background"], 
                    (WIDTH, HEIGHT)
                )
                print(f"Fondo recargado desde: {ruta}")
                break
        else:
            declaraciones["background"] = None
            
    except Exception as e:
        print(f"Error recargando fondo: {e}")
        declaraciones["background"] = None
    
    camera_offset_x = 0
    camera_offset_y = 0
    actualizar_fuentes()
    
    if en_juego and protagonista:
        actualizar_camara()

def manejar_input_game_over(event):
    """Maneja el input durante la pantalla de Game Over"""
    global mostrando_game_over, estadisticas_finales
    
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            # Volver al menú principal
            volver_al_menu()
            return True
        elif event.key == pygame.K_ESCAPE:
            # También ESC para volver al menú
            volver_al_menu()
            return True
    
    return False

def volver_al_menu():
    """Vuelve al menú principal desde Game Over"""
    global mostrando_game_over, en_juego, estadisticas_finales
    
    # Guardar estadísticas en variables globales para mostrarlas si es necesario
    if estadisticas_finales:
        Variables_Globales["ESTADISTICAS_PARTIDA"] = estadisticas_finales
    
    # Resetear estados
    mostrando_game_over = False
    en_juego = False
    
    # Restablecer estados del menú
    estado_bloques["rect1"] = True
    estado_bloques["rect2"] = True
    estado_bloques["rect3"] = True
    estado_bloques["rect4"] = False
    estado_bloques["rect5"] = False
    estado_bloques["rect6"] = False
    Variables_Globales["STARTGAME"] = False
    
    # Limpiar estadísticas para la próxima partida
    estadisticas_finales = {}
    
def dibujar_pantalla_game_over():
    """Dibuja la pantalla de Game Over con estadísticas"""
    global game_over_alpha, tiempo_game_over
    
    screen = declaraciones["screen"]
    
    # Actualizar alpha (efecto de fade in)
    tiempo_game_over += clock.get_time() / 1000.0
    game_over_alpha = min(255, int(tiempo_game_over * 128))
    
    # Fondo negro semitransparente
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, game_over_alpha // 2))
    screen.blit(overlay, (0, 0))
    
    # Fondo rojo para título
    titulo_bg = pygame.Surface((WIDTH, int(HEIGHT * 0.15)), pygame.SRCALPHA)
    titulo_bg.fill((200, 0, 0, game_over_alpha))
    screen.blit(titulo_bg, (0, HEIGHT // 2 - int(HEIGHT * 0.3)))
    
    # Título
    titulo_texto = "GAME OVER" if estadisticas_finales.get("razon") == "Derrotado" else "PARTIDA COMPLETADA"
    titulo_color = (255, 50, 50) if estadisticas_finales.get("razon") == "Derrotado" else (255, 200, 50)
    
    titulo = font_grande.render(titulo_texto, True, titulo_color)
    titulo_rect = titulo.get_rect(center=(WIDTH // 2, HEIGHT // 2 - int(HEIGHT * 0.25)))
    screen.blit(titulo, titulo_rect)
    
    # Estadísticas
    stats_y = HEIGHT // 2 - int(HEIGHT * 0.15)
    
    # Tiempo de juego
    minutos = int(estadisticas_finales.get("tiempo_total", 0) // 60)
    segundos = int(estadisticas_finales.get("tiempo_total", 0) % 60)
    tiempo_stats = f"Tiempo de supervivencia: {minutos:02d}:{segundos:02d}"
    
    # Razón de fin
    razon_text = f"Razón: {estadisticas_finales.get('razon', 'Desconocida')}"
    
    stats = [
        tiempo_stats,
        f"Enemigos derrotados: {estadisticas_finales.get('enemigos_derrotados', 0)}",
        f"Nivel alcanzado: {estadisticas_finales.get('nivel_alcanzado', 0)}",
        f"Experiencia total: {estadisticas_finales.get('experiencia_total', 0)}",
        f"Poderes obtenidos: {estadisticas_finales.get('poderes_obtenidos', 0)}",
        f"Mundo máximo: {estadisticas_finales.get('mundo_maximo', 'bosque').capitalize()}",
        razon_text
    ]
    
    for i, stat in enumerate(stats):
        color = (255, 255, 255) if i % 2 == 0 else (200, 200, 200)
        stat_texto = font_mediana.render(stat, True, color)
        stat_rect = stat_texto.get_rect(center=(WIDTH // 2, stats_y + i * int(HEIGHT * 0.05)))
        screen.blit(stat_texto, stat_rect)
    
    # Instrucciones
    instrucciones_y = HEIGHT - int(HEIGHT * 0.15)
    instrucciones = font_mediana.render("Presiona ENTER para volver al menú", True, (200, 200, 255))
    instrucciones_rect = instrucciones.get_rect(center=(WIDTH // 2, instrucciones_y))
    
    # Efecto de parpadeo en las instrucciones
    if int(pygame.time.get_ticks() / 500) % 2 == 0:
        screen.blit(instrucciones, instrucciones_rect)
    
    # Firma/creditos
    creditos = font_pequena.render("Game Over - Puras Holadas", True, (150, 150, 150))
    creditos_rect = creditos.get_rect(center=(WIDTH // 2, HEIGHT - 30))
    screen.blit(creditos, creditos_rect)

# Bucle principal
while running:
    if en_juego:
        # Modo juego activo
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Pausar/volver al menú
                    en_juego = False
                    estado_bloques["rect1"] = True
                    estado_bloques["rect2"] = True
                    estado_bloques["rect3"] = True
                    estado_bloques["rect4"] = False
                    estado_bloques["rect5"] = False
                    estado_bloques["rect6"] = False
                    Variables_Globales["STARTGAME"] = False
                elif event.key == pygame.K_e:
                    enemigos.append(generar_enemigo_alrededor())
                    mostrar_mensaje("Enemigo generado (debug)")
                elif event.key == pygame.K_m:
                    if hasattr(protagonista, 'ganar_poder_aleatorio'):
                        resultado = protagonista.ganar_poder_aleatorio()
                        mostrar_mensaje(resultado)
                elif event.key == pygame.K_f:
                    Variables_Globales["FULLSCREEN"] = not Variables_Globales["FULLSCREEN"]
                    cambiar_resolucion()
        
        actualizar_juego()
        dibujar_juego()
        
    elif mostrando_game_over:
        # Pantalla de Game Over
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif manejar_input_game_over(event):
                # Si se presionó ENTER, ya se manejó en la función
                pass
        
        # Dibujar el último frame del juego como fondo
        dibujar_juego()
        # Dibujar overlay de Game Over
        dibujar_pantalla_game_over()
        
    else:
        # Modo menú
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                running = menu_eventos(event, running)
                
                if Variables_Globales["STARTGAME"] and not en_juego:
                    en_juego = True
                    inicializar_juego()
        
        menu()
    
    pygame.display.flip()



pygame.quit()
sys.exit()