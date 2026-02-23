"""
🔓 Brute Force MD5/SHA1 com Hashcat
Baixa e executa o Hashcat automaticamente.
Funciona com GPU AMD, NVIDIA e CPU.
"""

import hashlib
import subprocess
import os
import sys
import urllib.request
import zipfile
import time

# ============================================================
# Configuração
# ============================================================
PROJETO_DIR = os.path.dirname(os.path.abspath(__file__))
HASHCAT_DIR = os.path.join(PROJETO_DIR, "hashcat")
HASHCAT_URL = "https://hashcat.net/files/hashcat-6.2.6.7z"
HASHCAT_EXE = os.path.join(HASHCAT_DIR, "hashcat-6.2.6", "hashcat.exe")

# Senhas para gerar os hashes (as mesmas do hash.py)
SENHA_ALVO = "texto"


def gerar_hashes(senha):
    """Gera os hashes MD5 e SHA1 da senha."""
    md5 = hashlib.md5(senha.encode()).hexdigest()
    sha1 = hashlib.sha1(senha.encode()).hexdigest()
    return md5, sha1


def verificar_hashcat():
    """Verifica se o Hashcat está disponível."""
    # 1. Verifica no PATH do sistema
    try:
        result = subprocess.run(["hashcat", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Hashcat encontrado no PATH: {result.stdout.strip()}")
            return "hashcat"
    except FileNotFoundError:
        pass
    
    # 2. Verifica na pasta local
    if os.path.exists(HASHCAT_EXE):
        print(f"✅ Hashcat encontrado localmente: {HASHCAT_EXE}")
        return HASHCAT_EXE
    
    return None


def instrucoes_instalacao():
    """Mostra como instalar o Hashcat."""
    print()
    print("=" * 60)
    print("⚠️  HASHCAT NÃO ENCONTRADO")
    print("=" * 60)
    print()
    print("Para instalar o Hashcat no Windows:")
    print()
    print("  Opção 1 - Download manual (recomendado):")
    print(f"    1. Acesse: https://hashcat.net/hashcat/")
    print(f"    2. Baixe a versão binaries para Windows")
    print(f"    3. Extraia na pasta: {HASHCAT_DIR}")
    print(f"    4. Verifique que existe: {HASHCAT_EXE}")
    print()
    print("  Opção 2 - Chocolatey:")
    print("    choco install hashcat")
    print()
    print("  Opção 3 - Winget:")
    print("    winget install hashcat")
    print()
    print("Depois de instalar, rode este script novamente!")
    print("=" * 60)


def salvar_hash(hash_value, filename):
    """Salva o hash em um arquivo para o Hashcat."""
    filepath = os.path.join(PROJETO_DIR, filename)
    with open(filepath, "w") as f:
        f.write(hash_value + "\n")
    return filepath


def rodar_hashcat(hashcat_exe, hash_file, modo_hash, descricao):
    """
    Roda o Hashcat em modo brute force.
    
    modo_hash:
        0    = MD5
        100  = SHA1
    
    Modos de ataque (-a):
        0 = Dicionário
        1 = Combinação
        3 = Brute Force (máscara)
        6 = Dicionário + Máscara
        7 = Máscara + Dicionário
    
    Máscaras:
        ?l = Letra minúscula (a-z)
        ?u = Letra maiúscula (A-Z)
        ?d = Dígito (0-9)
        ?a = Todos os printáveis
        ?l?l?l?l?l = 5 letras minúsculas
    """
    print(f"\n{'='*60}")
    print(f"🔨 Hashcat - Brute Force {descricao}")
    print(f"{'='*60}")
    
    # Arquivo de saída para senhas encontradas
    output_file = os.path.join(PROJETO_DIR, f"cracked_{descricao.lower()}.txt")
    
    # Comando Hashcat:
    # -m 0       = tipo de hash (MD5)
    # -a 3       = modo ataque (brute force / máscara)
    # -o output  = arquivo de saída
    # --force    = força execução mesmo sem GPU otimizada
    # ?l?l?l?l?l = máscara: 5 letras minúsculas
    # --increment = testa de 1 a 5 caracteres
    cmd = [
        hashcat_exe,
        "-m", str(modo_hash),       # Tipo de hash
        "-a", "3",                   # Ataque: brute force (máscara)
        hash_file,                   # Arquivo com o hash alvo
        "--increment",               # Incrementar tamanho
        "--increment-min", "1",      # Mínimo: 1 caractere
        "--increment-max", "6",      # Máximo: 6 caracteres
        "?l?l?l?l?l?l",             # Máscara: até 6 letras minúsculas
        "-o", output_file,           # Saída
        "--force",                   # Forçar execução
        "--potfile-disable",         # Não usar cache de resultados
    ]
    
    print(f"\n📋 Comando: {' '.join(cmd)}\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(hashcat_exe),
            timeout=300  # Timeout de 5 minutos
        )
        
        elapsed = time.time() - start_time
        
        # Mostrar saída do Hashcat
        if result.stdout:
            # Filtrar linhas relevantes
            for line in result.stdout.split("\n"):
                if any(kw in line.lower() for kw in 
                       ["speed", "recovered", "progress", "time", "hash"]):
                    print(f"  {line.strip()}")
        
        if result.stderr and "error" in result.stderr.lower():
            print(f"\n⚠️  Erros: {result.stderr[:200]}")
        
        # Verificar resultado
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                content = f.read().strip()
            if content:
                # Formato: hash:senha
                senha_encontrada = content.split(":")[-1]
                print(f"\n✅ SENHA ENCONTRADA ({descricao}): {senha_encontrada}")
                print(f"   Tempo: {elapsed:.2f} segundos")
                return senha_encontrada
        
        print(f"\n❌ Senha não encontrada em {elapsed:.2f} segundos")
        print(f"   (Pode ser que a senha tenha caracteres fora da máscara ?l)")
        return None
        
    except subprocess.TimeoutExpired:
        print(f"\n⏰ Timeout atingido (120s). Senha muito complexa para brute force simples.")
        return None
    except Exception as e:
        print(f"\n❌ Erro ao rodar Hashcat: {e}")
        return None


def mostrar_comandos_manuais(md5_hash, sha1_hash):
    """Mostra os comandos para rodar manualmente."""
    print()
    print("=" * 60)
    print("📋 COMANDOS PARA RODAR MANUALMENTE")
    print("=" * 60)
    
    print(f"""
Hashes gerados:
  MD5:  {md5_hash}
  SHA1: {sha1_hash}

# ─── Brute Force MD5 (letras minúsculas, até 6 chars) ───
hashcat -m 0 -a 3 {md5_hash} ?l?l?l?l?l?l --increment --force

# ─── Brute Force SHA1 (letras minúsculas, até 6 chars) ───
hashcat -m 100 -a 3 {sha1_hash} ?l?l?l?l?l?l --increment --force

# ─── Com letras + números ───
hashcat -m 0 -a 3 {md5_hash} ?a?a?a?a?a?a --increment --force

# ─── Usando wordlist (dicionário) ───
hashcat -m 0 -a 0 {md5_hash} wordlist.txt --force

# ─── Verificar resultado ───
hashcat -m 0 --show {md5_hash}

Máscaras disponíveis:
  ?l = letras minúsculas (a-z)
  ?u = letras maiúsculas (A-Z)
  ?d = dígitos (0-9)
  ?s = símbolos (!@#$...)
  ?a = todos os acima
""")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("🔐 Brute Force de Hashes com Hashcat")
    print("=" * 60)
    
    # 1. Gerar hashes da senha alvo
    md5_hash, sha1_hash = gerar_hashes(SENHA_ALVO)
    print(f"   Senha alvo: {SENHA_ALVO}")
    print(f"   MD5:  {md5_hash}")
    print(f"   SHA1: {sha1_hash}")
    
    # 2. Sempre mostrar comandos manuais (para o relatório)
    mostrar_comandos_manuais(md5_hash, sha1_hash)
    
    # 3. Tentar rodar automaticamente
    hashcat_exe = verificar_hashcat()
    
    if not hashcat_exe:
        instrucoes_instalacao()
        sys.exit(1)
    
    # 4. Salvar hashes em arquivos
    md5_file = salvar_hash(md5_hash, "hash_md5.txt")
    sha1_file = salvar_hash(sha1_hash, "hash_sha1.txt")
    
    print(f"\n📁 Hashes salvos em:")
    print(f"   {md5_file}")
    print(f"   {sha1_file}")
    
    # 5. Rodar Hashcat - MD5
    resultado_md5 = rodar_hashcat(hashcat_exe, md5_file, 0, "MD5")
    
    # 6. Rodar Hashcat - SHA1
    resultado_sha1 = rodar_hashcat(hashcat_exe, sha1_file, 100, "SHA1")
    
    # 7. Resumo final
    print(f"\n{'='*60}")
    print("📊 RESUMO FINAL")
    print(f"{'='*60}")
    print(f"   MD5:  {resultado_md5 or 'Não encontrada'}")
    print(f"   SHA1: {resultado_sha1 or 'Não encontrada'}")
