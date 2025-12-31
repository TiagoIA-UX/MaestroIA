from langchain_openai import ChatOpenAI
from pytrends.request import TrendReq
from maestroia.config.settings import (
    OPENAI_API_KEY,
    DEFAULT_LLM_MODEL,
    DEFAULT_TEMPERATURE,
)
from maestroia.core.state import MaestroState

llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model=DEFAULT_LLM_MODEL,
    temperature=DEFAULT_TEMPERATURE,
)

def agente_pesquisador(state: MaestroState) -> MaestroState:
    """
    Agente responsável por analisar o mercado e identificar tendências relevantes.
    """

    objetivo = state.get("objetivo", "Marketing digital")
    publico = state.get("publico_alvo", "Público geral")

    # Buscar tendências no Google Trends
    pytrends = TrendReq()
    keywords = [objetivo, publico]
    pytrends.build_payload(keywords, cat=0, timeframe='today 12-m', geo='', gprop='')
    trends_data = pytrends.interest_over_time()
    trends_summary = trends_data.head().to_string() if not trends_data.empty else "Dados de tendências não disponíveis."

    # Simulação de dados SEMrush (API paga - integrar chave real futuramente)
    semrush_data = f"Palavras-chave relacionadas: {objetivo} (volume estimado: 10k), {publico} (volume estimado: 5k). Concorrentes: Empresa A, Empresa B."

    prompt = f"""
    Analise o mercado de marketing digital considerando:

    Objetivo: {objetivo}
    Público-alvo: {publico}

    Dados do Google Trends:
    {trends_summary}

    Dados simulados do SEMrush:
    {semrush_data}

    Gere um resumo claro sobre:
    - Tendências atuais
    - Oportunidades
    - Riscos
    """

    resposta = llm.invoke(prompt)

    return {
        "pesquisa": resposta.content
    }
