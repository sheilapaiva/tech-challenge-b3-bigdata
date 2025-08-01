Tech Challenge - Big Data B3 🚀

Este projeto demonstra uma arquitetura de pipeline batch para coleta e processamento de dados do pregão da B3 utilizando **SCRAPING** com Selenium e AWS. Os componentes principais são:

- **Scraper**: coleta **DADOS** do site da B3 usando Selenium WebDriver.
- **S3**: armazenamento dos arquivos brutos em formato parquet particionado por data.
- **Lambda**: acionada quando novos arquivos chegam no bucket e inicia o Job do Glue.
- **Glue Job**: realiza transformações, salva no bucket *refined* e cataloga os dados.
- **Athena**: consulta dos dados refinados.

## 🎯 **SCRAPING IMPLEMENTADO!**

✅ **Dados da B3** - Coleta os dados.
✅ **Selenium WebDriver** - Renderiza JavaScript para acessar dados dinâmicos  
✅ **22 ações do Ibovespa** - Códigos como PETR4, VALE3, ITUB4, etc.  
✅ **Composição oficial** - Quantidade teórica e participação percentual  

## Diagrama da Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│   🌐 B3 Site    │    │  📊 Scraper     │    │   ☁️ AWS Cloud   │
│   (JavaScript)  │◄───┤  Selenium       │    │                  │
└─────────────────┘    │  Chrome Driver  │    │                  │
                       └─────────┬───────┘    │                  │
                                 │            │                  │
                       ┌─────────▼───────┐    │                  │
                       │ 📄 Dados Brutos │    │                  │
                       │ Ações B3        │    │                  │
                       └─────────┬───────┘    │                  │
                                 │            │                  │
                                 ▼            │                  │
    ┌────────────────────────────────────────────────────────────┼──────────────┐
    │                                                            │              │
    │  ┌─────────────────┐   S3 Event     ┌──────────────────┐   │              │
    │  │   🪣 S3 Raw     │─────────────▶  │  ⚡ Lambda        │   │              │
    │  │                 │  ObjectCreated │  Trigger         │   │              │
    │  │ raw/date=       │                │  b3-pipeline     │   │              │
    │  │ 2025-08-01/     │                └─────────┬────────┘   │              │
    │  │ data.parquet    │                          │            │              │
    │  └─────────────────┘                          ▼            │              │
    │                                    ┌────────────────────┐  │              │
    │                                    │  🛠️ Glue Job       │  │              │
    │                                    │  (Visual Mode)     │  │              │
    │                                    │                    │  │              │
    │                                    │ A: Aggregate       │  │              │
    │                                    │ B: Rename Fields   │  │              │
    │                                    │ C: Date Calcs      │  │              │
    │                                    └─────────┬──────────┘  │              │
    │                                              │             │              │
    │  ┌─────────────────┐                         ▼             │              │
    │  │  🪣 S3 Refined  │              ┌────────────────────┐   │              │
    │  │                 │◄─────────────┤  📋 Glue Catalog   │   │              │
    │  │ refined/        │              │  b3_database       │   │              │
    │  │ data_ref=*/     │              │  b3_refined_data   │   │              │
    │  │ codigo_acao=*/  │              └─────────┬──────────┘   │              │
    │  │ data.parquet    │                        │              │              │
    │  └─────────────────┘                        ▼              │              │
    │                                   ┌─────────────────────┐  │              │
    │                                   │  🔍 Amazon Athena   │  │              │
    │                                   │  SQL Queries        │  │              │
    │                                   │  Analytics          │  │              │
    │                                   └─────────────────────┘  │              │
    └────────────────────────────────────────────────────────────┼──────────────┘
                                                                 │
                                                   ┌─────────────▼──────────────┐
                                                   │  📊 Business Intelligence  │
                                                   │  Dashboards & Reports      │
                                                   └────────────────────────────┘
```

### 🔄 Fluxo de Dados Detalhado:

1. **🌐 Scraping**: Selenium acessa o site da B3, renderiza JavaScript e extrai dados reais da composição do Ibovespa
2. **📤 Upload**: Dados são convertidos para Parquet e salvos no S3 em `raw/date=YYYY-MM-DD/data.parquet`
3. **⚡ Trigger**: S3 Event Notification aciona automaticamente a função Lambda
4. **🛠️ ETL Visual**: Lambda inicia o Glue Job visual que executa as transformações:
   - **A**: Agrupamento por código de ação + sumarização (soma, contagem)
   - **B**: Renomeação de colunas (`Código`→`codigo_acao`, etc.)
   - **C**: Cálculos com data (diferenças, extrações, formatações)
5. **💾 Refined**: Dados transformados são salvos em `refined/` particionados por data e código da ação
6. **📋 Catalogação**: Glue Job automaticamente registra tabela no Glue Catalog
7. **🔍 Consultas**: Dados ficam disponíveis para consulta no Athena e análises de BI

### 📊 Dados Processados:
- **Entrada**: 22 ações do Ibovespa (PETR4, VALE3, ITUB4, etc.)
- **Saída**: Dados agregados, renomeados e enriquecidos com cálculos temporais
- **Particionamento**: Por data de referência e código da ação
- **Formato**: Parquet otimizado para consultas analíticas

O link de origem dos dados é obrigatório e está disponível [aqui](https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br).

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.7+
- Google Chrome (para Selenium)
- pip

### 1. Instalação das Dependências

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 2. Execução com Dados

**Scraping da B3:**
```bash
python -m src.scraper
```

**Demonstração completa com dados:**
```bash
python demo.py
```

### 3. Exemplo de Uso Programático

```python
from src.scraper import B3Scraper
from src.uploader import S3Uploader
import pandas as pd

# Coletar dados da B3
scraper = B3Scraper(headless=True)  # headless=False para ver o navegador
df = scraper.fetch_with_fallback()

print(f"Coletadas {len(df)} ações!")
print(df.head())

# Para upload S3 (requer credenciais AWS)
uploader = S3Uploader(bucket="seu-bucket", prefix="raw")
key = uploader.upload_parquet(df, pd.Timestamp.now())
```

## 📊 Dados Coletados

O scraper agora coleta dados da composição do Ibovespa:

- **Código**: Código da ação (ex: PETR4, VALE3)
- **Ação**: Nome da empresa
- **Tipo**: Tipo de ação (ON, PN, etc.)
- **Qtde. Teórica**: Quantidade teórica na carteira
- **Part. (%)**: Participação percentual no índice
- **data_ref**: Data de referência dos dados

## 📈 Exemplo de Saída

```
Código         Ação     Tipo Qtde. Teórica  Part. (%)
ALOS3        ALLOS  ON ED NM   476.976.044      495.0
ABEV3    AMBEV S/A       ON 4.394.835.131     2666.0
ASAI3        ASSAI    ON NM 1.345.897.506      617.0
AURE3        AUREN    ON NM   323.738.747      146.0
AZZA3   AZZAS 2154    ON NM   136.643.320      237.0
```

## 🛠️ Funcionalidades

### Scraper (src/scraper.py)
- **Selenium WebDriver** para renderizar JavaScript
- **Chrome headless** para scraping automatizado
- **Dados** da composição do Ibovespa
- **Fallback robusto** em caso de falhas
- **Headers apropriados** para simular navegador

### Uploader (src/uploader.py)
- Upload de DataFrame para S3 em formato Parquet
- Particionamento automático por data
- Compressão eficiente

### Pipeline ETL (src/etl_job.py)
- Job do AWS Glue para transformações
- Agregações por ticker
- Renomeação de colunas
- Cálculo de diferenças de data

## ☁️ Deploy na AWS

Para usar o pipeline completo na AWS:

1. **Configurar credenciais AWS:**
   ```bash
   aws configure
   ```

2. **Criar recursos AWS:**
   - Bucket S3 para dados raw e refined
   - Função Lambda
   - Glue Job
   - Permissões IAM necessárias

3. **Deploy dos componentes:**
   - Upload do código Lambda
   - Configuração do Glue Job
   - Setup do Glue Catalog

## 🛠️ Estrutura do Projeto

```
tech-challenge-b3-bigdata/
├── src/
│   ├── scraper.py      # Scraping com Selenium
│   ├── uploader.py     # Upload para S3
│   ├── lambda_handler.py # Função Lambda
│   └── etl_job.py      # Job do Glue
├── demo.py             # Demonstração completa
├── requirements.txt    # Dependências
└── README.md          # Este arquivo
```

## 📝 Dependências

- **boto3**: Cliente AWS
- **pandas**: Manipulação de dados
- **requests**: Requisições HTTP (fallback)
- **pyarrow**: Formato Parquet
- **lxml**: Parser HTML
- **html5lib**: Parser HTML alternativo
- **beautifulsoup4**: Parser HTML robusto
- **selenium**: WebDriver para scraping JavaScript
- **webdriver-manager**: Gerenciamento automático do ChromeDriver
- **openpyxl**: Export para Excel

## 🔧 Solução de Problemas

**Erro "No module named 'selenium'":**
```bash
pip install selenium webdriver-manager
```

**Erro do Chrome/ChromeDriver:**
- O webdriver-manager baixa automaticamente o ChromeDriver correto
- Certifique-se de ter o Google Chrome instalado

**Erro "No tables found":**
- O projeto inclui fallback automático para casos de falha
- Verifique a conexão com a internet

**Erro de credenciais AWS:**
Configure com `aws configure` ou variáveis de ambiente.

## 🎯 **Resultados**

✅ **22 ações** coletadas do Ibovespa  
✅ **Dados estruturados** em CSV e Excel  
✅ **Pipeline completo** pronto para deploy  
✅ **Scraping** com Selenium  

---

🚀 **Teste:** `python demo.py` - **DADOS DA B3!**