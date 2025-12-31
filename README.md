
<div align="center">
   <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Versão" />
   <img src="https://img.shields.io/badge/python-3.14+-green.svg" alt="Python" />
   <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="Licença" />
</div>

# 🎯 MaestroIA

<div align="center">
   <img src="https://user-images.githubusercontent.com/your-banner-image.png" width="60%" alt="MaestroIA Banner" />
   <h2>Orquestração Inteligente de Agentes de Marketing Digital</h2>
   <p>Automatize campanhas, gere relatórios em PDF e receba pagamentos via Mercado Pago em uma interface elegante estilo ebook.</p>
</div>


## 📖 Sobre o Projeto

O **MaestroIA** é uma plataforma visual e interativa para orquestração de agentes de IA em marketing digital. Com interface estilo ebook, você cria campanhas, gera conteúdos, acompanha resultados e baixa relatórios em PDF — tudo em poucos cliques, sem precisar de conhecimento técnico.

**Destaques:**
- Interface Streamlit elegante, responsiva e moderna
- Relatórios em PDF com visual profissional
- Integração Mercado Pago para planos pagos
- Experiência de uso inspirada em eBooks e dashboards premium


## ✨ Funcionalidades Principais

### 🤖 Agentes Inteligentes
- **Pesquisador**: Analisa tendências e oportunidades
- **Estrategista**: Cria estratégias de marketing
- **Criador de Conteúdo**: Gera posts e anúncios otimizados
- **Publicador**: Simula publicações em múltiplas redes
- **Otimizador**: Sugere melhorias com base em dados
- **Maestro**: Orquestra e supervisiona todo o fluxo

### 💎 Experiência Visual
- Design com gradientes, cards e feedback animado
- Relatórios em PDF estilo ebook, prontos para download
- Interface responsiva, intuitiva e acessível

### 🔗 Integrações
- **OpenAI** (GPT-4o-mini, DALL-E)
- **Google Trends**
- **Mercado Pago** (pagamentos de planos)
- **Redes Sociais** (simulação e estrutura para integrações reais)

### 🔐 Segurança
- Cadastro seguro, validação de email e senha forte
- Dados criptografados e controle de acesso


## 🚀 Instalação e Primeiros Passos

### Pré-requisitos
- Python 3.14+
- Git
- Conta OpenAI (para IA)

### Instalação Rápida
```bash
# Clone o repositório
git clone https://github.com/TiagoIA-UX/MaestroIA.git
cd MaestroIA

# Crie o ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r requirements.txt
```

### Configuração
1. Copie `.env.example` para `.env` e preencha suas chaves:
   - `OPENAI_API_KEY=sk-...`
   - `MERCADOPAGO_ACCESS_TOKEN=...`
   - Outras chaves conforme integrações desejadas

2. Execute a interface web:
```bash
streamlit run ui_app.py
```

3. Acesse: [http://localhost:8501](http://localhost:8501)

### Primeiro Uso
1. Cadastre-se na aba **📝 Cadastrar-se**
2. Crie sua campanha em **📝 Criar Campanha**
3. Veja resultados e baixe o PDF em **📊 Resultados**
4. Faça upgrade de plano em **💎 Planos & Pagamento**


## 🗂️ Estrutura do Projeto

```
maestroia/
├─ agents/          # Agentes inteligentes
├─ config/          # Configurações
├─ core/            # Governança e estado
├─ graphs/          # Orquestração (LangGraph)
├─ memory/          # Memória vetorial
├─ services/        # Lógica de campanhas
├─ tools/           # Ferramentas auxiliares
├─ ui/              # Componentes Streamlit
├─ ui_app.py        # App principal (Streamlit)
├─ users.json       # Usuários
├─ requirements.txt
├─ .env.example
└─ README.md
```


## 🛠️ Tecnologias

- **Python 3.14+**
- **Streamlit** (UI elegante)
- **OpenAI API** (GPT-4o-mini, DALL-E)
- **Mercado Pago** (pagamentos)
- **LangGraph** (orquestração de agentes)
- **FAISS** (memória vetorial)
- **ReportLab** (PDF estilo ebook)
- **APIs de Redes Sociais** (simulação e estrutura)


## 🔑 Configuração de APIs (Opcional)

Para integrações reais, preencha as chaves no `.env`:

```env
OPENAI_API_KEY=sk-...
MERCADOPAGO_ACCESS_TOKEN=...
# Outras chaves: Twitter, Meta, etc.
```

Sem chaves, o sistema funciona em modo simulado.


## 🎬 Exemplo Visual e Saídas

<div align="center">
  <img src="https://user-images.githubusercontent.com/your-ui-screenshot.png" width="70%" alt="UI MaestroIA" />
</div>

Ao criar uma campanha, você recebe:
- **Análise de mercado** (texto detalhado)
- **Estratégia** (plano de ação)
- **Conteúdos** (posts e anúncios)
- **Publicações** (simulação)
- **Otimização** (sugestões de melhoria)
- **Imagens geradas** (DALL-E)
- **Relatório PDF** (ebook visual)

<details>
<summary>Exemplo de PDF gerado</summary>

![Exemplo PDF](https://user-images.githubusercontent.com/your-pdf-sample.png)

</details>


## 💳 Planos e Pagamento

Escolha seu plano e pague com Mercado Pago direto na interface:

- **Gratuito**: 2 campanhas/mês, 2 canais, 7 dias de teste
- **Starter**: 10 campanhas/mês, 5 canais, 14 dias de teste, R$ 49,90/mês
- **Professional**: 50 campanhas/mês, 10 canais, 30 dias de teste, R$ 149,90/mês
- **Enterprise**: Ilimitado, 30 dias de teste, R$ 499,90/mês

O upgrade é feito via link Mercado Pago. Após o pagamento, o plano é ativado.


## 🚦 Status e Roadmap

- ✅ MVP Visual e funcional (Streamlit)
- 🔄 Próximos: Integrações reais, analytics, agendamento real
- 🚀 Futuro: Plugins, painel admin, IA avançada


## 🤝 Contribuição

1. Fork este repositório
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'feat: nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request


## 📄 Licença

MIT License


## 👤 Autor

**Tiago Rocha**

Desenvolvido com foco em inovação, experiência visual e escalabilidade para o futuro do marketing digital.


---

## 📚 Casos de Uso

- Orquestração de agentes de marketing digital
- Automação de processos com IA
- Plataformas educacionais e de conteúdo
- Base para SaaS com múltiplos agentes

---

## 📜 Atribuições

Para citações e licenças de terceiros, veja [ATTRIBUTIONS.md](ATTRIBUTIONS.md).

---
