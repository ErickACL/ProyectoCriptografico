import os, pytest
from bson import Binary
from unittest.mock import patch, MagicMock
from main.GenClaveMaestra import main
from main.shamir import make_random_shares, combine_shares

@patch('os.urandom')
@patch('main.GenClaveMaestra.MongoClient')
def test_main(mock_mongo_client, mock_urandom):
    # Configura el mock de os.urandom para devolver una clave predecible
    mock_urandom.return_value = bytes.fromhex('00112233445566778899aabbccddeeff')  # Ejemplo de clave predecible

    # Configura el mock de MongoDB
    mock_db = mock_mongo_client.return_value['distributed_keys']
    mock_collection = mock_db['fragments']

    # Simula la inserción en la base de datos
    mock_insert = MagicMock()
    mock_collection.insert_one = mock_insert

    # Ejecuta el script principal
    main()

    # Verifica que se insertaron los 5 fragmentos
    assert mock_insert.call_count == 5  # Se deben insertar 5 fragmentos

    # Valida que cada fragmento sea binario de 16 bytes
    for call in mock_insert.call_args_list:
        args, _ = call
        fragment = args[0]['fragment']
        assert isinstance(fragment, bytes)  # El fragmento debe ser bytes
        assert len(fragment) == 16  # El fragmento debe ser exactamente de 16 bytes

#Validar que los fragmentos generados cumplen con los parámetros
def test_valfrag():
    key_int = int.from_bytes(b'\x00\x11"3DUfw\x88\x99\xaa\xbb\xcc\xdd\xee\xff', byteorder="big")
    minimum = 3
    shares = 5

    _, fragments = make_random_shares(minimum, shares, key_int)
    
    assert len(fragments) == shares, f"Se esperaban {shares} fragmentos, pero se generaron {len(fragments)}."
    assert all(isinstance(frag, tuple) for frag in fragments), "Los fragmentos deben ser tuplas."
    assert all(len(frag) == 2 for frag in fragments), "Cada fragmento debe tener un ID y un valor."

#Probar que los fragmentos se pueden recombinar correctamente
@patch('main.GenClaveMaestra.MongoClient')
def test_recomfrag(mock_mongo_client):
    # Mock de la base de datos y la colección
    mock_db = mock_mongo_client.return_value['distributed_keys']
    mock_collection = mock_db['fragments']
    mock_insert = MagicMock()
    mock_collection.insert_one = mock_insert

    # Ejecutar la función principal
    main()

    # Verificar que se insertaron 5 fragmentos
    assert mock_insert.call_count == 5, f"Se esperaban 5 inserciones, pero se realizaron {mock_insert.call_count}."

    # Verificar la estructura de los datos insertados
    for call in mock_insert.call_args_list:
        fragment = call[0][0]  # Primer argumento del método insert_one
        assert 'id' in fragment, "Falta la clave 'id' en el documento insertado."
        assert 'fragment' in fragment, "Falta la clave 'fragment' en el documento insertado."
        assert isinstance(fragment['id'], int), "El ID del fragmento debe ser un entero."
        assert isinstance(fragment['fragment'], Binary), "El fragmento debe estar almacenado como Binary."

#Probar el manejo de errores al generar fragmentos
def test_errorfrag():
    key_int = int.from_bytes(b'\x00\x11"3DUfw\x88\x99\xaa\xbb\xcc\xdd\xee\xff', byteorder="big")
    minimum = 6  # Mayor que el número de fragmentos
    shares = 5

    with pytest.raises(ValueError, match="El número mínimo de fragmentos debe ser menor o igual al total."):
        make_random_shares(minimum, shares, key_int)

#Probar la conversion de fragmentos a binario
def test_fragbin():
    fragment = 123456789  # Valor ejemplo
    fragment_bin = fragment.to_bytes((fragment.bit_length() + 7) // 8, byteorder="big")
    
    assert isinstance(fragment_bin, bytes), "El fragmento convertido debe ser de tipo bytes."
    assert len(fragment_bin) > 0, "El fragmento convertido no debe estar vacío."


