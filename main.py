import subprocess
import sys

scripts = [
    "script_resumo_trafego.py",
    "script_paginas.py",
    "script_aquisicao.py",
    "script_dispositivos.py",
    "script_localizacao.py",
    "script_eventos.py"
]

for script in scripts:
    print(f"\nExecutando: {script}")

    resultado = subprocess.run([sys.executable, script])

    if resultado.returncode != 0:
        print(f"Erro ao executar {script}")
        sys.exit(1)

    print(f"{script} executado com sucessso!")

print("\nTodos os relatórios foram atualizados.")