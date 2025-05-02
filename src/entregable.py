import asyncio
import random
import datetime
import statistics
from abc import ABC, abstractmethod

#R1
class Sistema:
    _instance = None

    def _init_(self,nombre):
        if Sistema._instance is not None:
            raise Exception("¡Esta clase es un Singleton! Utilice 'get_instance()' para obtener la instancia.")
        
        self.nombre = nombre
        self.camiones = []
        print(f"Se ha creado el sistema logístico {self.nombre}")

    @classmethod
    def get_instance(cls, nombre):
        # Método de clase para obtener la instancia única de la clase ConexionBD
        if cls._instance is None:
            cls._instance = cls(nombre)
        return cls._instance
    
    def agregar_camion(self, camion):
        self.camiones.append(camion)

#R2
    def actualizacion(self, camion):
        print(f"{camion} actualizó sus datos de tiempo, temperatura , humedad, latitud y longitud")

    
class Camion:
    def _init_(self, numero, sistema):
        self.numero = numero
        self.sistema = sistema
        self.umbral = 40
        self.sistema.agregar_camion(self)
        self.data = {'temperatura': [], 'humedad':[]}
        self.calcular_estadisticos = None
        self.verificar_umbral = None
        self.comprobar_variacion = None
    
    async def actualizar_datos(self):
        timestamp = datetime.now()
        temperatura = self.simular_temperatura()
        humedad = self.simular_humedad()
        localizacion = self.simular_localizacion()
        if len(self.data[temperatura]) >= 12:
            del(self.data['temperatura'][0])
            del(self.data['humedad'][0])

        self.data['temperatura'].append(temperatura) 
        self.data['humedad'].append(humedad) 
        self.sistema.actualizacion(self)

        self.calcular_estadisticos = Estadistico()
        self.verificar_umbral = VerificarUmbralTemperatura(self.umbral, self.calcular_estadisticos)
        self.comprobar_variacion = ComprobarVariacion(self.verificar_umbral)

        await self.calcular_estadisticos.handle_request(self)
        await asyncio.sleep(5)

    def simular_temperatura(self):
        return 20 + (5 * random.random()) #Valores de temperatura en los que se maneja España

    def simular_humedad(self):
        return 70 + (10 * random.random()) #Valores de homedad en los que se maneja España

    def simular_localizacion(self):
        return (random.uniform(3, 9), random.uniform(27, 43)) #Los valores de latitud en los que se maneja España
#R3 Cadena de responsabilidad  
    

class Handler:
    def __init__(self, successor=None):
        self.successor = successor 

    def handle_request(self, data):
        pass

class Estadistico(Handler):
    def handle_request(self, camion):
        temp_mean = statistics.mean(camion.data['temperatura'])
        temp_var = statistics.stdev(camion.data['temperatura'])
        hum_mean = statistics.mean(camion.data["humedades"])
        hum_var = statistics.stdev(camion.data["humedades"])
        
        print(f'media_temperatura = {temp_mean}, varianza_temperatura = {temp_var}, media_humedad = {hum_mean}, varianza_humedad = {hum_var}')


        if self.successor:
            self.successor.handle_request(camion)
        

class VerificarUmbralTemperatura(Handler):
    def __init__(self, umbral):
        self.umbral = umbral 
    
    def handle_request(self, camion):
        if camion.data['temperatura'][-1] > self.umbral:
            print(f"Advertencia: Temperatura actual ({camion.data['temperatura'][-1]}°C) está por encima del umbral ({self.umbral}°C).")
        else:
            print(f"Temperatura actual ({camion.data['temperatura'][-1]}°C) está dentro del umbral.")
        
        if self.successor:
            self.successor.handle_request(camion)

class ComprobarVariacion(Handler):
    def handle_request(self, camion):
        nuevos_datos_temp = camion.data['temperatura'][len(camion.data['temperatura'])/2:]
        nuevos_datos_hum = camion.data['humedad'][len(camion.data['humedad'])/2:]
        variacion_temp = abs(nuevos_datos_temp[-1] - nuevos_datos_temp["temperaturas"][0])
        if variacion_temp > 2:
            print(f"Advertencia: Variación de temperatura mayor a 2°C: {variacion_temp}°C")
            
        variacion_humedad = abs(nuevos_datos_hum[-1] - nuevos_datos_hum[0])
        if variacion_humedad > 2:
            print(f"Advertencia: Variación de humedad mayor a 2%: {variacion_humedad}%")

        if self.successor:
            self.successor.handle_request(camion)