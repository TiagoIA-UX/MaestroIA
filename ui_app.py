import streamlit as st
import requests
from maestroia.graphs.marketing_graph import build_marketing_graph

st.title("MaestroIA")

# Simulação de login (integrar com API futuramente)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # Simulação
        if email and password:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Credenciais inválidas")
else:
    st.success("Logado como " + st.session_state.get("email", "Usuário"))

    graph = build_marketing_graph()

    objetivo = st.text_input("Objetivo da Campanha")
    publico = st.text_input("Público-Alvo")
    canais = st.multiselect("Canais", ["Instagram", "Google Ads", "Facebook"])
    orcamento = st.number_input("Orçamento", min_value=0.0)

    if st.button("Executar Campanha"):
        state = {
            "objetivo": objetivo,
            "publico_alvo": publico,
            "canais": canais,
            "orcamento": orcamento
        }
        result = graph.invoke(state)
        st.json(result)

        # Mostrar imagens se geradas
        if "imagens" in result:
            for img_url in result["imagens"]:
                if img_url.startswith("http"):
                    st.image(img_url, caption="Imagem gerada")
                else:
                    st.write(img_url)