import pytest
from unittest.mock import patch, MagicMock
from bson import Binary

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../main')))
from main.GenClaveMaestra import main

# Mock de os.urandom para devolver una clave predecible
@patch('os.urandom')
# Mock de MongoDB para evitar conexión real
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

    # Verifica que la función de inserción se haya llamado con los fragmentos generados
    assert mock_insert.call_count == 5  # Se deben insertar 5 fragmentos
    args, _ = mock_insert.call_args_list[0]  # Obtiene los argumentos pasados al primer insert
    assert len(args[0]['fragment']) == 16  # Verifica que el fragmento sea de tipo Binary
    
    # Verifica que la clave maestra generada es la esperada
    expected_key = bytes.fromhex('00112233445566778899aabbccddeeff')
    assert args[0]['id'] == 1  # Comprobación del ID de fragmento (o lo que se espera)
    assert args[0]['fragment'] == Binary(expected_key)  # Verifica que el fragmento tiene el valor esperado
