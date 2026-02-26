import socket
from common import calcular_hash

SERVER_IP = "192.168.105.118"  # IP do servidor
PORT = 5000

def quebrar_hash(hash_alvo, algoritmo, inicio, fim):
    for numero in range(inicio, fim):
        tentativa = str(numero).zfill(4)
        if calcular_hash(tentativa, algoritmo) == hash_alvo:
            return tentativa
    return None

def main():
    while True:
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.connect((SERVER_IP, PORT))

        dados = cliente.recv(1024).decode()

        if not dados:
            break

        hash_alvo, algoritmo, inicio, fim = dados.split(",")

        resultado = quebrar_hash(hash_alvo, algoritmo, int(inicio), int(fim))

        if resultado:
            cliente.send(resultado.encode())
            break
        else:
            cliente.send("NOT_FOUND".encode())

        cliente.close()

if __name__ == "__main__":
    main()