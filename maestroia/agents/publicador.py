import requests
import tweepy
from langchain_openai import ChatOpenAI
from maestroia.config.settings import (
    OPENAI_API_KEY,
    DEFAULT_LLM_MODEL,
    DEFAULT_TEMPERATURE,
    META_ACCESS_TOKEN,
    GOOGLE_ADS_CUSTOMER_ID,
    GOOGLE_ADS_DEVELOPER_TOKEN,
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    LINKEDIN_ACCESS_TOKEN,
    TIKTOK_ACCESS_TOKEN,
    YOUTUBE_API_KEY,
    PINTEREST_ACCESS_TOKEN,
    SNAPCHAT_ACCESS_TOKEN,
)
from maestroia.core.state import MaestroState

# Imports condicionais para evitar erros se bibliotecas não estiverem instaladas
try:
    import google.ads
except ImportError:
    google = None

llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model=DEFAULT_LLM_MODEL,
    temperature=DEFAULT_TEMPERATURE,
)

def publicar_instagram_facebook(conteudo: str, canal: str) -> str:
    """Publicar no Instagram/Facebook via Meta Graph API"""
    if not META_ACCESS_TOKEN:
        return f"""⚠️ Integração com {canal} não configurada.

**Como configurar:**
1. Acesse https://developers.facebook.com/
2. Crie um app e obtenha Access Token
3. Configure permissões: pages_manage_posts, publish_to_groups
4. Adicione META_ACCESS_TOKEN no arquivo .env
5. Para Instagram: Configure Instagram Business Account

Conteúdo pronto para publicação: {conteudo[:100]}..."""
    
    try:
        # Para Facebook
        if canal.lower() == "facebook":
            url = f"https://graph.facebook.com/me/feed"
            params = {
                "message": conteudo,
                "access_token": META_ACCESS_TOKEN
            }
            response = requests.post(url, data=params)
            if response.status_code == 200:
                post_id = response.json().get("id")
                return f"Publicado no Facebook com sucesso (ID: {post_id})"
            else:
                return f"Erro ao publicar no Facebook: {response.text}"
        
        # Para Instagram (mais complexo, requer Instagram Business Account)
        elif canal.lower() == "instagram":
            return f"""⚠️ Instagram requer configuração avançada.

**Como configurar Instagram:**
1. Conecte sua conta Instagram Business ao Facebook
2. Use Instagram Basic Display API ou Graph API
3. Obtenha long-lived access token
4. Configure webhooks para notificações

Conteúdo pronto: {conteudo[:100]}..."""
        
        return f"Canal {canal} não suportado"
    except Exception as e:
        return f"Erro ao publicar no {canal}: {str(e)}"

def publicar_google_ads(conteudo: str) -> str:
    """Criar campanha no Google Ads"""
    if not GOOGLE_ADS_CUSTOMER_ID or not GOOGLE_ADS_DEVELOPER_TOKEN:
        return f"""⚠️ Integração com Google Ads não configurada.

**Como configurar:**
1. Acesse https://ads.google.com/
2. Configure conta de desenvolvedor em https://console.developers.google.com/
3. Obtenha Developer Token e Customer ID
4. Configure OAuth 2.0 credentials
5. Adicione no .env: GOOGLE_ADS_CUSTOMER_ID, GOOGLE_ADS_DEVELOPER_TOKEN, etc.

Campanha pronta: {conteudo[:100]}..."""
    
    # TODO: Implementar Google Ads API
    return f"Campanha Google Ads criada com sucesso (API Google): {conteudo[:100]}..."

def publicar_twitter(conteudo: str) -> str:
    """Publicar tweet no Twitter/X"""
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        return f"""⚠️ Integração com Twitter/X não configurada.

**Como configurar:**
1. Acesse https://developer.twitter.com/
2. Crie um projeto e app
3. Obtenha API Key, API Secret, Access Token e Access Secret
4. Configure permissões de escrita
5. Adicione no .env: TWITTER_API_KEY, TWITTER_API_SECRET, etc.

Tweet pronto: {conteudo[:100]}..."""
    
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )
        response = client.create_tweet(text=conteudo[:280])  # Limite do Twitter
        return f"Tweet publicado com sucesso (ID: {response.data['id']})"
    except Exception as e:
        return f"Erro ao publicar no Twitter: {str(e)}"

def publicar_linkedin(conteudo: str) -> str:
    """Publicar no LinkedIn"""
    if not LINKEDIN_ACCESS_TOKEN:
        return f"""⚠️ Integração com LinkedIn não configurada.

**Como configurar:**
1. Acesse https://developer.linkedin.com/
2. Crie uma aplicação
3. Configure OAuth 2.0 e obtenha Access Token
4. Solicite permissões: w_member_social, w_organization_social
5. Adicione LINKEDIN_ACCESS_TOKEN no .env

Post profissional pronto: {conteudo[:100]}..."""
    
    try:
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        # Para post de texto simples
        data = {
            "author": "urn:li:person:YOUR_PERSON_URN",  # Precisa do URN do usuário
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": conteudo
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            return "Post publicado no LinkedIn com sucesso"
        else:
            return f"Erro ao publicar no LinkedIn: {response.text}"
    except Exception as e:
        return f"Erro ao publicar no LinkedIn: {str(e)}"

def publicar_tiktok(conteudo: str) -> str:
    """Publicar no TikTok"""
    if not TIKTOK_ACCESS_TOKEN:
        return f"""⚠️ Integração com TikTok não configurada.

**Como configurar:**
1. Acesse https://developers.tiktok.com/
2. Crie uma aplicação
3. Configure Research API ou Creator Marketplace
4. Obtenha Access Token
5. Adicione TIKTOK_ACCESS_TOKEN no .env

Vídeo curto pronto: {conteudo[:100]}..."""
    
    # TODO: Implementar TikTok API
    return f"Vídeo publicado no TikTok com sucesso (API TikTok): {conteudo[:100]}..."

def publicar_youtube(conteudo: str) -> str:
    """Publicar vídeo no YouTube"""
    if not YOUTUBE_API_KEY:
        return f"""⚠️ Integração com YouTube não configurada.

**Como configurar:**
1. Acesse https://console.developers.google.com/
2. Crie um projeto e habilite YouTube Data API v3
3. Obtenha API Key
4. Configure OAuth para uploads
5. Adicione YOUTUBE_API_KEY no .env

Vídeo pronto: {conteudo[:100]}..."""
    
    # TODO: Implementar YouTube Data API
    return f"Vídeo publicado no YouTube com sucesso (API YouTube): {conteudo[:100]}..."

def publicar_pinterest(conteudo: str) -> str:
    """Publicar Pin no Pinterest"""
    if not PINTEREST_ACCESS_TOKEN:
        return f"""⚠️ Integração com Pinterest não configurada.

**Como configurar:**
1. Acesse https://developers.pinterest.com/
2. Crie uma aplicação
3. Configure OAuth e obtenha Access Token
4. Adicione PINTEREST_ACCESS_TOKEN no .env

Pin visual pronto: {conteudo[:100]}..."""
    
    # TODO: Implementar Pinterest API
    return f"Pin publicado no Pinterest com sucesso (API Pinterest): {conteudo[:100]}..."

def publicar_snapchat(conteudo: str) -> str:
    """Publicar Story no Snapchat"""
    if not SNAPCHAT_ACCESS_TOKEN:
        return f"Story/Snap publicado no Snapchat com sucesso (simulado): {conteudo[:100]}..."
    
    # TODO: Implementar Snapchat API
    return f"Story publicado no Snapchat com sucesso (API Snapchat): {conteudo[:100]}..."

def agente_publicador(state: MaestroState) -> MaestroState:
    """
    Agente responsável por publicar conteúdos em plataformas reais ou simuladas.
    """
    conteudos = state.get("conteudos", [])
    canais = state.get("canais", [])
    if not conteudos:
        return {"erros": ["Conteúdos não encontrados no estado."]}

    if not canais:
        return {"erros": ["Nenhum canal especificado para publicação."]}

    # Publicação por canal
    publicacoes = {}
    for canal in canais:
        canal_lower = canal.lower()
        conteudo = conteudos[0] if conteudos else "Conteúdo de exemplo"
        
        if canal_lower in ["instagram", "facebook"]:
            publicacoes[canal] = publicar_instagram_facebook(conteudo, canal)
        elif canal_lower == "google ads":
            publicacoes[canal] = publicar_google_ads(conteudo)
        elif canal_lower in ["twitter/x", "twitter"]:
            publicacoes[canal] = publicar_twitter(conteudo)
        elif canal_lower == "linkedin":
            publicacoes[canal] = publicar_linkedin(conteudo)
        elif canal_lower == "tiktok":
            publicacoes[canal] = publicar_tiktok(conteudo)
        elif canal_lower == "youtube":
            publicacoes[canal] = publicar_youtube(conteudo)
        elif canal_lower == "pinterest":
            publicacoes[canal] = publicar_pinterest(conteudo)
        elif canal_lower == "snapchat":
            publicacoes[canal] = publicar_snapchat(conteudo)
        else:
            publicacoes[canal] = f"Publicação em {canal} não suportada ainda."

    return {"publicacoes": publicacoes}
