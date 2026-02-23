"""
🔓 Brute Force de Hashes MD5 e SHA1
Atividade individual - N1
Gera combinações e verifica se o hash corresponde ao hash alvo.
"""

import hashlib
import itertools
import string
import time


def calcular_hashes(senha):
    """Calcula os hashes MD5 e SHA1 de uma senha."""
    md5 = hashlib.md5(senha.encode()).hexdigest()
    sha1 = hashlib.sha1(senha.encode()).hexdigest()
    return md5, sha1


def brute_force(hash_alvo, tipo_hash, max_len=8):
    """
    Brute force para encontrar a senha que gera o hash alvo.
    
    Parâmetros:
        hash_alvo: hash em hexadecimal para quebrar
        tipo_hash: 'md5' ou 'sha1'
        max_len: tamanho máximo da senha a testar
    
    Retorna:
        (senha_encontrada, tempo_gasto) ou (None, tempo_gasto)
    """
    chars = string.ascii_lowercase + string.digits  # a-z, 0-9
    
    # Seleciona a função de hash
    if tipo_hash == 'md5':
        hash_func = hashlib.md5
    else:
        hash_func = hashlib.sha1
    
    start_time = time.time()
    tentativas = 0
    
    for tamanho in range(1, max_len + 1):
        for tentativa in itertools.product(chars, repeat=tamanho):
            senha = ''.join(tentativa)
            tentativas += 1
            
            if hash_func(senha.encode()).hexdigest() == hash_alvo:
                tempo = time.time() - start_time
                return senha, tempo, tentativas
    
    tempo = time.time() - start_time
    return None, tempo, tentativas


def testar_senha(senha):
    """Testa brute force de uma senha para MD5 e SHA1."""
    print(f"\n{'='*60}")
    print(f"🔐 Senha alvo: \"{senha}\"")
    print(f"{'='*60}")
    
    # Calcular hashes
    md5_hash, sha1_hash = calcular_hashes(senha)
    print(f"   MD5:  {md5_hash}")
    print(f"   SHA1: {sha1_hash}")
    
    resultados = {}
    
    # --- Brute Force MD5 ---
    print(f"\n🔨 Iniciando brute force MD5...")
    senha_md5, tempo_md5, tent_md5 = brute_force(md5_hash, 'md5')
    
    if senha_md5:
        print(f"   ✅ String encontrada (MD5): {senha_md5}")
        print(f"   ⏱️  Tempo: {tempo_md5:.2f} segundos")
        print(f"   🔢 Tentativas: {tent_md5:,}")
    else:
        print(f"   ❌ Não encontrada em {tempo_md5:.2f} segundos")
    
    resultados['md5'] = {'senha': senha_md5, 'tempo': tempo_md5, 'tentativas': tent_md5}
    
    # --- Brute Force SHA1 ---
    print(f"\n🔨 Iniciando brute force SHA1...")
    senha_sha1, tempo_sha1, tent_sha1 = brute_force(sha1_hash, 'sha1')
    
    if senha_sha1:
        print(f"   ✅ String encontrada (SHA1): {senha_sha1}")
        print(f"   ⏱️  Tempo: {tempo_sha1:.2f} segundos")
        print(f"   🔢 Tentativas: {tent_sha1:,}")
    else:
        print(f"   ❌ Não encontrada em {tempo_sha1:.2f} segundos")
    
    resultados['sha1'] = {'senha': senha_sha1, 'tempo': tempo_sha1, 'tentativas': tent_sha1}
    
    return resultados


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("🔓 Brute Force de Hashes MD5 e SHA1")
    print("Atividade Individual - N1")
    
    # ─── Senha 1: fornecida pelo professor ───
    resultado1 = testar_senha("texto")
    
    # ─── Senha 2: alterada pelo aluno ───
    resultado2 = testar_senha("sol")
    
    # ─── Senha 3: mais longa para comparação ───
    resultado3 = testar_senha("abc123")
    
    # ============================================================
    # Comparação de tempos
    # ============================================================
    print(f"\n{'='*60}")
    print("📊 COMPARAÇÃO DE TEMPOS (MD5)")
    print(f"{'='*60}")
    print(f"{'Senha':<15} {'Tamanho':<10} {'Tempo (s)':<15} {'Tentativas':<15}")
    print(f"{'-'*55}")
    
    for senha, res in [("texto", resultado1), ("sol", resultado2), ("abc123", resultado3)]:
        t = res['md5']['tempo']
        n = res['md5']['tentativas']
        print(f"{senha:<15} {len(senha):<10} {t:<15.2f} {n:<15,}")
    
    print(f"\n{'='*60}")
    print("📊 COMPARAÇÃO DE TEMPOS (SHA1)")
    print(f"{'='*60}")
    print(f"{'Senha':<15} {'Tamanho':<10} {'Tempo (s)':<15} {'Tentativas':<15}")
    print(f"{'-'*55}")
    
    for senha, res in [("texto", resultado1), ("sol", resultado2), ("abc123", resultado3)]:
        t = res['sha1']['tempo']
        n = res['sha1']['tentativas']
        print(f"{senha:<15} {len(senha):<10} {t:<15.2f} {n:<15,}")
    
    print(f"\n💡 Conclusão: Senhas mais longas e complexas demoram")
    print(f"   exponencialmente mais tempo para serem quebradas.")
    print(f"   Isso ocorre porque o número de combinações cresce")
    print(f"   como charset^tamanho (36^n neste caso).")