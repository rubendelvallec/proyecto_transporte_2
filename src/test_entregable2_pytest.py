import pytest
import asyncio
from unittest.mock import MagicMock
from datetime import datetime
from io import StringIO
from unittest import mock
from entregable import Sistema, Camion, Estadistico, VerificarUmbralTemperatura, ComprobarVariacion, Variacion, Localizacion
from numpy import mean
import functools

def test_crear_sistema():
    # Prueba que se crea una instancia del sistema
    sistema = Sistema.get_instance("amazon")
    sistema2 = Sistema.get_instance("Vueling")
    assert sistema == sistema2
    assert len(sistema.camiones) == 0  

def test_agregar_camion():
    # Prueba que se agrega un camión al sistema
    sistema = Sistema.get_instance("amazon")
    camion = Camion(1, sistema, 500)
    
    assert len(sistema.camiones) == 1
    assert sistema.camiones[0].numero == 1

@pytest.mark.asyncio
async def test_temperatura():
    #Prueba de que se acutualizan bien los datos
    sistema = Sistema.get_instance("amazon")
    camion = Camion(1, sistema, 500)

    await camion.actualizar_datos()
    assert len(camion.data['temperatura']) > 0
@pytest.mark.asyncio
async def test_media():
    #Prueba de que se calcula bien la media
    sistema = Sistema.get_instance("amazon")
    camion = Camion(1, sistema, 500)

    await camion.actualizar_datos()
    await camion.actualizar_datos()

    assert mean(camion.data['temperatura']) == functools.reduce(lambda x, y: x+y, camion.data['temperatura']) / len(camion.data['temperatura'])

def test_fin_trayecto():
    # Verifica que el trayecto de un camión termina correctamente
    sistema = Sistema.get_instance("amazon")
    camion = Camion(1, sistema, 500)

    camion.tiempo_trayecto = 0  # Simulamos que el trayecto ha terminado
    
    assert camion.fin_trayecto() is True


def test_localizacion():
    # Verifica que la localización se convierta correctamente a OLC
    lat = (3, 30, 30, 'N')
    lon = (9, 30, 30, 'E')
    localizacion = Localizacion(lat, lon)
    
    olc_code = localizacion.gms_a_olc()
    
    assert len(olc_code) > 0  

@pytest.mark.asyncio
async def test_calculo_variacion_temperatura():
    #Probamos a ver si calcula bien la variacion
    sistema = Sistema.get_instance("amazon")
    camion = Camion(1, sistema, 500)

    camion.data['temperatura'] = [20, 22, 23, 25, 24, 23] 
    variacion = Variacion()
    resultado = await variacion.hacer_calculo(camion.data['temperatura'][0], camion.data['temperatura'][-1])
    assert resultado == 3