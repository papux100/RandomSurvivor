import pygame
import random
import math
import time

class Poder:
    def __init__(self, nombre, nivel=1, max_nivel=10):
        self.nombre = nombre
        self.nivel = nivel
        self.max_nivel = max_nivel
        self.daño = 0
        self.velocidad = 0
        self.cooldown = 0
        self.cooldown_actual = 0
        self.duracion = 0
        self.rango = 0
        self.area = 0
        self.estaqueable = False
        self.max_stacks = 1
        self.stacks = 1
        self.textura = None
        self.descripcion = ""
        self.ultimo_uso = 0
        
    def subir_nivel(self):
        if self.nivel < self.max_nivel:
            self.nivel += 1
            self.actualizar_estadisticas()
            return True
        return False
    
    def actualizar_estadisticas(self):
        # Método que será sobrescrito por cada poder específico
        pass
    
    def usar(self, jugador, enemigos, tiempo_actual):
        # Método que será sobrescrito por cada poder específico
        pass
    
    def puede_usar(self, tiempo_actual):
        return tiempo_actual - self.ultimo_uso >= self.cooldown
    
    def get_info(self):
        return f"{self.nombre} (Nv.{self.nivel}) - {self.descripcion}"
    
    def puede_staquear(self):
        return self.estaqueable and self.stacks < self.max_stacks
    
    def reset_cooldown(self):
        self.ultimo_uso = 0

# CLASES BASE PARA EFECTOS/PROYECTILES
class Efecto:
    def __init__(self, x, y, daño):
        self.x = x
        self.y = y
        self.daño = daño
        self.vivo = True
        self.tiempo_vida = 0
        self.duracion_maxima = 5.0
        
    def update(self, dt, jugador=None, enemigos=None):
        self.tiempo_vida += dt
        if self.tiempo_vida > self.duracion_maxima:
            self.vivo = False
        return self.vivo
    
    def draw(self, screen, offset_x=0, offset_y=0):
        pass
    
    def aplicar_daño(self, enemigo):
        if hasattr(enemigo, 'recibir_daño'):
            return enemigo.recibir_daño(self.daño)
        return False

class Proyectil(Efecto):
    def __init__(self, x, y, objetivo, daño, velocidad):
        super().__init__(x, y, daño)
        self.objetivo = objetivo
        self.velocidad = velocidad
        self.radio = 8
        self.duracion_maxima=3
        
    def update(self, dt, jugador=None, enemigos=None):
        if not self.vivo or not self.objetivo:
            self.vivo = False
            return False
            
        # Calcular dirección hacia el objetivo
        dx = self.objetivo.x - self.x
        dy = self.objetivo.y - self.y
        distancia = math.hypot(dx, dy)
        
        if distancia < 10:  # Colisión
            self.vivo = False
            if hasattr(self.objetivo, 'recibir_daño'):
                self.objetivo.recibir_daño(self.daño)
            return False
            
        if distancia > 500:  # Fuera de rango
            self.vivo = False
            return False
            
        # Normalizar y mover
        if distancia > 0:
            self.x += (dx / distancia) * self.velocidad
            self.y += (dy / distancia) * self.velocidad
            
        return super().update(dt)

class ProyectilHoming(Proyectil):
    def __init__(self, x, y, enemigos, daño, velocidad):
        super().__init__(x, y, None, daño, velocidad)
        self.enemigos = enemigos
        self.buscar_nuevo_objetivo()
        
    def buscar_nuevo_objetivo(self):
        if self.enemigos:
            # Buscar el enemigo más cercano
            self.objetivo = min(self.enemigos, 
                key=lambda e: math.hypot(e.x - self.x, e.y - self.y))

# PODERES ESPECÍFICOS

class BolaDeFuego(Poder):
    def __init__(self, nivel=1):
        super().__init__("Bola de Fuego", nivel, 8)
        self.descripcion = "Dispara bolas de fuego que dañan a los enemigos"
        self.estaqueable = True
        self.max_stacks = 5
        self.stacks = 1
        self.cooldown_base = 1.0
        self.actualizar_estadisticas()
        
    def actualizar_estadisticas(self):
        self.daño = 5 + (self.nivel * 2) + (self.stacks * 1.5)
        self.velocidad = 3 + (self.nivel * 0.2)
        self.cooldown = max(0.3, self.cooldown_base - (self.nivel * 0.1))
        self.rango = 300 + (self.nivel * 20)
        
    def usar(self, jugador, enemigos, tiempo_actual):
        if not enemigos or not self.puede_usar(tiempo_actual):
            return []
        
        self.ultimo_uso = tiempo_actual
        
        # Buscar el enemigo más cercano
        enemigo_mas_cercano = min(enemigos, 
            key=lambda e: math.hypot(e.x - jugador.x, e.y - jugador.y))
        
        # Crear proyectiles
        proyectiles = []
        for i in range(self.stacks):
            angulo_offset = (i - (self.stacks - 1) / 2) * 0.2
            dx = enemigo_mas_cercano.x - jugador.x
            dy = enemigo_mas_cercano.y - jugador.y
            distancia = math.hypot(dx, dy)
            
            if distancia > 0:
                # Aplicar offset de ángulo
                angulo_base = math.atan2(dy, dx)
                angulo = angulo_base + angulo_offset
                
                # Crear proyectil con dirección fija
                proyectil = ProyectilFuego(
                    jugador.x, jugador.y, 
                    angulo, self.daño, self.velocidad, self.rango
                )
                proyectiles.append(proyectil)
        
        return proyectiles

class EspadasVoladoras(Poder):
    def __init__(self, nivel=1):
        super().__init__("Espadas Voladoras", nivel, 6)
        self.descripcion = "Espadas que orbitan alrededor tuyo"
        self.estaqueable = True
        self.max_stacks = 8
        self.espadas = []
        self.angulo_actual = 0
        self.actualizar_estadisticas()
        
    def actualizar_estadisticas(self):
        self.daño = 3 + (self.nivel * 1.5)
        self.velocidad_angular = 0.001 + (self.nivel * 0.1)
        self.radio_orbitante = 80 + (self.nivel * 5)
        self.num_espadas = 1 + (self.nivel // 2)
        
    def usar(self, jugador, enemigos, tiempo_actual):
        if not self.puede_usar(tiempo_actual):
            return []
        
        self.ultimo_uso = tiempo_actual
        
        # Crear o actualizar espadas orbitantes
        espadas = []
        total_espadas = self.num_espadas * self.stacks
        
        for i in range(total_espadas):
            angulo = self.angulo_actual + (i * 2 * math.pi / total_espadas)
            espada = EspadaOrbitante(
                jugador.x, jugador.y, angulo,
                self.radio_orbitante, self.daño, self.velocidad_angular
            )
            espadas.append(espada)
        
        self.angulo_actual += 0.1
        return espadas

class RayoElectrico(Poder):
    def __init__(self, nivel=1):
        super().__init__("Rayo Eléctrico", nivel, 7)
        self.descripcion = "Rayo que daña a múltiples enemigos en línea"
        self.estaqueable = False
        self.cooldown_base = 2.0
        self.actualizar_estadisticas()
        
    def actualizar_estadisticas(self):
        self.daño = 8 + (self.nivel * 3)
        self.rango = 200 + (self.nivel * 30)
        self.area = 20 + (self.nivel * 5)
        self.cooldown = max(0.5, self.cooldown_base - (self.nivel * 0.2))
        
    def usar(self, jugador, enemigos, tiempo_actual):
        if not enemigos or not self.puede_usar(tiempo_actual):
            return []
        
        self.ultimo_uso = tiempo_actual
        
        # Encontrar el enemigo más cercano
        enemigo_mas_cercano = min(enemigos, 
            key=lambda e: math.hypot(e.x - jugador.x, e.y - jugador.y))
        
        # Encontrar otros enemigos en la misma línea
        enemigos_en_linea = [enemigo_mas_cercano]
        for enemigo in enemigos:
            if enemigo != enemigo_mas_cercano:
                # Calcular distancia perpendicular a la línea jugador-enemigo_principal
                distancia = self.distancia_a_linea(
                    jugador.x, jugador.y,
                    enemigo_mas_cercano.x, enemigo_mas_cercano.y,
                    enemigo.x, enemigo.y
                )
                if distancia < self.area:
                    enemigos_en_linea.append(enemigo)
        
        return [RayoElectro(
            jugador.x, jugador.y, enemigos_en_linea, 
            self.daño, self.cooldown * 0.3  # Duración del rayo
        )]
    
    @staticmethod
    def distancia_a_linea(x1, y1, x2, y2, x0, y0):
        """Calcula la distancia de un punto a una línea"""
        numerador = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        denominador = math.hypot(y2 - y1, x2 - x1)
        return numerador / denominador if denominador != 0 else float('inf')

class CampoMagnetico(Poder):
    def __init__(self, nivel=1):
        super().__init__("Campo Magnético", nivel, 5)
        self.descripcion = "Atrae a los enemigos y los daña continuamente"
        self.estaqueable = False
        self.cooldown_base = 10.0
        self.actualizar_estadisticas()
        
    def actualizar_estadisticas(self):
        self.daño_por_segundo = 1 + (self.nivel * 0.5)
        self.area = 150 + (self.nivel * 20)
        self.fuerza_atraccion = 0.5 + (self.nivel * 0.1)
        self.cooldown = max(3.0, self.cooldown_base - (self.nivel * 1.0))
        self.duracion = 5 + (self.nivel * 1)
        
    def usar(self, jugador, enemigos, tiempo_actual):
        if not self.puede_usar(tiempo_actual):
            return []
        
        self.ultimo_uso = tiempo_actual
        
        return [CampoMag(
            jugador.x, jugador.y, self.daño_por_segundo, 
            self.area, self.fuerza_atraccion, self.duracion
        )]

class AuraSagrada(Poder):
    def __init__(self, nivel=1):
        super().__init__("Aura Sagrada", nivel, 6)
        self.descripcion = "Cura al jugador y daña a enemigos cercanos"
        self.estaqueable = False
        self.aura_activa = None  # Referencia a la única aura activa
        self.actualizar_estadisticas()
        
    def actualizar_estadisticas(self):
        self.cura_por_segundo = 1 + (self.nivel * 0.5)
        self.daño_por_segundo = 2 + (self.nivel * 0.8)
        self.area = 120 + (self.nivel * 15)
        self.cooldown = 1.0  # Actualización constante
        
    def usar(self, jugador, enemigos, tiempo_actual):
        # Si ya hay una aura activa, actualizarla y devolver lista vacía
        if self.aura_activa and self.aura_activa.vivo:
            # Actualizar estadísticas de la aura existente
            self.aura_activa.cura_por_segundo = self.cura_por_segundo
            self.aura_activa.daño = self.daño_por_segundo
            self.aura_activa.area = self.area
            return []  # No crear nueva aura
            
        # Crear nueva aura si no existe
        self.aura_activa = AuraSag(
            jugador.x, jugador.y, self.cura_por_segundo,
            self.daño_por_segundo, self.area
        )
        return [self.aura_activa]

class LanzaHielo(Poder):
    def __init__(self, nivel=1):
        super().__init__("Lanza de Hielo", nivel, 7)
        self.descripcion = "Lanza que congela a los enemigos"
        self.estaqueable = True
        self.max_stacks = 4
        self.cooldown_base = 1.5
        self.actualizar_estadisticas()
        
    def actualizar_estadisticas(self):
        self.daño = 6 + (self.nivel * 2)
        self.velocidad = 2.5 + (self.nivel * 0.15)
        self.duracion_congelacion = 1 + (self.nivel * 0.3)
        self.cooldown = max(0.5, self.cooldown_base - (self.nivel * 0.1))
        
    def usar(self, jugador, enemigos, tiempo_actual):
        if not enemigos or not self.puede_usar(tiempo_actual):
            return []
        
        self.ultimo_uso = tiempo_actual
        
        proyectiles = []
        enemigo_mas_cercano = min(enemigos, 
            key=lambda e: math.hypot(e.x - jugador.x, e.y - jugador.y))
        
        for i in range(self.stacks):
            angulo_offset = (i - (self.stacks - 1) / 2) * 0.15
            dx = enemigo_mas_cercano.x - jugador.x
            dy = enemigo_mas_cercano.y - jugador.y
            distancia = math.hypot(dx, dy)
            
            if distancia > 0:
                angulo_base = math.atan2(dy, dx)
                angulo = angulo_base + angulo_offset
                
                proyectil = LanzaHieloProyectil(
                    jugador.x, jugador.y, angulo,
                    self.daño, self.velocidad, self.duracion_congelacion
                )
                proyectiles.append(proyectil)
        
        return proyectiles

# IMPLEMENTACIONES COMPLETAS DE LOS EFECTOS

class ProyectilFuego(Proyectil):
    def __init__(self, x, y, angulo, daño, velocidad, rango):
        super().__init__(x, y, None, daño, velocidad)
        self.angulo = angulo
        self.rango = rango
        self.distancia_recorrida = 0
        self.radio = 12
        
    def update(self, dt, jugador=None, enemigos=None):
        # Mover en dirección del ángulo
        self.x += math.cos(self.angulo) * self.velocidad
        self.y += math.sin(self.angulo) * self.velocidad
        self.distancia_recorrida += self.velocidad
        
        # Verificar colisión con enemigos
        if enemigos:
            for enemigo in enemigos[:]:
                distancia = math.hypot(self.x - enemigo.x, self.y - enemigo.y)
                if distancia < self.radio + 15:  # Radio de colisión
                    self.aplicar_daño(enemigo)
                    # Bola de fuego explota al impactar
                    self.vivo = False
                    return False
        
        # Verificar si ha recorrido suficiente distancia
        if self.distancia_recorrida > self.rango:
            self.vivo = False
            return False
            
        return True
    
    def draw(self, screen, offset_x=0, offset_y=0):
        if self.vivo:
            # Círculo de fuego
            pygame.draw.circle(screen, (255, 100, 0), 
                             (int(self.x + offset_x), int(self.y + offset_y)), 
                             self.radio)
            pygame.draw.circle(screen, (255, 200, 0), 
                             (int(self.x + offset_x), int(self.y + offset_y)), 
                             self.radio - 4)
            # Efecto de llama
            for i in range(3):
                radio_llama = self.radio + random.randint(0, 3)
                color_llama = (255, 150 + random.randint(0, 50), 0)
                pygame.draw.circle(screen, color_llama,
                                 (int(self.x + offset_x + random.randint(-2, 2)),
                                  int(self.y + offset_y + random.randint(-2, 2))),
                                 radio_llama)

class EspadaOrbitante:
    def __init__(self, x_centro, y_centro, angulo, radio, daño, velocidad_angular):
        self.x_centro = x_centro
        self.y_centro = y_centro
        self.angulo = angulo
        self.radio = radio
        self.daño = daño
        self.velocidad_angular = velocidad_angular
        self.vivo = True
        self.tiempo_vida = 0
        self.duracion_maxima = float('inf')  # Vive hasta que el poder se cancele
        
        # Calcular posición inicial
        self.x = self.x_centro + self.radio * math.cos(self.angulo)
        self.y = self.y_centro + self.radio * math.sin(self.angulo)
        
    def update(self, dt, jugador=None, enemigos=None):
        if not self.vivo:
            return False
            
        # Actualizar centro si hay jugador
        if jugador:
            self.x_centro = jugador.x
            self.y_centro = jugador.y
        
        # Rotar
        self.angulo += self.velocidad_angular * dt
        
        # Calcular nueva posición
        self.x = self.x_centro + self.radio * math.cos(self.angulo)
        self.y = self.y_centro + self.radio * math.sin(self.angulo)
        
        # Verificar colisiones
        if enemigos:
            for enemigo in enemigos[:]:
                distancia = math.hypot(self.x - enemigo.x, self.y - enemigo.y)
                if distancia < 20:  # Radio de ataque
                    enemigo.recibir_daño(self.daño)
        
        self.tiempo_vida += dt
        return True
    
    def draw(self, screen, offset_x=0, offset_y=0):
        if self.vivo:
            # Dibujar espada
            start_x = int(self.x + offset_x - 10 * math.cos(self.angulo + math.pi/2))
            start_y = int(self.y + offset_y - 10 * math.sin(self.angulo + math.pi/2))
            end_x = int(self.x + offset_x + 20 * math.cos(self.angulo))
            end_y = int(self.y + offset_y + 20 * math.sin(self.angulo))
            
            pygame.draw.line(screen, (200, 200, 220), 
                           (start_x, start_y), (end_x, end_y), 4)
            pygame.draw.line(screen, (100, 100, 255), 
                           (start_x, start_y), (end_x, end_y), 2)

class RayoElectro(Efecto):
    def __init__(self, x, y, enemigos, daño, duracion):
        super().__init__(x, y, daño)
        self.enemigos = enemigos
        self.duracion_maxima = duracion
        self.tiempo_entre_daños = 0.1
        self.tiempo_ultimo_daño = 0
        
    def update(self, dt, jugador=None, enemigos_lista=None):
        if not super().update(dt):
            return False
            
        # Aplicar daño periódico
        self.tiempo_ultimo_daño += dt
        if self.tiempo_ultimo_daño >= self.tiempo_entre_daños:
            self.tiempo_ultimo_daño = 0
            for enemigo in self.enemigos:
                self.aplicar_daño(enemigo)
        
        return True
    
    def draw(self, screen, offset_x=0, offset_y=0):
        # Dibujar líneas de rayo a cada enemigo
        for enemigo in self.enemigos:
            # Efecto de rayo eléctrico (línea con variaciones)
            for i in range(3):
                offset = random.randint(-3, 3)
                color = (100 + i*50, 200 + i*20, 255)
                pygame.draw.line(screen, color,
                               (int(self.x + offset_x + offset), 
                                int(self.y + offset_y)),
                               (int(enemigo.x + offset_x + random.randint(-2, 2)),
                                int(enemigo.y + offset_y + random.randint(-2, 2))),
                               2)

class CampoMag(Efecto):
    def __init__(self, x, y, daño_por_segundo, area, fuerza_atraccion, duracion):
        super().__init__(x, y, daño_por_segundo)
        self.area = area
        self.fuerza_atraccion = fuerza_atraccion
        self.duracion_maxima = duracion
        self.tiempo_entre_daños = 0.5
        self.tiempo_ultimo_daño = 0
        
    def update(self, dt, jugador=None, enemigos=None):
        if not super().update(dt):
            return False
            
        if not enemigos:
            return True
            
        # Aplicar atracción y daño
        self.tiempo_ultimo_daño += dt
        
        for enemigo in enemigos[:]:
            # Calcular distancia al centro del campo
            dx = self.x - enemigo.x
            dy = self.y - enemigo.y
            distancia = math.hypot(dx, dy)
            
            if distancia < self.area:
                # Atraer hacia el centro
                if distancia > 10:  # No atraer si está muy cerca
                    enemigo.x += (dx / distancia) * self.fuerza_atraccion
                    enemigo.y += (dy / distancia) * self.fuerza_atraccion
                
                # Aplicar daño periódico
                if self.tiempo_ultimo_daño >= self.tiempo_entre_daños:
                    self.aplicar_daño(enemigo)
        
        if self.tiempo_ultimo_daño >= self.tiempo_entre_daños:
            self.tiempo_ultimo_daño = 0
            
        return True
    
    def draw(self, screen, offset_x=0, offset_y=0):
        # Dibujar campo magnético (círculos concéntricos)
        for i in range(3):
            radio = self.area * (1 - i * 0.2)
            alpha = 100 - i * 30
            color = (100, 100, 255, alpha)
            
            # Crear superficie temporal para alpha
            temp_surf = pygame.Surface((int(radio*2), int(radio*2)), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, color, (int(radio), int(radio)), int(radio), 2)
            
            screen.blit(temp_surf, 
                       (int(self.x + offset_x - radio), 
                        int(self.y + offset_y - radio)))

class AuraSag(Efecto):
    def __init__(self, x, y, cura_por_segundo, daño_por_segundo, area):
        super().__init__(x, y, daño_por_segundo)
        self.cura_por_segundo = cura_por_segundo
        self.area = area
        self.duracion_maxima = float('inf')  # Efecto permanente
        self.tiempo_entre_efectos = 0.5
        self.tiempo_ultimo_efecto = 0
        self.jugador = None  # Referencia al jugador
        
    def update(self, dt, jugador=None, enemigos=None):
        # Guardar referencia al jugador
        if jugador and not self.jugador:
            self.jugador = jugador
        
        # Actualizar posición para seguir al jugador
        if self.jugador:
            self.x = self.jugador.x
            self.y = self.jugador.y
        
        self.tiempo_ultimo_efecto += dt
        
        if self.tiempo_ultimo_efecto >= self.tiempo_entre_efectos:
            self.tiempo_ultimo_efecto = 0
            
            # Curar al jugador
            if jugador:
                jugador.curar(self.cura_por_segundo * self.tiempo_entre_efectos)
            
            # Dañar enemigos cercanos
            if enemigos:
                for enemigo in enemigos[:]:
                    distancia = math.hypot(self.x - enemigo.x, self.y - enemigo.y)
                    if distancia < self.area:
                        enemigo.recibir_daño(self.daño * self.tiempo_entre_efectos)
        
        return True
    
    def draw(self, screen, offset_x=0, offset_y=0):
        # Dibujar aura sagrada alrededor del jugador
        # Optimización: dibujar menos capas y simplificar
        
        # Solo dibujar si está activo
        if not self.vivo:
            return
            
        # Calcular posición en pantalla (seguir al jugador)
        screen_x = self.x + offset_x
        screen_y = self.y + offset_y
        
        # Dibujar solo 1 capa en lugar de 2 (optimización)
        radio = self.area * 0.9  # Radio ligeramente más pequeño
        color = (255, 255, 100, 80)  # Alpha reducido para optimizar
        
        # Crear superficie para el círculo con alpha
        temp_surf = pygame.Surface((int(radio*2), int(radio*2)), pygame.SRCALPHA)
        pygame.draw.circle(temp_surf, color, 
                          (int(radio), int(radio)), 
                          int(radio))
        
        # Dibujar borde (más delgado)
        pygame.draw.circle(temp_surf, (255, 255, 150, 120), 
                          (int(radio), int(radio)), 
                          int(radio), 1)
        
        screen.blit(temp_surf, 
                   (int(screen_x - radio), 
                    int(screen_y - radio)))
        
        # Efecto de partículas opcional (reducido para optimizar)
        import random
        for _ in range(2):  # Solo 2 partículas en lugar de muchas
            angle = random.random() * 2 * math.pi
            particle_radius = random.randint(int(radio*0.8), int(radio))
            px = screen_x + particle_radius * math.cos(angle)
            py = screen_y + particle_radius * math.sin(angle)
            
            particle_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (255, 255, 200, 100), (3, 3), 3)
            screen.blit(particle_surf, (int(px-3), int(py-3)))

class LanzaHieloProyectil(Proyectil):
    def __init__(self, x, y, angulo, daño, velocidad, duracion_congelacion):
        super().__init__(x, y, None, daño, velocidad)
        self.angulo = angulo
        self.duracion_congelacion = duracion_congelacion
        self.radio = 10
        self.enemigo_congelado = None
        
    def update(self, dt, jugador=None, enemigos=None):
        # Mover en dirección del ángulo
        self.x += math.cos(self.angulo) * self.velocidad
        self.y += math.sin(self.angulo) * self.velocidad
        
        # Verificar colisión
        if enemigos:
            for enemigo in enemigos[:]:
                distancia = math.hypot(self.x - enemigo.x, self.y - enemigo.y)
                if distancia < self.radio + 15:
                    self.aplicar_daño(enemigo)
                    self.enemigo_congelado = enemigo
                    self.vivo = False
                    
                    # Aplicar congelación si el enemigo tiene el método
                    if hasattr(enemigo, 'aplicar_congelacion'):
                        enemigo.aplicar_congelacion(self.duracion_congelacion)
                    
                    return False
        
        # Verificar límites de pantalla
        if (self.x < -100 or self.x > 900 or 
            self.y < -100 or self.y > 700):
            self.vivo = False
            return False
            
        return True
    
    def draw(self, screen, offset_x=0, offset_y=0):
        if self.vivo:
            # Dibujar lanza de hielo
            start_x = int(self.x + offset_x)
            start_y = int(self.y + offset_y)
            end_x = int(self.x + offset_x + 20 * math.cos(self.angulo))
            end_y = int(self.y + offset_y + 20 * math.sin(self.angulo))
            
            pygame.draw.line(screen, (100, 200, 255), 
                           (start_x, start_y), (end_x, end_y), 6)
            pygame.draw.line(screen, (200, 230, 255), 
                           (start_x, start_y), (end_x, end_y), 3)

# FACTORY PARA CREAR PODERES
class PoderFactory:
    @staticmethod
    def crear_poder(tipo, nivel=1):
        poderes = {
            "bola_fuego": BolaDeFuego,
            "espadas": EspadasVoladoras,
            "rayo": RayoElectrico,
            "campo_magnetico": CampoMagnetico,
            "aura": AuraSagrada,
            "hielo": LanzaHielo
        }
        
        if tipo in poderes:
            return poderes[tipo](nivel)
        return None
    
    @staticmethod
    def crear_poder_aleatorio(nivel=1):
        tipos = ["bola_fuego", "espadas", "rayo", "campo_magnetico", 
                "esqueletos", "aura", "hielo"]
        tipo = random.choice(tipos)
        return PoderFactory.crear_poder(tipo, nivel)