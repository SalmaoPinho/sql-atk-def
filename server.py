import socket
import time
import threading
from common import calcular_hash

HOST = '0.0.0.0'
PORT = 5000

HASH_ALVO = calcular_hash("54321")
ALGORITMO = "md5"

INTERVALO_TOTAL = 100000   # 00000 a 99999
TAMANHO_BLOCO = 1000

blocos = []
indice_bloco = 0
senha_encontrada = False
lock = threading.Lock()
inicio_tempo = None

def gerar_blocos():
    for inicio in range(0, INTERVALO_TOTAL, TAMANHO_BLOCO):
        yield (inicio, min(inicio + TAMANHO_BLOCO, INTERVALO_TOTAL))

def tratar_cliente(conn, addr):
    global indice_bloco, senha_encontrada

    print(f"Conectado com {addr}")

    with lock:
        if indice_bloco >= len(blocos) or senha_encontrada:
            conn.close()
            return

        inicio, fim = blocos[indice_bloco]
        indice_bloco += 1

    mensagem = f"{HASH_ALVO},{ALGORITMO},{inicio},{fim}"
    conn.send(mensagem.encode())

    resposta = conn.recv(1024).decode()

    if resposta != "NOT_FOUND":
        with lock:
            senha_encontrada = True
        fim_tempo = time.time() 
        print(f"\nSenha encontrada: {resposta}")
        print(f"Tempo total: {fim_tempo - inicio_tempo:.4f} segundos")

    conn.close()

def main():
    global blocos, inicio_tempo   # <-- CORREÇÃO AQUI

    blocos = list(gerar_blocos())

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen()

    print("Servidor aguardando conexões...")
    
    inicio_tempo = time.time()   # agora altera a variável global

    while not senha_encontrada:
        conn, addr = servidor.accept()
        thread = threading.Thread(target=tratar_cliente, args=(conn, addr))
        thread.start()

    servidor.close()

if __name__ == "__main__":
    main()