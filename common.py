import hashlib

def calcular_hash(texto, algoritmo="md5"):
    h = hashlib.new(algoritmo)
    h.update(texto.encode())
    return h.hexdigest()