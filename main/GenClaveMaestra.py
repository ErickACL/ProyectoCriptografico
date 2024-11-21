import os
from pymongo import MongoClient
from bson import Binary
from main.shamir import make_random_shares

def main():
    # Generar clave maestra
    key = os.urandom(16)
    key_int = int.from_bytes(key, byteorder="big")

    # Fragmentar la clave maestra
    minimum = 3  # Mmínimo de fragmentos requeridos
    shares = 5  # Total de fragmentos a generar

    print(f"Clave maestra generada (binario): {key}")
    print(f"Valores antes de la generación de fragmentos: minimum={minimum}, shares={shares}")

    try:
        _, fragments = make_random_shares(minimum, shares, key_int)
        print("Fragmentos generados (binarios):", fragments)
    except ValueError as e:
        print(f"Error al generar los fragmentos: {e}")
        return  # Salir si ocurre un error

    # Conecta a MongoDB
    client = MongoClient("mongodb://172.16.19.219:27017/")
    db = client['distributed_keys']
    collection = db['fragments']

    # Almacenar los fragmentos en la base de datos como enteros binarios
    for idx, (id_frag, fragment) in enumerate(fragments):
        # Convertir el fragmento a un número binario que se ajuste al tamaño de 16 bytes
        fragment_bin = fragment.to_bytes((fragment.bit_length() + 7) // 8, byteorder="big")
        collection.insert_one({"id": id_frag, "fragment": Binary(fragment_bin)})

    print("Fragmentos enviados al nodo secundario en formato binario.")

if __name__ == "__main__":
    main()
