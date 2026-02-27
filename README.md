# 📊 Consultoria Analítica: ReclameAqui - HAPVIDA

> **Status do Projeto:** Em Desenvolvimento (Acompanhamento 1)

---

## 👥 Equipe
* **Integrante 1**: Rafaeel Antônio da Silva Neto (2212378) - [Função: Ex: Data Engineer / SRC]
* **Integrante 2**: [Nome Completo] - [Função: Ex: Data Analyst / Notebooks]
* **Integrante 3**: [Nome Completo] - [Função: Ex: UI/UX Designer / Dashboard]
* **Integrante 4**: [Nome Completo] - [Função: Ex: Documentation / Storytelling]

---

## 🎯 Objetivos do Projeto
[Descreva aqui em um parágrafo o que a equipe pretende descobrir. Exemplo: Identificar gargalos logísticos e falhas de comunicação no pós-venda da empresa X.]

* **Objetivo 1:** [Ex: Analisar a sazonalidade das reclamações]
* **Objetivo 2:** [Ex: Mapear a eficiência de resolução por estado]
* **Objetivo 3:** [Ex: Correlacionar o tamanho do texto do cliente com o sucesso da solução]

---

## 📂 Organização do Repositório (Arquitetura)

Este projeto utiliza uma estrutura modular para garantir que a análise seja escalável e organizada. Abaixo, a função de cada diretório:

### 1. `data/` (Gestão de Dados)
* **`RECLAMEAQUI_HAPVIDA/`**: Contém o dataset original extraído do ReclameAqui. **Nunca deve ser alterado.**

### 2. `notebooks/` (Relatórios Narrativos)
Nesta pasta, o foco é o **Storytelling**. Cada decisão técnica é explicada em texto antes do código.
* **`01_limpeza.ipynb`**: Focado no tratamento inicial, conversão de tipos e higienização. Contém as justificativas de por que os dados foram filtrados.
* **`02_analise_exploratoria.ipynb`**: Contém os cruzamentos estatísticos, testes de hipóteses e gráficos preliminares.

### 3. `src/` (Código-Fonte / Backend)
Contém a lógica reutilizável em arquivos `.py`. Isso evita poluir os notebooks com códigos repetitivos.
* **Limpeza**: Funções de automação de limpeza de strings, datas e tratamento de nulos.
* **Métricas**: Cálculos dos KPIs (Key Performance Indicators) definidos pela equipe.
* **NLP**: Processamento de texto para a WordCloud e análise de caracteres.

### 4. `dashboard/` (Interface Final)
* **`app.py`**: Arquivo principal do Streamlit/Dash.
* **Interatividade**: Implementação de filtros globais (Estado, Status, Tamanho de Texto) e visualizações dinâmicas.

---

## 🛠️ Tecnologias Utilizadas
* **Linguagem**: Python 3.x
* **Análise de Dados**: Pandas, Numpy
* **Visualização**: Plotly, Seaborn, Matplotlib
* **NLP**: NLTK ou Spacy (Stopwords)
* **Dashboard**: Streamlit / Plotly Dash
* **IDE**: VS Code

---

## 🚀 Como Executar o Projeto
1. Clone este repositório.
2. Crie um ambiente virtual e instale as dependências:
   ```bash
   pip install -r requirements.txt
3. Para visualizar o tratamento de dados, abra os arquivos na pasta `notebooks/`.
4. Para rodar o Dashboard interativo:
   ```bash
   streamlit run dashboard/app.py