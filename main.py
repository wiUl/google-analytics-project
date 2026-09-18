import subprocess
import sys
import os


# PARTE 1 - Roda os arquivos locais e atualiza a planilha localmente
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


#PARTE 2 - Atualiza o arquivo na nuvem(teams/sharepoint)

FLOW_URL = (
    "ms-powerautomate:/console/flow/run"
    "?environmentid=Default-e0b8308a-8004-442e-bd3d-ec333d7809b7"
    "&workflowid=7ba33d61-aa70-490b-936a-b2b0c9406293"
    "&source=Other"
)

print("\nIniciando envio para o SharePoint...")

os.startfile(FLOW_URL)

print("Fluxo do Power Automate iniciado!")