import pytest

# Función simple que queremos probar
def suma(a, b):
    return a + b

# Prueba unitaria
def test_suma():
    assert suma(2, 3) == 5  # Verifica que la suma de 2 y 3 sea 5

def test_suma_negativos():
    assert suma(-1, -1) == -2  # Verifica que la suma de -1 y -1 sea -2

def test_suma_cero():
    assert suma(0, 0) == 0  # Verifica que la suma de 0 y 0 sea 0
