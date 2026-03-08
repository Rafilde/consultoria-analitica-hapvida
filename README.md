# 📊 Consultoria Analítica: ReclameAqui - HAPVIDA

> **Status do Projeto:** Em Desenvolvimento (Acompanhamento 1)

---

## 👥 Equipe
* **Integrante 1**: Rafaeel Antônio da Silva Neto - 2212378
* **Integrante 2**: Emanuel Sales Marinho Rocha - 2413961
* **Integrante 3**: [Nome Completo] - [Matrícula]
* **Integrante 4**: [Nome Completo] - [Matrícula]

---

## 🎯 Objetivos do Projeto
Este projeto visa analisar o fluxo de reclamações da Hapvida Saúde na plataforma ReclameAqui, transformando relatos qualitativos em indicadores estratégicos. Através da análise de dados, buscamos identificar falhas operacionais na rede de atendimento, gargalos regionais de infraestrutura e a eficácia da equipe de Customer Experience (CX) na resolução definitiva de conflitos.

* **Objetivo 1:** [Ex: Analisar a sazonalidade das reclamações]
* **Objetivo 2:** [Ex: Mapear a eficiência de resolução por estado]
* **Objetivo 3:** [Ex: Correlacionar o tamanho do texto do cliente com o sucesso da solução]

---

## 📂 Organização do Repositório (Arquitetura)

Este projeto utiliza uma estrutura modular para garantir que a análise seja escalável e organizada. Abaixo, a função de cada diretório:

### 1. `data/` (Gestão de Dados)
* **`RECLAMEAQUI_HAPVIDA/`**: Contém o dataset original extraído do ReclameAqui. **Nunca deve ser alterado.**

### 2. `notebooks/` (Relatórios Narrativos)

Nesta pasta, o foco é o **Storytelling**. Cada decisão técnica é explicada em texto antes do código, servindo como o relatório oficial da consultoria.

* **`00_inspecao_inicial.ipynb`**: O primeiro contato com os dados brutos da Hapvida. Este notebook documenta a análise de integridade, identificação de valores nulos, redundâncias e inconsistências de tipagem. Serve para validar "o que está errado" antes de qualquer ação.
* **`01_tratamento_e_justificativa.ipynb`**: Corresponde ao **Acompanhamento 1**. Aqui, os insights de negócio são conectados às ações técnicas. Cada limpeza é precedida por uma justificativa estratégica, demonstrando como o dado limpo ajudará a responder aos objetivos da consultoria.
* **`02_analise_exploratoria.ipynb`**: Focado no **Acompanhamento 2**, contém os cruzamentos estatísticos, validação de hipóteses e a geração dos gráficos preliminares que servirão de base para o Dashboard final.

### 3. `src/` (Código-Fonte / Backend)
Contém a lógica reutilizável em arquivos `.py`. Isso evita poluir os notebooks com códigos repetitivos.
* **entrada_saida**: Funções para leitura e escrita das planilhas.
* **Limpeza**: Funções de automação de limpeza de strings, datas e tratamento de nulos.
* **Métricas**: Cálculos dos KPIs (Key Performance Indicators) definidos pela equipe.
* **NLP**: Processamento de texto para a WordCloud e análise de caracteres.

### 4. `dashboard/` (Interface Final)
* **`app.py`**: Arquivo principal do Streamlit/Dash.
* **Interatividade**: Implementação de filtros globais (Estado, Status, Tamanho de Texto) e visualizações dinâmicas.

---

## 🛠️ Tecnologias Utilizadas
* **Linguagem**: Python
* **Análise de Dados**: Pandas, Numpy
* **Visualização**: Plotly, Seaborn, Matplotlib
* **NLP**: Spacy 
* **Dashboard**: Streamlit / Plotly Dash
* **IDE**: VS Code

---

## Como Executar o Projeto

### Clone o repositório
```bash
git clone <url-do-repositorio>
cd CONSULTORIA-ANALITICA-HAPVIDA
```

### Executando os Notebooks

Este projeto utiliza notebooks Jupyter que devem ser executados localmente (não no Google Colab), pois dependem da estrutura de pastas do projeto (`src/`, `data/`, etc.).

Instale o kernel do Jupyter:
```bash
pip install ipykernel notebook
```

Abra o projeto no VS Code (pela pasta raiz) e execute os arquivos dentro de:
```
notebooks/
```

> Certifique-se de selecionar o Python local como Kernel no canto superior direito do notebook.


### Crie um ambiente virtual (recomendado)
```bash
python -m venv venv
```

Ative o ambiente:

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

### Instale as dependências
```bash
pip install -r requirements.txt
```

### Configuração do Kernel no VS Code (Importante)
Após instalar as dependências no venv, você precisa garantir que o Jupyter Notebook está usando o ambiente correto:

- Abra qualquer arquivo .ipynb no VS Code.

- No canto superior direito, clique onde aparece a versão do Python (ex: Python 3.13.x).

- Selecione a opção "Python Environments...".

- Escolha o interpretador que está dentro da pasta do projeto (geralmente marcado como 'venv': venv).

- Se o VS Code pedir para instalar o ipykernel, clique em Install.

Dica: Se você não fizer isso, o código não encontrará as bibliotecas instaladas (como o pandas ou nltk), mesmo que o terminal diga que está tudo certo.

### Rodando o Dashboard Interativo
```bash
streamlit run dashboard/app.py
```

O Streamlit abrirá automaticamente no navegador.

---