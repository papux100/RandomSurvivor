from enemigo import Enemigo
import texturas
import random
import math
import time
from variable_global import Variables_Globales

class EnemigoMejorado(Enemigo):
    def __init__(self, experiencia, vida, velocidad, tipo="zombie", pos=(500, 100)):
        # Verificar si el tipo está permitido en el mundo actual
        mundo_actual = Variables_Globales.get("MUNDO_ACTUAL", "bosque")
        en_endless = Variables_Globales.get("EN_ENDLESS", False)
        
        # En endless mode, todos los tipos están permitidos
        if not en_endless and mundo_actual in ENEMIGOS_POR_MUNDO:
            tipos_permitidos = ENEMIGOS_POR_MUNDO[mundo_actual]
            if tipo not in tipos_permitidos:
                # Si no está permitido, usar un tipo por defecto del mundo
                tipo = random.choice(tipos_permitidos) if tipos_permitidos else "zombie"
        
        animaciones_dict = texturas.obtener_textura_enemigo(tipo) 
        
        super().__init__(experiencia, vida, velocidad, animaciones_dict, pos=pos)
        self.tipo = tipo
        self.daño = 5
        self.velocidad_ataque = 1.0
        self.tiempo_ultimo_ataque = 0
        self.vida_max = vida
        self.experiencia_base = experiencia
        
        # Ajustar XP según tipo (sobrescribiendo el método base)
        self.ajustar_xp_segun_tipo()
        
        # Ajustar según resolución
        self.ajustar_por_resolucion()
        
        # Configurar follow después de inicializar
        self.follow = None
    
    def ajustar_xp_segun_tipo(self):
        """Ajusta la experiencia otorgada según el tipo de enemigo"""
        # XP base por tipo
        xp_por_tipo = {
            "zombie": 10,
            "esqueleto": 15,
            "brujo": 25,
            "momia": 20,
            "escorpion": 12,
            "gusano": 8,
            "templario": 40,
            "angel_oscuro": 60,
            "sacerdote": 35
        }
        
        if self.tipo in xp_por_tipo:
            # Usar XP base sin multiplicadores complejos
            self.experiencia_otorgada = xp_por_tipo[self.tipo]
        else:
            self.experiencia_otorgada = 10
    
    def ajustar_por_resolucion(self):
        """Ajusta las estadísticas según la resolución de pantalla"""
        width, height = Variables_Globales["RESOLUTION"]
        scale_factor = max(width / 1280, height / 720)
        
        # Aumentar vida y daño en pantallas más grandes
        self.vida *= scale_factor * 0.8
        self.vida_max = self.vida
        self.daño *= scale_factor * 0.7
    
    def atacar(self, jugador, tiempo_actual):
        """Intenta atacar al jugador, devuelve True si atacó"""
        if tiempo_actual - self.tiempo_ultimo_ataque > self.velocidad_ataque:
            # Radio de ataque escalado
            width, height = Variables_Globales["RESOLUTION"]
            attack_range = 40 * (width / 1280)
            
            distancia = math.hypot(self.x - jugador.x, self.y - jugador.y)
            if distancia < attack_range:
                self.tiempo_ultimo_ataque = tiempo_actual
                if hasattr(jugador, 'recibir_daño'):
                    return jugador.recibir_daño(self.daño)
        return False
    
    def recibir_daño(self, cantidad):
        """Recibe daño, devuelve True si murió"""
        self.vida -= cantidad
        return self.vida <= 0

# Importar ENEMIGOS_POR_MUNDO desde variable_global
from variable_global import ENEMIGOS_POR_MUNDO

# Tipos específicos de enemigos con XP ajustada
class Zombie(EnemigoMejorado):
    def __init__(self, experiencia=10, vida=50, velocidad=1.5, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "zombie", pos)
        self.daño = 8
        self.experiencia = int(experiencia * 1.0)

class Esqueleto(EnemigoMejorado):
    def __init__(self, experiencia=15, vida=35, velocidad=2.0, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "esqueleto", pos)
        self.daño = 12
        self.velocidad_ataque = 1.5
        self.experiencia = int(experiencia * 1.2)

class Brujo(EnemigoMejorado):
    def __init__(self, experiencia=25, vida=40, velocidad=1.2, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "brujo", pos)
        self.daño = 15
        self.rango_ataque = 150
        self.cooldown_hechizo = 3.0
        self.tiempo_ultimo_hechizo = 0
        self.experiencia = int(experiencia * 1.5)
    
    def atacar(self, jugador, tiempo_actual):
        distancia = math.hypot(self.x - jugador.x, self.y - jugador.y)
        
        # Ataque cuerpo a cuerpo
        if distancia < 40:
            if super().atacar(jugador, tiempo_actual):
                return True
        
        # Hechizo a distancia
        if distancia < self.rango_ataque and tiempo_actual - self.tiempo_ultimo_hechizo > self.cooldown_hechizo:
            self.tiempo_ultimo_hechizo = tiempo_actual
            self.daño = 20
            resultado = super().atacar(jugador, tiempo_actual)
            self.daño = 15
            return resultado
        
        return False

class Momia(EnemigoMejorado):
    def __init__(self, experiencia=20, vida=80, velocidad=1.0, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "momia", pos)
        self.daño = 20
        self.regeneracion = 0.5
        self.tiempo_ultima_regeneracion = 0
        self.experiencia = int(experiencia * 1.3)
    
    def update(self, dt):
        super().update(dt)
        # Regeneración pasiva
        self.tiempo_ultima_regeneracion += dt
        if self.tiempo_ultima_regeneracion >= 1.0:
            self.vida = min(self.vida + self.regeneracion, self.vida_max)
            self.tiempo_ultima_regeneracion = 0

class Escorpion(EnemigoMejorado):
    def __init__(self, experiencia=12, vida=25, velocidad=2.5, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "escorpion", pos)
        self.daño = 10
        self.veneno_daño = 2
        self.veneno_duracion = 3
        self.experiencia = int(experiencia * 0.8)

class Gusano(EnemigoMejorado):
    def __init__(self, experiencia=8, vida=20, velocidad=3.0, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "gusano", pos)
        self.daño = 6
        self.velocidad_ataque = 0.5
        self.experiencia = int(experiencia * 0.6)

class Templario(EnemigoMejorado):
    def __init__(self, experiencia=40, vida=100, velocidad=1.8, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "templario", pos)
        self.daño = 25
        self.armadura = 0.3
        self.experiencia = int(experiencia * 2.0)
    
    def recibir_daño(self, cantidad):
        cantidad_reducida = cantidad * (1 - self.armadura)
        return super().recibir_daño(cantidad_reducida)

class AngelOscuro(EnemigoMejorado):
    def __init__(self, experiencia=60, vida=70, velocidad=2.2, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "angel_oscuro", pos)
        self.daño = 30
        self.vuela = True
        self.experiencia = int(experiencia * 2.5)

class Sacerdote(EnemigoMejorado):
    def __init__(self, experiencia=35, vida=60, velocidad=1.3, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "sacerdote", pos)
        self.daño = 18
        self.curacion_aliados = 2
        self.rango_curacion = 100
        self.experiencia = int(experiencia * 1.8)

# Factory para crear enemigos
class EnemigoFactory:
    @staticmethod
    def crear_enemigo(tipo, nivel=1, pos=None):
        from variable_global import Variables_Globales
        
        if pos is None:
            width, height = Variables_Globales["RESOLUTION"]
            pos = (random.randint(100, width-100), random.randint(100, height-100))
        
        # Multiplicador según nivel
        multiplicador = 1 + (nivel - 1) * 0.5
        
        # Ajustar según resolución
        width, height = Variables_Globales["RESOLUTION"]
        scale_factor = max(width / 1280, height / 720)
        
        # Verificar si el tipo está permitido en el mundo actual
        mundo_actual = Variables_Globales.get("MUNDO_ACTUAL", "bosque")
        en_endless = Variables_Globales.get("EN_ENDLESS", False)
        
        if not en_endless and mundo_actual in ENEMIGOS_POR_MUNDO:
            tipos_permitidos = ENEMIGOS_POR_MUNDO[mundo_actual]
            if tipo not in tipos_permitidos:
                # Si no está permitido, usar el primer tipo permitido
                tipo = tipos_permitidos[0] if tipos_permitidos else "zombie"
        
        enemigos = {
            "zombie": lambda: Zombie(
                experiencia=int(10 * multiplicador * scale_factor),
                vida=int(50 * multiplicador * scale_factor),
                velocidad=1.5,
                pos=pos
            ),
            "esqueleto": lambda: Esqueleto(
                experiencia=int(15 * multiplicador * scale_factor),
                vida=int(35 * multiplicador * scale_factor),
                velocidad=2.0,
                pos=pos
            ),
            "brujo": lambda: Brujo(
                experiencia=int(25 * multiplicador * scale_factor),
                vida=int(40 * multiplicador * scale_factor),
                velocidad=1.2,
                pos=pos
            ),
            "momia": lambda: Momia(
                experiencia=int(20 * multiplicador * scale_factor),
                vida=int(80 * multiplicador * scale_factor),
                velocidad=1.0,
                pos=pos
            ),
            "escorpion": lambda: Escorpion(
                experiencia=int(12 * multiplicador * scale_factor),
                vida=int(25 * multiplicador * scale_factor),
                velocidad=2.5,
                pos=pos
            ),
            "gusano": lambda: Gusano(
                experiencia=int(8 * multiplicador * scale_factor),
                vida=int(20 * multiplicador * scale_factor),
                velocidad=3.0,
                pos=pos
            ),
            "templario": lambda: Templario(
                experiencia=int(40 * multiplicador * scale_factor),
                vida=int(100 * multiplicador * scale_factor),
                velocidad=1.8,
                pos=pos
            ),
            "angel_oscuro": lambda: AngelOscuro(
                experiencia=int(60 * multiplicador * scale_factor),
                vida=int(70 * multiplicador * scale_factor),
                velocidad=2.2,
                pos=pos
            ),
            "sacerdote": lambda: Sacerdote(
                experiencia=int(35 * multiplicador * scale_factor),
                vida=int(60 * multiplicador * scale_factor),
                velocidad=1.3,
                pos=pos
            )
        }
        
        if tipo in enemigos:
            return enemigos[tipo]()
        
        return Zombie(pos=pos)
    
    @staticmethod
    def crear_enemigo_aleatorio(nivel=1, pos=None):
        from variable_global import Variables_Globales, ENEMIGOS_POR_MUNDO
        
        mundo_actual = Variables_Globales.get("MUNDO_ACTUAL", "bosque")
        en_endless = Variables_Globales.get("EN_ENDLESS", False)
        
        if en_endless:
            # En endless mode, todos los tipos están disponibles
            tipos = list(ENEMIGOS_POR_MUNDO["endless"])
        elif mundo_actual in ENEMIGOS_POR_MUNDO:
            tipos = ENEMIGOS_POR_MUNDO[mundo_actual]
        else:
            tipos = ["zombie", "esqueleto", "brujo"]
        
        if not tipos:
            tipos = ["zombie"]
        
        tipo = random.choice(tipos)
        return EnemigoFactory.crear_enemigo(tipo, nivel, pos)