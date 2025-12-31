import requests
import streamlit as st
import json
import os
import hashlib
import re
from io import BytesIO
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.units import inch
from maestroia.graphs.marketing_graph import build_marketing_graph

# Mercado Pago
import mercadopago
from maestroia.config.settings import MERCADOPAGO_ACCESS_TOKEN

# Função utilitária para criar link de pagamento Mercado Pago
def criar_preferencia_pagamento(email, plano_nome, valor):
    if not MERCADOPAGO_ACCESS_TOKEN:
        return None
    sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)
    preference_data = {
        "items": [
            {
                "title": f"Plano {plano_nome}",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(valor)
            }
        ],
        "payer": {
            "email": email
        }
    }
    preference_response = sdk.preference().create(preference_data)
    return preference_response["response"].get("init_point")
# Arquivo para armazenar usuários
USERS_FILE = "users.json"

# Planos disponíveis
PLANOS = {
    "free": {
        "nome": "Gratuito",
        "campanhas_mes": 2,
        "canais_max": 2,
        "suporte": "Comunidade",
        "preco": 0,
        "periodo_teste": 7  # dias
    },
    "starter": {
        "nome": "Starter",
        "campanhas_mes": 10,
        "canais_max": 5,
        "suporte": "Email",
        "preco": 49.90,
        "periodo_teste": 14
    },
    "professional": {
        "nome": "Professional",
        "campanhas_mes": 50,
        "canais_max": 10,
        "suporte": "Prioritário",
        "preco": 149.90,
        "periodo_teste": 30
    },
    "enterprise": {
        "nome": "Enterprise",
        "campanhas_mes": -1,  # ilimitado
        "canais_max": -1,     # ilimitado
        "suporte": "24/7",
        "preco": 499.90,
        "periodo_teste": 30
    }
}

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

def get_user_plan_status(user_data):
    """Verifica status do plano do usuário"""
    plano = user_data.get("plano", "free")
    data_cadastro = datetime.fromisoformat(user_data.get("created_at", datetime.now().isoformat()))
    campanhas_usadas = user_data.get("campanhas_mes", 0)

    # Verifica se está no período de teste
    periodo_teste = PLANOS[plano]["periodo_teste"]
    data_fim_teste = data_cadastro + timedelta(days=periodo_teste)
    em_teste = datetime.now() < data_fim_teste

    # Verifica limite de campanhas
    limite_campanhas = PLANOS[plano]["campanhas_mes"]
    if limite_campanhas == -1:  # ilimitado
        campanhas_disponiveis = float('inf')
    else:
        campanhas_disponiveis = max(0, limite_campanhas - campanhas_usadas)

    return {
        "plano": plano,
        "em_teste": em_teste,
        "dias_teste_restantes": max(0, (data_fim_teste - datetime.now()).days),
        "campanhas_disponiveis": campanhas_disponiveis,
        "limite_campanhas": limite_campanhas,
        "pago": user_data.get("pago", False)
    }

def pode_executar_campanha(user_data):
    """Verifica se usuário pode executar campanha"""
    status = get_user_plan_status(user_data)
    return status["em_teste"] or status["pago"] or status["campanhas_disponiveis"] > 0

def incrementar_campanha_usuario(email):
    """Incrementa contador de campanhas do usuário"""
    users = load_users()
    if email in users:
        users[email]["campanhas_mes"] = users[email].get("campanhas_mes", 0) + 1
        save_users(users)

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

    .agent-result-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }

    .agent-result-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    }

    .agent-pesquisador { border-left-color: #17a2b8; }
    .agent-estrategista { border-left-color: #ffc107; }
    .agent-criador { border-left-color: #28a745; }
    .agent-publicador { border-left-color: #dc3545; }
    .agent-otimizador { border-left-color: #6f42c1; }
    .agent-maestro { border-left-color: #e83e8c; }

    .agent-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #eee;
    }

    .agent-icon {
        font-size: 2rem;
        margin-right: 1rem;
        background: rgba(0,0,0,0.1);
        padding: 0.5rem;
        border-radius: 50%;
    }

    .agent-title {
        margin: 0;
        font-size: 1.3rem;
        font-weight: bold;
    }

    .agent-subtitle {
        margin: 0.2rem 0 0 0;
        color: #666;
        font-size: 0.9rem;
    }

    .plan-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border: 2px solid transparent;
        transition: all 0.3s ease;
        position: relative;
        color: #222 !important;
    }

    .plan-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }

    .plan-popular {
        border-color: #667eea;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    }

    .plan-popular::after {
        content: '⭐ MAIS POPULAR';
        position: absolute;
        top: -10px;
        left: 50%;
        transform: translateX(-50%);
        background: #667eea;
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }

    .plan-price {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
        text-align: center;
        margin: 1rem 0;
    }
    .plan-card button, .plan-card .stButton > button {
        color: #222 !important;
        font-weight: bold;
        background: #f8f9fa;
        border-radius: 20px;
        border: 1px solid #667eea;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        padding: 0.5rem 1.2rem;
        transition: background 0.2s;
    }
    /* Botão Fazer Upgrade do Starter em branco */
    .plan-popular ~ div .stButton > button, .plan-popular .stButton > button {
        color: #fff !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: 1px solid #667eea;
    }
    .plan-popular ~ div .stButton > button:hover, .plan-popular .stButton > button:hover {
        background: #4b3c91 !important;
        color: #fff !important;
    }

    .plan-price .currency {
        font-size: 1rem;
        vertical-align: super;
    }

    .plan-price .period {
        font-size: 0.8rem;
        color: #666;
        font-weight: normal;
    }

    .plan-free {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
    }

    .plan-free .plan-price {
        color: white;
    }

    .status-success {
        color: #28a745;
        font-weight: bold;
    }

    .status-info {
        color: #17a2b8;
        font-weight: bold;
    }

    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }

    .content-block {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
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

    .trial-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(102, 126, 234, 0); }
        100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0); }
    }

    .upgrade-prompt {
        background: linear-gradient(135deg, #ffc107 0%, #ff8c00 100%);
        color: #333;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        border: 2px solid #fff3cd;
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

# Verificar se há usuário logado persistentemente
if not st.session_state.logged_in:
    users = load_users()
    for email, user_data in users.items():
        if user_data.get("logged_in", False):
            st.session_state.logged_in = True
            st.session_state.email = email
            st.session_state.display_name = user_data.get("display_name", "Usuário")
            break

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
                    users[login_email]["logged_in"] = True
                    save_users(users)
                    st.session_state.logged_in = True
                    st.session_state.display_name = users[login_email]["display_name"]
                    st.session_state.email = login_email
                    st.success(f"✅ Bem-vindo de volta, {users[login_email]['display_name']}!")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
else:
    # Carregar dados do usuário
    users = load_users()
    user_email = st.session_state.email
    user_data = users.get(user_email, {})
    display_name = st.session_state.get("display_name", "Usuário")

    # Verificar status do plano
    plan_status = get_user_plan_status(user_data)
    plano_info = PLANOS[plan_status["plano"]]

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'<div class="metric-card">👋 Bem-vindo, <strong>{display_name}</strong>!</div>', unsafe_allow_html=True)

        # Banner de período de teste ou upgrade
        if plan_status["em_teste"]:
            st.markdown(f"""
            <div class="trial-banner">
                🎁 <strong>Período de Teste Ativo!</strong><br>
                Você tem <strong>{plan_status['dias_teste_restantes']} dias</strong> restantes no plano {plano_info['nome']}<br>
                <small>Campanhas disponíveis: {plan_status['campanhas_disponiveis'] if plan_status['campanhas_disponiveis'] != float('inf') else 'Ilimitadas'}</small>
            </div>
            """, unsafe_allow_html=True)
        elif not plan_status["pago"] and plan_status["campanhas_disponiveis"] <= 2:
            st.markdown(f"""
            <div class="upgrade-prompt">
                ⚠️ <strong>Limite Próximo!</strong><br>
                Você tem apenas <strong>{plan_status['campanhas_disponiveis']}</strong> campanhas restantes este mês.<br>
                <small>Faça upgrade para continuar criando campanhas ilimitadas!</small>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        # Status do plano
        if plan_status["pago"]:
            st.success(f"💎 {plano_info['nome']}")
        elif plan_status["em_teste"]:
            st.info(f"🎁 Teste {plano_info['nome']}")
        else:
            st.warning(f"🆓 {plano_info['nome']}")

        if st.button("🚪 Sair", use_container_width=True):
            users = load_users()
            if user_email in users:
                users[user_email]["logged_in"] = False
                save_users(users)
            st.session_state.logged_in = False
            st.rerun()

    graph = build_marketing_graph()

    # Abas estilizadas
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Criar Campanha", "💎 Planos & Pagamento", "⚙️ Configurações", "📊 Resultados", "📅 Agendamento"])

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
            # Limitar canais baseado no plano
            max_canais = PLANOS[plan_status["plano"]]["canais_max"]
            if max_canais == -1:  # ilimitado
                max_canais = 9  # todos disponíveis

            canais_opcoes = ["Instagram", "Facebook", "Google Ads", "Twitter/X", "LinkedIn", "TikTok", "YouTube", "Pinterest", "Snapchat"]
            canais = st.multiselect(
                f"📢 Canais de Divulgação (máx. {max_canais})",
                canais_opcoes,
                default=["Instagram", "Facebook"][:max_canais]
            )
        with col4:
            orcamento = st.number_input("💰 Orçamento (R$)", min_value=0.0, value=1500.0, step=100.0)

        # Verificar se pode executar campanha
        pode_executar = pode_executar_campanha(user_data)
        limite_canais_ok = len(canais) <= PLANOS[plan_status["plano"]]["canais_max"] or PLANOS[plan_status["plano"]]["canais_max"] == -1

        if not pode_executar:
            if plan_status["em_teste"]:
                st.warning("⏰ Seu período de teste expirou! Faça upgrade para continuar.")
            else:
                st.warning("📊 Você atingiu o limite de campanhas do mês. Faça upgrade para continuar.")
        elif not limite_canais_ok:
            st.warning(f"📢 Seu plano permite no máximo {PLANOS[plan_status['plano']]['canais_max']} canais. Reduza a seleção ou faça upgrade.")

        # Botão condicional
        if st.button("🚀 Executar Campanha", type="primary", use_container_width=True, disabled=not (pode_executar and limite_canais_ok)):
            if not objetivo or not publico or not canais:
                st.error("❌ Preencha todos os campos obrigatórios!")
            elif not pode_executar:
                st.error("❌ Você não tem permissão para executar campanhas. Verifique seu plano.")
            elif not limite_canais_ok:
                st.error(f"❌ Seu plano permite no máximo {PLANOS[plan_status['plano']]['canais_max']} canais.")
            else:
                # Incrementar contador de campanhas
                incrementar_campanha_usuario(user_email)

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

                st.success("🎉 Vá para a aba '📊 Resultados' para ver os resultados organizados por agentes e gerenciar as publicações!")

                st.balloons()

        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        st.markdown("### 💎 Planos e Pagamentos")

        # Status atual do plano
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Seu Plano", plano_info['nome'])
        with col2:
            if plan_status["em_teste"]:
                st.metric("Dias de Teste", plan_status["dias_teste_restantes"])
            else:
                st.metric("Status", "Pago" if plan_status["pago"] else "Gratuito")
        with col3:
            if plan_status["limite_campanhas"] == -1:
                st.metric("Campanhas", "Ilimitadas")
            else:
                st.metric("Campanhas Disponíveis", f"{plan_status['campanhas_disponiveis']}/{plan_status['limite_campanhas']}")

        st.markdown("---")

        # Planos disponíveis
        st.markdown("### 🛒 Escolha seu Plano")

        col1, col2, col3, col4 = st.columns(4)

        # Plano Gratuito
        with col1:
            st.markdown("""
            <div class="plan-card plan-free">
                <h3>🆓 Gratuito</h3>
                <div class="plan-price">
                    <span class="currency">R$</span>0<span class="period">/mês</span>
                </div>
                <ul>
                    <li>2 campanhas/mês</li>
                    <li>2 canais máximo</li>
                    <li>7 dias de teste</li>
                    <li>Suporte comunitário</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            if plan_status["plano"] == "free":
                st.success("✅ Plano Atual")

        # Plano Starter
        with col2:
            st.markdown("""
            <div class="plan-card plan-popular">
                <h3>🚀 Starter</h3>
                <div class="plan-price">
                    <span class="currency">R$</span>49,90<span class="period">/mês</span>
                </div>
                <ul>
                    <li>10 campanhas/mês</li>
                    <li>5 canais máximo</li>
                    <li>14 dias de teste</li>
                    <li>Suporte por email</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            if plan_status["plano"] == "starter":
                st.success("✅ Plano Atual")
            else:
                if st.button("✨ Fazer Upgrade", key="upgrade_starter", use_container_width=True):
                    payment_url = criar_preferencia_pagamento(user_email, "Starter", 49.90)
                    if payment_url:
                        st.markdown(f"[Clique aqui para pagar com Mercado Pago]({payment_url})", unsafe_allow_html=True)
                        st.info("Após o pagamento, seu plano será ativado manualmente ou automaticamente via webhook.")
                    else:
                        st.error("Configuração do Mercado Pago ausente. Contate o suporte.")

        # Plano Professional
        with col3:
            st.markdown("""
            <div class="plan-card">
                <h3>💼 Professional</h3>
                <div class="plan-price">
                    <span class="currency">R$</span>149,90<span class="period">/mês</span>
                </div>
                <ul>
                    <li>50 campanhas/mês</li>
                    <li>10 canais máximo</li>
                    <li>30 dias de teste</li>
                    <li>Suporte prioritário</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            if plan_status["plano"] == "professional":
                st.success("✅ Plano Atual")
            else:
                btn_pro = st.button("🚀 Upgrade Pro", key="upgrade_pro", use_container_width=True)
                if btn_pro:
                    payment_url = criar_preferencia_pagamento(user_email, "Professional", 149.90)
                    if payment_url:
                        st.markdown(f"[Clique aqui para pagar com Mercado Pago]({payment_url})", unsafe_allow_html=True)
                        st.info("Após o pagamento, seu plano será ativado manualmente ou automaticamente via webhook.")
                    else:
                        st.error("Configuração do Mercado Pago ausente. Contate o suporte.")

        # Plano Enterprise
        with col4:
            st.markdown("""
            <div class="plan-card">
                <h3>🏢 Enterprise</h3>
                <div class="plan-price">
                    <span class="currency">R$</span>499,90<span class="period">/mês</span>
                </div>
                <ul>
                    <li>Campanhas ilimitadas</li>
                    <li>Canais ilimitados</li>
                    <li>30 dias de teste</li>
                    <li>Suporte 24/7</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            if plan_status["plano"] == "enterprise":
                st.success("✅ Plano Atual")
            else:
                btn_ent = st.button("💎 Upgrade Enterprise", key="upgrade_enterprise", use_container_width=True)
                if btn_ent:
                    payment_url = criar_preferencia_pagamento(user_email, "Enterprise", 499.90)
                    if payment_url:
                        st.markdown(f"[Clique aqui para pagar com Mercado Pago]({payment_url})", unsafe_allow_html=True)
                        st.info("Após o pagamento, seu plano será ativado manualmente ou automaticamente via webhook.")
                    else:
                        st.error("Configuração do Mercado Pago ausente. Contate o suporte.")

        st.markdown("---")

        # Informações de pagamento
        st.markdown("### 💳 Informações de Pagamento")
        st.info("💡 Pagamentos 100% seguros via Mercado Pago. Após o pagamento, seu plano é ativado automaticamente. Suporte a cartão, boleto e Pix.")

        with st.expander("🔧 Como Funciona o Pagamento"):
            st.markdown("""
            **Fluxo de Pagamento:**
            1. Escolha o plano desejado
            2. Clique em "Fazer Upgrade"
            3. Sistema redireciona para gateway de pagamento
            4. Após confirmação, plano é ativado automaticamente
            5. Receba fatura mensal por email

            **Formas de Pagamento:**
            - Cartão de Crédito
            - Boleto Bancário
            - PIX
            - Transferência Bancária

            **Política de Reembolso:**
            - 30 dias para reembolso total
            - Suporte disponível 24/7
            """)

        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
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

    with tab4:
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

            # Resultados organizados por agentes
            st.markdown("### 🤖 Relatório da Orquestração por Agentes")

            # Agente Pesquisador
            if "pesquisa" in result:
                st.markdown("""
                <div class="agent-result-card agent-pesquisador">
                    <div class="agent-header">
                        <div class="agent-icon">🔍</div>
                        <div>
                            <div class="agent-title">Pesquisador</div>
                            <div class="agent-subtitle">Análise de mercado e tendências</div>
                        </div>
                    </div>
                    <div class="content-block">
                """, unsafe_allow_html=True)
                st.write(result["pesquisa"])
                st.markdown('</div></div>', unsafe_allow_html=True)

            # Agente Estrategista
            if "estrategia" in result:
                st.markdown("""
                <div class="agent-result-card agent-estrategista">
                    <div class="agent-header">
                        <div class="agent-icon">🎯</div>
                        <div>
                            <div class="agent-title">Estrategista</div>
                            <div class="agent-subtitle">Desenvolvimento de estratégias de marketing</div>
                        </div>
                    </div>
                    <div class="content-block">
                """, unsafe_allow_html=True)
                st.write(result["estrategia"])
                st.markdown('</div></div>', unsafe_allow_html=True)

            # Agente Criador de Conteúdo
            if "conteudos" in result:
                st.markdown("""
                <div class="agent-result-card agent-criador">
                    <div class="agent-header">
                        <div class="agent-icon">✍️</div>
                        <div>
                            <div class="agent-title">Criador de Conteúdo</div>
                            <div class="agent-subtitle">Produção de conteúdos otimizados por rede social</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Inicializar estado de aprovação se não existir
                if "conteudos_aprovados" not in st.session_state:
                    st.session_state.conteudos_aprovados = {}

                for i, conteudo in enumerate(result["conteudos"], 1):
                    canal_nome = result.get('canais', [''])[i-1] if i <= len(result.get('canais', [])) else 'Geral'
                    
                    with st.expander(f"📝 Conteúdo {i} - {canal_nome}", expanded=True):
                        st.markdown('<div class="content-block">', unsafe_allow_html=True)
                        # Limpar markdown para exibição
                        conteudo_limpo = conteudo.replace('**', '').replace('*', '').replace('#', '')
                        st.write(conteudo_limpo)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Botões de aprovação
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            if st.button(f"✅ Aprovar {i}", key=f"aprovar_{i}", use_container_width=True):
                                st.session_state.conteudos_aprovados[i] = True
                                st.success(f"Conteúdo {i} aprovado!")
                                st.rerun()
                        with col2:
                            if st.button(f"❌ Rejeitar {i}", key=f"rejeitar_{i}", use_container_width=True):
                                st.session_state.conteudos_aprovados[i] = False
                                st.error(f"Conteúdo {i} rejeitado!")
                                st.rerun()
                        with col3:
                            if st.session_state.conteudos_aprovados.get(i, False):
                                if st.button(f"🚀 Publicar em {canal_nome}", key=f"publicar_{i}", type="primary", use_container_width=True):
                                    st.success(f"Publicado em {canal_nome}! (Simulado - integração real pendente)")
                            else:
                                st.info("Aprove o conteúdo primeiro para publicar.")

                st.markdown('</div>', unsafe_allow_html=True)

            # Agente Publicador
            if "publicacoes" in result:
                st.markdown("""
                <div class="agent-result-card agent-publicador">
                    <div class="agent-header">
                        <div class="agent-icon">📤</div>
                        <div>
                            <div class="agent-title">Publicador</div>
                            <div class="agent-subtitle">Publicação automatizada em múltiplas plataformas</div>
                        </div>
                    </div>
                    <div class="content-block">
                """, unsafe_allow_html=True)

                for canal, status in result["publicacoes"].items():
                    if "simulado" in status.lower():
                        st.info(f"📱 {canal}: {status}")
                    else:
                        st.success(f"📱 {canal}: {status}")

                st.markdown('</div></div>', unsafe_allow_html=True)

            # Agente Otimizador
            if "otimizacao" in result:
                st.markdown("""
                <div class="agent-result-card agent-otimizador">
                    <div class="agent-header">
                        <div class="agent-icon">📊</div>
                        <div>
                            <div class="agent-title">Otimizador</div>
                            <div class="agent-subtitle">Análise e otimização de performance</div>
                        </div>
                    </div>
                    <div class="content-block">
                """, unsafe_allow_html=True)
                st.write(result["otimizacao"])
                st.markdown('</div></div>', unsafe_allow_html=True)

            # Agente Maestro
            if "orquestracao" in result:
                st.markdown("""
                <div class="agent-result-card agent-maestro">
                    <div class="agent-header">
                        <div class="agent-icon">🎼</div>
                        <div>
                            <div class="agent-title">Maestro</div>
                            <div class="agent-subtitle">Coordenação e supervisão geral</div>
                        </div>
                    </div>
                    <div class="content-block">
                """, unsafe_allow_html=True)
                st.write(result["orquestracao"])
                st.markdown('</div></div>', unsafe_allow_html=True)

            # Imagens Geradas (se houver)
            if "imagens" in result and result["imagens"]:
                st.markdown("""
                <div class="agent-result-card agent-criador">
                    <div class="agent-header">
                        <div class="agent-icon">🖼️</div>
                        <div>
                            <div class="agent-title">Imagens Geradas</div>
                            <div class="agent-subtitle">Conteúdo visual criado pela IA</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                for i, img_url in enumerate(result["imagens"], 1):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if img_url.startswith("http"):
                            st.image(img_url, caption=f"Imagem {i}", use_column_width=True)
                        else:
                            st.info(f"📝 Descrição da imagem {i}")
                    with col2:
                        st.write(f"**Imagem {i}:** {img_url}")

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

    with tab5:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        st.markdown("### 📅 Agendamento de Posts")

        # Análise de horários ideais
        st.markdown("#### 🕐 Horários Mais Acessados no Nicho")

        # Simulação de dados de horários (futuramente integrar com analytics reais)
        horarios_ideais = {
            "Instagram": ["08:00-10:00", "18:00-20:00", "12:00-14:00"],
            "Facebook": ["13:00-15:00", "19:00-21:00", "09:00-11:00"],
            "Twitter/X": ["12:00-14:00", "18:00-20:00", "08:00-10:00"],
            "LinkedIn": ["07:00-09:00", "12:00-14:00", "17:00-19:00"],
            "TikTok": ["18:00-22:00", "12:00-14:00", "08:00-10:00"],
            "YouTube": ["14:00-16:00", "19:00-21:00", "11:00-13:00"]
        }

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Horários Sugeridos por Plataforma:**")
            for plataforma, horarios in horarios_ideais.items():
                st.markdown(f"**{plataforma}:** {', '.join(horarios)}")

        with col2:
            st.markdown("**📊 Baseado em Análise de Dados**")
            st.info("💡 Estes horários são sugeridos com base em padrões de engajamento no seu nicho. Use analytics reais para otimizar.")

        st.markdown("---")

        # Agendamento manual
        st.markdown("#### ⏰ Agendar Post")

        if "conteudos_aprovados" in st.session_state and any(st.session_state.conteudos_aprovados.values()):
            # Mostrar conteúdos aprovados para agendamento
            conteudos_aprovados = [i for i, aprovado in st.session_state.conteudos_aprovados.items() if aprovado]

            if conteudos_aprovados:
                selected_conteudo = st.selectbox("Selecionar conteúdo aprovado:", options=conteudos_aprovados, format_func=lambda x: f"Conteúdo {x}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    plataforma = st.selectbox("Plataforma:", ["Instagram", "Facebook", "Twitter/X", "LinkedIn", "TikTok", "YouTube"])
                with col2:
                    data_agendamento = st.date_input("Data:", min_value=datetime.now().date())
                with col3:
                    hora_agendamento = st.time_input("Hora:")

                if st.button("📅 Agendar Post", type="primary"):
                    # Simulação de agendamento (futuramente integrar com scheduler real)
                    st.success(f"✅ Post agendado para {plataforma} em {data_agendamento} às {hora_agendamento}")
                    # TODO: Salvar no banco de dados ou scheduler
            else:
                st.info("📝 Aprove conteúdos na aba de Resultados primeiro.")
        else:
            st.info("📝 Execute e aprove conteúdos primeiro para agendar posts.")

        st.markdown('</div>', unsafe_allow_html=True)