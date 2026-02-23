"""
🔓 Brute Force MD5 com GPU (PyCUDA)
Requer: pip install pycuda
Requer: NVIDIA CUDA Toolkit instalado
Requer: Placa de vídeo NVIDIA com suporte a CUDA
"""

import hashlib
import numpy as np
import time

# ============================================================
# Tenta importar PyCUDA - se não tiver, mostra instrução
# ============================================================
try:
    import pycuda.autoinit
    import pycuda.driver as cuda
    from pycuda.compiler import SourceModule
    GPU_DISPONIVEL = True
except ImportError:
    GPU_DISPONIVEL = False
    print("⚠️  PyCUDA não instalado. Instale com:")
    print("   pip install pycuda")
    print("   (Requer NVIDIA CUDA Toolkit)")
    print()

# ============================================================
# Kernel CUDA - Implementação completa do MD5 na GPU
# ============================================================
CUDA_KERNEL = """
#include <stdint.h>

// Constantes MD5 (RFC 1321)
__device__ const uint32_t K[64] = {
    0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
    0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
    0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
    0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
    0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
    0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
    0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
    0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
    0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
    0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
    0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
    0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
    0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
    0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
    0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
    0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391
};

// Shifts por rodada
__device__ const uint32_t S[64] = {
    7,12,17,22, 7,12,17,22, 7,12,17,22, 7,12,17,22,
    5, 9,14,20, 5, 9,14,20, 5, 9,14,20, 5, 9,14,20,
    4,11,16,23, 4,11,16,23, 4,11,16,23, 4,11,16,23,
    6,10,15,21, 6,10,15,21, 6,10,15,21, 6,10,15,21
};

// Rotação à esquerda
__device__ uint32_t rotate_left(uint32_t x, uint32_t n) {
    return (x << n) | (x >> (32 - n));
}

// Calcula MD5 de uma string curta (até 55 bytes)
__device__ void md5_compute(const char *msg, int len, uint32_t *digest) {
    // Bloco de 64 bytes (512 bits) zerado
    uint32_t M[16];
    // Zerar
    for (int i = 0; i < 16; i++) M[i] = 0;
    
    // Copiar a mensagem byte a byte
    unsigned char *block = (unsigned char *)M;
    for (int i = 0; i < len; i++) {
        block[i] = (unsigned char)msg[i];
    }
    
    // Padding: adicionar bit 1 (0x80)
    block[len] = 0x80;
    
    // Tamanho em bits (little-endian) nos últimos 8 bytes
    uint64_t bit_len = (uint64_t)len * 8;
    M[14] = (uint32_t)(bit_len);
    M[15] = (uint32_t)(bit_len >> 32);
    
    // Valores iniciais MD5
    uint32_t a0 = 0x67452301;
    uint32_t b0 = 0xefcdab89;
    uint32_t c0 = 0x98badcfe;
    uint32_t d0 = 0x10325476;
    
    uint32_t A = a0, B = b0, C = c0, D = d0;
    
    // 64 rodadas
    for (int i = 0; i < 64; i++) {
        uint32_t F, g;
        if (i < 16) {
            F = (B & C) | ((~B) & D);
            g = i;
        } else if (i < 32) {
            F = (D & B) | ((~D) & C);
            g = (5 * i + 1) % 16;
        } else if (i < 48) {
            F = B ^ C ^ D;
            g = (3 * i + 5) % 16;
        } else {
            F = C ^ (B | (~D));
            g = (7 * i) % 16;
        }
        
        F = F + A + K[i] + M[g];
        A = D;
        D = C;
        C = B;
        B = B + rotate_left(F, S[i]);
    }
    
    digest[0] = a0 + A;
    digest[1] = b0 + B;
    digest[2] = c0 + C;
    digest[3] = d0 + D;
}

// Converte índice global -> string candidata
// charset = "abcdefghijklmnopqrstuvwxyz0123456789" (36 chars)
__device__ void index_to_password(long long idx, int pwd_len, const char *charset, 
                                   int charset_size, char *pwd) {
    for (int i = pwd_len - 1; i >= 0; i--) {
        pwd[i] = charset[idx % charset_size];
        idx /= charset_size;
    }
    pwd[pwd_len] = '\\0';
}

// ============================================================
// KERNEL PRINCIPAL: Cada thread testa uma senha diferente
// ============================================================
__global__ void brute_force_md5(
    const uint32_t target_a, const uint32_t target_b,
    const uint32_t target_c, const uint32_t target_d,
    const char *charset, int charset_size,
    int pwd_len, long long offset,
    char *result, int *found
) {
    long long idx = (long long)(blockIdx.x * blockDim.x + threadIdx.x) + offset;
    
    // Se já encontrou, não fazer nada
    if (*found) return;
    
    // Gerar a senha candidata a partir do índice
    char pwd[16];
    index_to_password(idx, pwd_len, charset, charset_size, pwd);
    
    // Calcular MD5
    uint32_t digest[4];
    md5_compute(pwd, pwd_len, digest);
    
    // Comparar com o hash alvo
    if (digest[0] == target_a && digest[1] == target_b &&
        digest[2] == target_c && digest[3] == target_d) {
        *found = 1;
        // Copiar a senha encontrada para result
        for (int i = 0; i <= pwd_len; i++) {
            result[i] = pwd[i];
        }
    }
}
"""

def hex_to_md5_ints(hex_str):
    """Converte hash hex string em 4 uint32 little-endian (formato interno MD5)."""
    import struct
    raw = bytes.fromhex(hex_str)
    return struct.unpack('<4I', raw)

def brute_force_gpu(target_hash_hex, max_len=6):
    """Brute force MD5 usando GPU."""
    
    if not GPU_DISPONIVEL:
        print("❌ GPU não disponível. Use hash.py (versão CPU).")
        return None
    
    # Compilar o kernel CUDA
    mod = SourceModule(CUDA_KERNEL)
    kernel = mod.get_function("brute_force_md5")
    
    # Charset: a-z + 0-9
    charset = "abcdefghijklmnopqrstuvwxyz0123456789"
    charset_size = len(charset)
    
    # Converter hash alvo para 4 inteiros (formato MD5 interno)
    target_a, target_b, target_c, target_d = hex_to_md5_ints(target_hash_hex)
    
    # Enviar charset para GPU
    charset_gpu = cuda.mem_alloc(len(charset))
    cuda.memcpy_htod(charset_gpu, charset.encode())
    
    # Buffers de resultado
    result = np.zeros(16, dtype=np.int8)
    found = np.zeros(1, dtype=np.int32)
    result_gpu = cuda.mem_alloc(result.nbytes)
    found_gpu = cuda.mem_alloc(found.nbytes)
    
    # Configuração de blocos/threads
    threads_per_block = 256
    blocks = 1024  # 256 * 1024 = 262.144 threads simultâneas
    batch_size = threads_per_block * blocks
    
    print(f"🎮 GPU Brute Force MD5")
    print(f"   Hash alvo: {target_hash_hex}")
    print(f"   Charset:   {charset} ({charset_size} chars)")
    print(f"   Threads:   {batch_size:,} por batch")
    print()
    
    start_time = time.time()
    total_tentativas = 0
    
    for pwd_len in range(1, max_len + 1):
        total_combinacoes = charset_size ** pwd_len
        print(f"📐 Testando senhas de {pwd_len} caractere(s): {total_combinacoes:,} combinações")
        
        offset = 0
        while offset < total_combinacoes:
            # Resetar flag de encontrado
            cuda.memcpy_htod(found_gpu, np.zeros(1, dtype=np.int32))
            cuda.memcpy_htod(result_gpu, np.zeros(16, dtype=np.int8))
            
            # Executar kernel!
            kernel(
                np.uint32(target_a), np.uint32(target_b),
                np.uint32(target_c), np.uint32(target_d),
                charset_gpu, np.int32(charset_size),
                np.int32(pwd_len), np.int64(offset),
                result_gpu, found_gpu,
                block=(threads_per_block, 1, 1),
                grid=(blocks, 1)
            )
            
            # Verificar se encontrou
            cuda.memcpy_dtoh(found, found_gpu)
            total_tentativas += min(batch_size, total_combinacoes - offset)
            
            if found[0] == 1:
                cuda.memcpy_dtoh(result, result_gpu)
                senha = ''.join(chr(b) for b in result if b != 0)
                elapsed = time.time() - start_time
                rate = total_tentativas / elapsed if elapsed > 0 else 0
                print(f"\n✅ Senha encontrada: {senha}")
                print(f"   Tempo: {elapsed:.2f} segundos")
                print(f"   Tentativas: {total_tentativas:,}")
                print(f"   Velocidade: {rate:,.0f} hashes/segundo")
                return senha
            
            offset += batch_size
        
        elapsed = time.time() - start_time
        rate = total_tentativas / elapsed if elapsed > 0 else 0
        print(f"   ...concluído ({rate:,.0f} hashes/s)")
    
    print(f"\n❌ Senha não encontrada em {max_len} caracteres.")
    print(f"   Tentativas totais: {total_tentativas:,}")
    return None


def brute_force_cpu(target_hash_hex, max_len=6):
    """Brute force MD5 usando CPU (fallback)."""
    import itertools
    import string
    
    chars = string.ascii_lowercase + string.digits
    
    print(f"🖥️  CPU Brute Force MD5")
    print(f"   Hash alvo: {target_hash_hex}")
    print()
    
    start_time = time.time()
    total = 0
    
    for pwd_len in range(1, max_len + 1):
        print(f"📐 Testando {pwd_len} caractere(s)...")
        for tentativa in itertools.product(chars, repeat=pwd_len):
            senha = ''.join(tentativa)
            total += 1
            if hashlib.md5(senha.encode()).hexdigest() == target_hash_hex:
                elapsed = time.time() - start_time
                rate = total / elapsed if elapsed > 0 else 0
                print(f"\n✅ Senha encontrada: {senha}")
                print(f"   Tempo: {elapsed:.2f} segundos")
                print(f"   Tentativas: {total:,}")
                print(f"   Velocidade: {rate:,.0f} hashes/segundo")
                return senha
    
    print(f"\n❌ Não encontrada em {max_len} caracteres.")
    return None


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    # Senha de teste
    senha_alvo = "texto"
    hash_alvo = hashlib.md5(senha_alvo.encode()).hexdigest()
    
    print(f"🔐 Senha original: {senha_alvo}")
    print(f"   MD5: {hash_alvo}")
    print("=" * 50)
    
    if GPU_DISPONIVEL:
        print("\n🟢 GPU detectada! Usando CUDA...\n")
        brute_force_gpu(hash_alvo, max_len=6)
    else:
        print("\n🟡 GPU não disponível. Usando CPU...\n")
        brute_force_cpu(hash_alvo, max_len=6)
