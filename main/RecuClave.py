from pymongo import MongoClient
from main.shamir import recover_secret

# Función para conectar con MongoDB y obtener fragmentos
def obtener_fragmentos():
    # Conectar al nodo secundario de MongoDB
    client = MongoClient("mongodb://172.16.19.219:27017/")
    db = client['distributed_keys']
    collection = db['fragments']
    
    # Obtener todos los fragmentos almacenados
    fragmentos = list(collection.find())
    
    # Extraer los fragmentos (id y fragmento) como tuplas
    shares = [(fragmento['id'], int.from_bytes(fragmento['fragment'], byteorder="big")) for fragmento in fragmentos]
    
    return shares

# Función para reconstruir la clave maestra
def reconstruir_clave(shares):
    # Recuperar la clave secreta a partir de los fragmentos
    clave_maestra_recuperada = recover_secret(shares)
    clave_maestra_bin = clave_maestra_recuperada.to_bytes(16, byteorder="big")  # Convertir a binario
    return clave_maestra_bin

# Función principal
def main():
    # Obtener los fragmentos
    fragmentos = obtener_fragmentos()
    
    if len(fragmentos) < 2:
        print("No hay suficientes fragmentos para reconstruir la clave.")
        return

    # Ordenar los fragmentos por el id (en caso de que estén desordenados)
    fragmentos = sorted(fragmentos, key=lambda x: x[0])
    
    # Reconstruir la clave maestra
    clave_maestra = reconstruir_clave(fragmentos)
    
    # Imprimir la clave maestra recuperada
    print(f"Clave maestra recuperada (binario): {clave_maestra}")

if __name__ == "__main__":
    main()