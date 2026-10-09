"""Orquestra a atualização dos relatórios e monitora o fluxo PAD via arquivo de status.

Para monitorar o resultado real do Power Automate Desktop, configure o fluxo para
gravar output/flow_status.json ao terminar, com {"status": "success"} ou
{"status": "error", "message": "..."}.
"""
import json
import logging
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from urllib.parse import urlencode

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STATUS_FILE = OUTPUT_DIR / "flow_status.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "automacao.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("orquestrador")

SCRIPTS = [
    "script_resumo_trafego.py",
    "script_paginas.py",
    "script_aquisicao.py",
    "script_dispositivos.py",
    "script_localizacao.py",
    "script_eventos.py",
]

FLOW_BASE_URL = (
    "ms-powerautomate:/console/flow/run?environmentid=Default-e0b8308a-8004-442e-bd3d-ec333d7809b7&workflowid=679a067b-315b-4f09-bf94-2b4de4f5044a&source=Other"
)
FLOW_TIMEOUT_SECONDS = 1800
FLOW_POLL_SECONDS = 5


def executar_relatorios():
    for script in SCRIPTS:
        caminho_script = BASE_DIR / script
        logger.info("Iniciando script: %s", script)
        if not caminho_script.is_file():
            raise FileNotFoundError(f"Script não encontrado: {caminho_script}")

        resultado = subprocess.run(
            [sys.executable, str(caminho_script)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if resultado.stdout:
            logger.info("[%s] saída:\n%s", script, resultado.stdout.strip())
        if resultado.stderr:
            nivel = logging.ERROR if resultado.returncode else logging.WARNING
            logger.log(nivel, "[%s] mensagens:\n%s", script, resultado.stderr.strip())

        if resultado.returncode != 0:
            raise RuntimeError(
                f"{script} terminou com código {resultado.returncode}. "
                f"Consulte {LOG_DIR / 'automacao.log'}."
            )
        logger.info("Script concluído: %s", script)

    arquivo_excel = OUTPUT_DIR / "relatorio_site_inyaga.xlsx"
    if not arquivo_excel.is_file() or arquivo_excel.stat().st_size == 0:
        raise FileNotFoundError(
            f"O arquivo Excel não foi criado ou está vazio: {arquivo_excel}"
        )
    logger.info("Todos os relatórios foram atualizados: %s", arquivo_excel)


def iniciar_e_monitorar_fluxo():
    run_id = str(uuid.uuid4())
    # O runId permite localizar os logs específicos desta execução no PAD.
    separador = "&" if "?" in FLOW_BASE_URL else "?"
    flow_url = f"{FLOW_BASE_URL}{separador}{urlencode({'runId': run_id})}"

    # Remove um resultado antigo para não confundi-lo com a execução atual.
    try:
        STATUS_FILE.unlink(missing_ok=True)
    except OSError:
        logger.exception("Não foi possível limpar o status antigo: %s", STATUS_FILE)
        raise

    logger.info("Solicitando execução do Power Automate Desktop. runId=%s", run_id)
    try:
        #os.startfile(flow_url)
        os.startfile(FLOW_BASE_URL)
    except OSError:
        logger.exception("Não foi possível abrir a URL do Power Automate Desktop.")
        raise

    logger.info(
        "Solicitação enviada ao PAD; aguardando status em %s. "
        "Abrir a URL não confirma que o fluxo terminou.",
        STATUS_FILE,
    )
    limite = time.monotonic() + FLOW_TIMEOUT_SECONDS
    while time.monotonic() < limite:
        if STATUS_FILE.is_file():
            try:
                with STATUS_FILE.open("r", encoding="utf-8") as arquivo:
                    status = json.load(arquivo)
            except (OSError, json.JSONDecodeError):
                logger.exception("O arquivo de status existe, mas não pôde ser lido.")
                raise

            resultado = str(status.get("status", "")).strip().lower()
            if resultado == "success":
                logger.info("Fluxo PAD concluído com sucesso. runId=%s", run_id)
                return
            if resultado == "error":
                mensagem = status.get("message", "O fluxo informou erro sem detalhes.")
                logger.error("Fluxo PAD falhou. runId=%s; detalhe=%s", run_id, mensagem)
                raise RuntimeError(f"Falha no Power Automate Desktop: {mensagem}")
            logger.error("Status inválido em %s: %r", STATUS_FILE, status)
            raise ValueError("O status do PAD deve ser 'success' ou 'error'.")

        time.sleep(FLOW_POLL_SECONDS)

    logger.error(
        "Tempo esgotado aguardando o PAD. Nenhum status foi recebido em %s segundos. "
        "runId=%s",
        FLOW_TIMEOUT_SECONDS,
        run_id,
    )
    raise TimeoutError(
        "O PAD não gravou o arquivo de status dentro do prazo. "
        "Verifique se o fluxo foi iniciado e se as ações finais de status foram configuradas."
    )


if __name__ == "__main__":
    try:
        executar_relatorios()
        iniciar_e_monitorar_fluxo()
    except Exception:
        logger.exception("A automação foi encerrada com erro.")
        sys.exit(1)

    logger.info("Automação concluída com sucesso.")
