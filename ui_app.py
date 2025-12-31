import streamlit as st
import requests
import json
import os
import hashlib
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.units import inch
from maestroia.graphs.marketing_graph import build_marketing_graph

# Arquivo para armazenar usuários
USERS_FILE = "users.json"

def load_users():
    """Carrega usuários do arquivo JSON"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Salva usuários no arquivo JSON"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def hash_password(password):
    """Hash da senha para armazenamento seguro"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Valida formato do email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Valida força da senha"""
    if len(password) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "A senha deve conter pelo menos uma letra maiúscula"
    if not re.search(r'[a-z]', password):
        return False, "A senha deve conter pelo menos uma letra minúscula"
    if not re.search(r'\d', password):
        return False, "A senha deve conter pelo menos um número"
    return True, "Senha válida"

# Configuração da página
st.set_page_config(
    page_title="MaestroIA - Marketing Inteligente",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para design elegante
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }

    .result-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-left: 4px solid #28a745;
    }

    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem 0;
    }

    .status-success {
        color: #28a745;
        font-weight: bold;
    }

    .status-info {
        color: #17a2b8;
        font-weight: bold;
    }

    .content-block {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .agent-progress {
        background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.2rem;
        font-size: 0.9rem;
    }

    .tab-content {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1rem;
    }

    .download-btn {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        font-weight: bold;
        text-decoration: none;
        display: inline-block;
        margin: 0.5rem;
        transition: transform 0.2s;
    }

    .download-btn:hover {
        transform: scale(1.05);
    }

    .agent-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho elegante
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; font-size: 2.5rem;">🎯 MaestroIA</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">Orquestração Inteligente de Agentes de Marketing Digital</p>
</div>
""", unsafe_allow_html=True)

# Sistema de login elegante
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Sistema de autenticação com abas
    tab_login, tab_register = st.tabs(["🔐 Entrar", "📝 Cadastrar-se"])

    with tab_register:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📝 Criar Nova Conta")
        st.markdown("**Bem-vindo ao MaestroIA!** Crie sua conta para começar a orquestrar campanhas de marketing inteligentes.")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            reg_display_name = st.text_input(
                "👤 Nome de Exibição",
                placeholder="Como gostaria de ser chamado?",
                help="Este nome será usado nas boas-vindas e interface",
                key="reg_display_name"
            )
            reg_email = st.text_input(
                "📧 Email",
                placeholder="seu@email.com",
                help="Será usado para confirmação e notificações importantes",
                key="reg_email"
            )
            reg_password = st.text_input(
                "🔒 Senha",
                type="password",
                placeholder="Crie uma senha forte",
                help="Mínimo 8 caracteres, com maiúscula, minúscula e número",
                key="reg_password"
            )
            reg_confirm_password = st.text_input(
                "🔒 Confirmar Senha",
                type="password",
                placeholder="Digite a senha novamente",
                key="reg_confirm_password"
            )

            if st.button("📝 Criar Conta", type="primary", use_container_width=True):
                users = load_users()

                # Validações
                if not reg_display_name.strip():
                    st.error("❌ Digite um nome de exibição!")
                elif not validate_email(reg_email):
                    st.error("❌ Digite um email válido!")
                elif reg_email in users:
                    st.error("❌ Este email já está cadastrado!")
                elif reg_password != reg_confirm_password:
                    st.error("❌ As senhas não coincidem!")
                else:
                    valid, msg = validate_password(reg_password)
                    if not valid:
                        st.error(f"❌ {msg}")
                    else:
                        # Criar conta
                        users[reg_email] = {
                            "display_name": reg_display_name.strip(),
                            "password_hash": hash_password(reg_password),
                            "created_at": str(st.session_state.get("current_time", "2025-12-30"))
                        }
                        save_users(users)

                        st.success("✅ Conta criada com sucesso!")
                        st.info("Agora você pode fazer login com suas credenciais.")
                        st.balloons()

        st.markdown('</div>', unsafe_allow_html=True)

    with tab_login:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔐 Fazer Login")
        st.markdown("Entre com suas credenciais para acessar o MaestroIA.")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_email = st.text_input(
                "📧 Email",
                placeholder="seu@email.com",
                key="login_email"
            )
            login_password = st.text_input(
                "🔒 Senha",
                type="password",
                placeholder="Digite sua senha",
                key="login_password"
            )

            if st.button("🚀 Entrar", type="primary", use_container_width=True):
                users = load_users()

                if not login_email or not login_password:
                    st.error("❌ Preencha email e senha!")
                elif login_email not in users:
                    st.error("❌ Email não encontrado! Faça seu cadastro primeiro.")
                elif users[login_email]["password_hash"] != hash_password(login_password):
                    st.error("❌ Senha incorreta!")
                else:
                    # Login bem-sucedido
                    st.session_state.logged_in = True
                    st.session_state.display_name = users[login_email]["display_name"]
                    st.session_state.email = login_email
                    st.success(f"✅ Bem-vindo de volta, {users[login_email]['display_name']}!")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
else:
    col1, col2 = st.columns([3, 1])
    with col1:
        display_name = st.session_state.get("display_name", "Usuário")
        st.markdown(f'<div class="metric-card">👋 Bem-vindo, <strong>{display_name}</strong>!</div>', unsafe_allow_html=True)
    with col2:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    graph = build_marketing_graph()

    # Abas estilizadas
    tab1, tab2, tab3 = st.tabs(["📝 Criar Campanha", "⚙️ Configurações", "📊 Resultados"])

    with tab1:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        st.markdown("### 🎯 Configure sua Campanha")

        col1, col2 = st.columns(2)
        with col1:
            objetivo = st.text_area(
                "Objetivo da Campanha",
                placeholder="Ex: Aumentar agendamento de consultas em 30% nos próximos 3 meses...",
                height=100
            )
        with col2:
            publico = st.text_area(
                "Público-Alvo",
                placeholder="Ex: Mulheres 25-55 anos interessadas em bem-estar emocional...",
                height=100
            )

        col3, col4 = st.columns(2)
        with col3:
            canais = st.multiselect(
                "📢 Canais de Divulgação",
                ["Instagram", "Facebook", "Google Ads", "Twitter/X", "LinkedIn", "TikTok", "YouTube", "Pinterest", "Snapchat"],
                default=["Instagram", "Facebook"]
            )
        with col4:
            orcamento = st.number_input("💰 Orçamento (R$)", min_value=0.0, value=1500.0, step=100.0)

        if st.button("🚀 Executar Campanha", type="primary", use_container_width=True):
            if not objetivo or not publico or not canais:
                st.error("❌ Preencha todos os campos obrigatórios!")
            else:
                # Barra de progresso elegante
                progress_container = st.container()
                with progress_container:
                    st.markdown("### 🔄 Executando Campanha...")
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    agentes = [
                        ("🔍 Pesquisador", "Analisando mercado e tendências"),
                        ("🎯 Estrategista", "Desenvolvendo estratégia de marketing"),
                        ("✍️ Criador de Conteúdo", "Gerando conteúdos otimizados"),
                        ("📤 Publicador", "Publicando em canais selecionados"),
                        ("📊 Otimizador", "Otimizando performance"),
                        ("🎼 Maestro", "Orquestrando resultados finais")
                    ]

                    for i, (agente, descricao) in enumerate(agentes):
                        status_text.markdown(f'<div class="agent-progress">{agente}: {descricao}</div>', unsafe_allow_html=True)
                        progress_bar.progress((i + 1) / len(agentes))
                        import time
                        time.sleep(1.0)  # Simular processamento

                # Executar campanha
                state = {
                    "objetivo": objetivo,
                    "publico_alvo": publico,
                    "canais": canais,
                    "orcamento": orcamento
                }
                result = graph.invoke(state)
                st.session_state.last_result = result
                st.session_state.campaign_executed = True
                st.session_state.campaign_data = state

                status_text.markdown('<div class="status-success">✅ Campanha concluída com sucesso!</div>', unsafe_allow_html=True)
                progress_bar.progress(1.0)

                st.balloons()

        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Configurações de Redes Sociais")
        st.info("Configure suas chaves de API para integrações reais. Deixe vazio para usar simulações.")

        with st.expander("📘 Meta (Instagram/Facebook)"):
            st.text_input("Access Token", type="password", key="meta_token")
            st.text_input("App ID", key="meta_app_id")

        with st.expander("🐦 Twitter/X"):
            st.text_input("API Key", type="password", key="twitter_api_key")
            st.text_input("API Secret", type="password", key="twitter_api_secret")
            st.text_input("Access Token", type="password", key="twitter_access_token")
            st.text_input("Access Token Secret", type="password", key="twitter_access_secret")

        with st.expander("💼 LinkedIn"):
            st.text_input("Access Token", type="password", key="linkedin_token")

        with st.expander("🎵 TikTok"):
            st.text_input("Access Token", type="password", key="tiktok_token")

        with st.expander("📺 YouTube"):
            st.text_input("API Key", type="password", key="youtube_key")

        with st.expander("📌 Pinterest"):
            st.text_input("Access Token", type="password", key="pinterest_token")

        with st.expander("👻 Snapchat"):
            st.text_input("Access Token", type="password", key="snapchat_token")

        if st.button("💾 Salvar Configurações"):
            st.success("Configurações salvas! (Nota: Ainda não persistidas - implementar futuramente)")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        if "campaign_executed" in st.session_state and st.session_state.campaign_executed:
            result = st.session_state.last_result
            campaign_data = st.session_state.get("campaign_data", {})

            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            st.markdown("### 📊 Resultados da Campanha")

            # Resumo da campanha
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown("#### 📋 Resumo da Campanha")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🎯 Objetivo", len(campaign_data.get("objetivo", "")))
            with col2:
                st.metric("👥 Público", len(campaign_data.get("publico_alvo", "")))
            with col3:
                st.metric("📢 Canais", len(campaign_data.get("canais", [])))
            with col4:
                st.metric("💰 Orçamento", f"R$ {campaign_data.get('orcamento', 0):.0f}")
            st.markdown('</div>', unsafe_allow_html=True)

            # Resultados organizados
            if "pesquisa" in result:
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown("#### 🔍 Análise de Mercado")
                st.markdown('<div class="content-block">', unsafe_allow_html=True)
                st.write(result["pesquisa"])
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if "conteudos" in result:
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown("#### ✍️ Conteúdos Gerados")
                for i, conteudo in enumerate(result["conteudos"], 1):
                    with st.expander(f"📝 Conteúdo {i}"):
                        st.markdown('<div class="content-block">', unsafe_allow_html=True)
                        # Limpar markdown para exibição
                        conteudo_limpo = conteudo.replace('**', '').replace('*', '').replace('#', '')
                        st.write(conteudo_limpo)
                        st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if "publicacoes" in result:
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown("#### 🚀 Status das Publicações")
                for canal, status in result["publicacoes"].items():
                    if "simulado" in status.lower():
                        st.info(f"📱 {canal}: {status}")
                    else:
                        st.success(f"📱 {canal}: {status}")
                st.markdown('</div>', unsafe_allow_html=True)

            if "imagens" in result:
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown("#### 🖼️ Imagens Geradas")
                for img_url in result["imagens"]:
                    if img_url.startswith("http"):
                        st.image(img_url, caption="Imagem gerada pela IA", use_column_width=True)
                    else:
                        st.info(f"📝 Descrição da imagem: {img_url}")
                st.markdown('</div>', unsafe_allow_html=True)

            # Botões de ação elegantes
            st.markdown("### 🎮 Ações da Campanha")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("✅ Aprovar e Publicar", type="primary", use_container_width=True):
                    st.success("Publicação aprovada! (Integração real pendente)")

            with col2:
                if st.button("🔄 Ajustar Campanha", use_container_width=True):
                    st.info("Recarregue a página e ajuste os parâmetros.")

            with col3:
                # Download JSON
                result_json = json.dumps(result, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📄 Baixar JSON",
                    data=result_json,
                    file_name="campanha_maestroia.json",
                    mime="application/json",
                    use_container_width=True
                )

            with col4:
                # Download PDF
                pdf_buffer = gerar_pdf_campanha(result, campaign_data.get("objetivo", ""), campaign_data.get("publico_alvo", ""), campaign_data.get("canais", []), campaign_data.get("orcamento", 0))
                st.download_button(
                    label="📕 Baixar PDF",
                    data=pdf_buffer,
                    file_name="relatorio_campanha_maestroia.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            st.info("🎯 Execute uma campanha primeiro para ver os resultados.")
            st.markdown('</div>', unsafe_allow_html=True)


def gerar_pdf_campanha(result, objetivo, publico, canais, orcamento):
    """Gera um PDF com os resultados da campanha"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Estilos customizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
    )
    normal_style = styles['Normal']

    story = []

    # Título
    story.append(Paragraph("Relatório da Campanha MaestroIA", title_style))
    story.append(Spacer(1, 12))

    # Informações da campanha
    story.append(Paragraph("Informações da Campanha", heading_style))
    story.append(Paragraph(f"<b>Objetivo:</b> {objetivo}", normal_style))
    story.append(Paragraph(f"<b>Público-Alvo:</b> {publico}", normal_style))
    story.append(Paragraph(f"<b>Canais:</b> {', '.join(canais)}", normal_style))
    story.append(Paragraph(f"<b>Orçamento:</b> R$ {orcamento:.2f}", normal_style))
    story.append(Spacer(1, 20))

    # Resultados
    if "pesquisa" in result:
        story.append(Paragraph("Análise de Mercado", heading_style))
        story.append(Paragraph(result["pesquisa"], normal_style))
        story.append(Spacer(1, 12))

    if "conteudos" in result:
        story.append(Paragraph("Conteúdos Gerados", heading_style))
        for i, conteudo in enumerate(result["conteudos"], 1):
            story.append(Paragraph(f"Conteúdo {i}:", styles['Heading3']))
            # Limpar markdown e HTML
            conteudo_limpo = conteudo.replace('*', '').replace('#', '').replace('**', '')
            story.append(Paragraph(conteudo_limpo, normal_style))
            story.append(Spacer(1, 8))
        story.append(Spacer(1, 12))

    if "publicacoes" in result:
        story.append(Paragraph("Publicações", heading_style))
        for canal, status in result["publicacoes"].items():
            story.append(Paragraph(f"<b>{canal}:</b> {status}", normal_style))
        story.append(Spacer(1, 12))

    # Imagens (se houver URLs válidas)
    if "imagens" in result:
        story.append(Paragraph("Imagens Geradas", heading_style))
        for img_url in result["imagens"]:
            if img_url.startswith("http"):
                try:
                    # Tentar baixar e adicionar imagem
                    response = requests.get(img_url)
                    if response.status_code == 200:
                        img_buffer = BytesIO(response.content)
                        img = RLImage(img_buffer, width=4*inch, height=3*inch)
                        story.append(img)
                        story.append(Spacer(1, 12))
                except:
                    story.append(Paragraph(f"Imagem: {img_url}", normal_style))
            else:
                story.append(Paragraph(f"Descrição da imagem: {img_url}", normal_style))

    # Rodapé
    story.append(Spacer(1, 30))
    story.append(Paragraph("Relatório gerado pelo MaestroIA", styles['Italic']))

    doc.build(story)
    buffer.seek(0)
    return buffer