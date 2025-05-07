# Crear un sistema de camiones
import asyncio
import random
import datetime
import statistics
from abc import ABC, abstractmethod
import functools
from openlocationcode import openlocationcode as olc

#R1
class Sistema:
    _instance = None

    def __init__(self, nombre):
        if Sistema._instance is not None:
            raise Exception("¡Esta clase es un Singleton! Utilice 'get_instance()' para obtener la instancia.")
        
        self.nombre = nombre
        self.camiones = []
        print(f"Se ha creado el sistema logístico {self.nombre}")

    @classmethod
    def get_instance(cls, nombre):
        if cls._instance is None:
            cls._instance = cls(nombre)
        return cls._instance
    
    def agregar_camion(self, camion):
        self.camiones.append(camion)

#R2
    def actualizacion(self, camion, tupla):
        print(f"El camión {camion.numero} actualizó sus datos {tupla}")

class Camion:
    def __init__(self, numero, sistema, km):
        self.numero = numero
        self.sistema = sistema
        self.tiempo_trayecto = km/100 #Asumimos que el camion va a una velocidad media de 100 km/h y pasamos la distancia a horas
        self.sistema.agregar_camion(self)
        self.data = {'temperatura': [], 'humedad': []}
        self.calcular_estadisticos = None
        self.verificar_umbral = None
        self.comprobar_variacion = None
    
    async def actualizar_datos(self):
        self.tiempo_trayecto -= 1 #Asumimos que los cinco segundos que tardan en actualizar los datos son 1 hora y eliminamos una hora de trayecto
        time = datetime.datetime.now()
        tiempo = time.strftime("%d-%m-%Y %H:%M:%S") 
        temperatura = self.simular_temperatura()
        humedad = self.simular_humedad()
        localizacion = self.simular_localizacion()

        if len(self.data['temperatura']) >= 12:
            del(self.data['temperatura'][0])
            del(self.data['humedad'][0])

        self.data['temperatura'].append(temperatura) 
        self.data['humedad'].append(humedad) 
        self.sistema.actualizacion(self, (tiempo, temperatura, humedad, localizacion))

        self.comprobar_variacion = ComprobarVariacion()
        self.verificar_umbral = VerificarUmbralTemperatura(self.comprobar_variacion)
        self.calcular_estadisticos = Estadistico(self.verificar_umbral)

        await self.calcular_estadisticos.handle_request(self)
        await asyncio.sleep(5)

    def simular_temperatura(self):
        return round((20 + (5 * random.random())), 2)  #Valores de temperatura en los que se maneja España

    def simular_humedad(self):
        return round((70 + (10 * random.random())), 2) #Valores de humedad en los que se maneja España

    def simular_localizacion(self):
        return (random.uniform(3, 9), random.uniform(27, 43)) #Los valores de latitud en los que se maneja España

    def fin_trayecto(self):
        if self.tiempo_trayecto == 0: #Si el tiempo se ha acabado el trayecto llega a su fin
            return True
        return False

#R3 Cadena de responsabilidad  

class Handler:
    def __init__(self, successor=None):
        self.successor = successor 

    async def handle_request(self, data):
        pass

class Estadistico(Handler):
    async def handle_request(self, camion):
        # Verificar si hay suficientes datos para calcular la media y la varianza
        if len(camion.data['temperatura']) > 1:
            temp_mean = functools.reduce(lambda x, y: x+y, camion.data['temperatura']) / len(camion.data['temperatura'])
            temp_var= functools.reduce(lambda x, y: x + (y - temp_mean) ** 2, camion.data['temperatura'], 0) / len(camion.data['temperatura'])
        else:
            temp_mean = functools.reduce(lambda x, y: x+y, camion.data['temperatura']) / len(camion.data['temperatura'])
            temp_var = 0  # No hay suficiente datos para calcular la desviación estándar

        if len(camion.data['humedad']) > 1:
            hum_mean = functools.reduce(lambda x, y: x+y, camion.data['humedad']) / len(camion.data['humedad'])
            hum_var= functools.reduce(lambda x, y: x + (y - temp_mean) ** 2, camion.data['humedad'], 0) / len(camion.data['humedad'])
        else:
            hum_mean = functools.reduce(lambda x, y: x+y, camion.data['humedad']) / len(camion.data['humedad'])
            hum_var = 0  # No hay suficiente datos para calcular la desviación estándar

        print(f'media_temperatura = {temp_mean}, varianza_temperatura = {temp_var}, media_humedad = {hum_mean}, varianza_humedad = {hum_var}')

        await self.successor.handle_request(camion)

class VerificarUmbralTemperatura(Handler):
    
    async def handle_request(self, camion):
        if camion.data['temperatura'][-1] > 27:
            print(f"Advertencia: Temperatura actual ({camion.data['temperatura'][-1]}°C) está por encima del umbral.")
        else:
            print(f"Temperatura actual ({camion.data['temperatura'][-1]}°C) está dentro del umbral.")
        
        await self.successor.handle_request(camion)
        

class ComprobarVariacion(Handler):
    async def handle_request(self, camion):
        nuevos_datos_temp = camion.data['temperatura']
        nuevos_datos_hum = camion.data['humedad']
        if len(camion.data['temperatura']) >= 6:
            while len(nuevos_datos_temp) != 6:
                i = 0
                nuevos_datos_temp = camion.data['temperatura'][i:]
                i+= 1
        if len(camion.data['humedad']) >= 6:
            while len(nuevos_datos_hum) != 6:
                i = 0
                nuevos_datos_hum = camion.data['humedad'][i:]
                i+= 1
        datos1 = nuevos_datos_temp[0]
        datos2 = nuevos_datos_temp[-1]
        datos3 = nuevos_datos_hum[0]
        datos4 = nuevos_datos_hum[-1]
        variacion_temp = Variacion()
        variacion_hum = Variacion()
        
        variacion_temp, variacion_hum = await asyncio.gather(
            variacion_temp.hacer_calculo(datos1, datos2),
            variacion_hum.hacer_calculo(datos3, datos4)
        )

        if variacion_temp > 2:
            print(f"Advertencia: Variación de temperatura mayor a 2°C")
            
        if variacion_hum > 2:
            print(f"Advertencia: Variación de humedad mayor a 2%")
#R4
class Calculo:
    def hacer_calculo(self, datos1, datos2):
        pass

class Variacion(Calculo):
    async def hacer_calculo(self, datos1, datos2):
        variacion = abs(datos1 - datos2)
        return variacion
class Localizacion:
    def _init_(self, longitud, latitud):
        self.longitud = longitud
        self.latitud = latitud

    def convertir_a_olc(self):
        # Convertir las coordenadas a código OLC
        codigo_olc = olc.encode(self.latitud, self.longitud)
        return codigo_olc

async def main():
    sistema1 = Sistema.get_instance("amazon")
    camion1 = Camion(1, sistema1, 500)
    camion2 = Camion(2, sistema1, 700)

    while True:
        if camion1.fin_trayecto() == False and camion2.fin_trayecto() == False:
            await camion1.actualizar_datos()
            await camion2.actualizar_datos()
        elif camion1.fin_trayecto() == True and camion2.fin_trayecto() == False:
            await camion2.actualizar_datos()
        elif camion2.fin_trayecto() == True and camion1.fin_trayecto() == False:
            await camion1.actualizar_datos()
        else:
            return False

if __name__ == "__main__":
    asyncio.run(main())