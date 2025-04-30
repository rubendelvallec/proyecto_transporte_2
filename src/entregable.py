import asyncio
import random

#R1
class Sistema:
    _instance = None

    def __init__(self,nombre):
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
    async def actualizar_sistema(self):
        if len(self.camiones) == 0:
            raise Exception("El sistema no tiene camiones agregados, utilize 'agregar_camion'")
        while True:
            for camion in self.camiones:
                camion.actualizar_datos()
            await asyncio.sleep(5)