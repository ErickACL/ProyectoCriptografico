import os
from unittest.mock import patch, MagicMock
from main.GenClaveMaestra import main

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
