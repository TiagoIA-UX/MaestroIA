from langchain_openai import ChatOpenAI
from openai import OpenAI
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
client = OpenAI(api_key=OPENAI_API_KEY)

def agente_criador_conteudo(state: MaestroState) -> MaestroState:
    """
    Agente responsável por criar conteúdos de marketing
    com base na estratégia definida.
    """

    estrategia = state.get("estrategia")
    canais = state.get("canais", ["Instagram", "Google"])

    if not estrategia:
        return {
            "erros": ["Estratégia não encontrada no estado."]
        }

    prompt = f"""
    Você é um especialista em criação de conteúdo para marketing digital.

    Estratégia:
    {estrategia}

    Crie conteúdos adequados para os seguintes canais:
    {", ".join(canais)}

    Para cada canal, gere:
    - Uma ideia principal
    - Um texto base de publicação
    - Sugestão de imagem (descrição para geração com IA)

    Retorne o conteúdo de forma organizada.
    """

    resposta = llm.invoke(prompt)

    # Gerar imagem com DALL-E baseada na sugestão
    image_prompt = "Uma imagem inspiradora para marketing digital sustentável"
    try:
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = image_response.data[0].url
    except Exception as e:
        image_url = f"Erro ao gerar imagem: {str(e)}"

    return {
        "conteudos": [resposta.content],
        "imagens": [image_url]
    }
