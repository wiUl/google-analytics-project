"""Utilitários de validação e atualização segura das planilhas de relatórios."""
import logging
from pathlib import Path

import pandas as pd

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "automacao.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("google_analytics")


def atualizar_planilha(arquivo, dados_novos, nome_aba, chaves):
    """Valida dados e substitui somente a aba correspondente após consolidar."""
    arquivo = Path(arquivo)
    arquivo.parent.mkdir(parents=True, exist_ok=True)

    if not isinstance(dados_novos, pd.DataFrame):
        raise TypeError(f"{nome_aba}: os dados recebidos não são um DataFrame.")

    if dados_novos.empty:
        mensagem = (
            f"{nome_aba}: a API retornou zero linhas. "
            "A aba existente foi preservada para evitar apagar dados por engano."
        )
        logger.warning(mensagem)
        if arquivo.exists():
            return False
        raise ValueError(f"{mensagem} O arquivo Excel ainda não existe.")

    if dados_novos.columns.duplicated().any():
        raise ValueError(f"{nome_aba}: existem nomes de colunas duplicados.")

    colunas_chave = [chaves] if isinstance(chaves, str) else list(chaves)
    faltantes = [c for c in colunas_chave if c not in dados_novos.columns]
    if faltantes:
        raise ValueError(f"{nome_aba}: faltam colunas-chave: {faltantes}")

    if dados_novos[colunas_chave].isna().any().any():
        raise ValueError(f"{nome_aba}: há valores vazios nas colunas-chave {colunas_chave}.")

    if arquivo.exists():
        try:
            antigo = pd.read_excel(arquivo, sheet_name=nome_aba)
        except ValueError:
            logger.warning("A aba '%s' não existe em %s; será criada.", nome_aba, arquivo)
            antigo = pd.DataFrame()
        except Exception:
            logger.exception("Falha ao ler a aba '%s' do arquivo %s.", nome_aba, arquivo)
            raise
    else:
        antigo = pd.DataFrame()

    if not antigo.empty:
        faltantes_antigo = [c for c in colunas_chave if c not in antigo.columns]
        if faltantes_antigo:
            raise ValueError(
                f"{nome_aba}: a planilha existente não contém as chaves {faltantes_antigo}."
            )

    quantidade_nova = len(dados_novos)
    combinado = pd.concat([antigo, dados_novos], ignore_index=True)
    combinado = combinado.drop_duplicates(subset=colunas_chave, keep="last")
    combinado = combinado.sort_values(by=colunas_chave, kind="stable").reset_index(drop=True)

    try:
        modo = "a" if arquivo.exists() else "w"
        with pd.ExcelWriter(
            arquivo,
            engine="openpyxl",
            mode=modo,
            if_sheet_exists="replace" if modo == "a" else None,
        ) as writer:
            combinado.to_excel(writer, sheet_name=nome_aba, index=False)
    except PermissionError:
        logger.exception(
            "Não foi possível salvar %s. Feche o Excel se o arquivo estiver aberto.",
            arquivo,
        )
        raise
    except Exception:
        logger.exception("Falha ao salvar a aba '%s' em %s.", nome_aba, arquivo)
        raise

    logger.info(
        "%s: validação concluída; %s linhas recebidas, %s linhas finais; arquivo=%s",
        nome_aba, quantidade_nova, len(combinado), arquivo,
    )
    return True
