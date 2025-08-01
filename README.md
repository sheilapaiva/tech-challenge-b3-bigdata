Tech Challenge - Big Data B3 🚀

Este projeto demonstra uma arquitetura de pipeline batch para coleta e processamento de dados do pregão da B3 utilizando **SCRAPING REAL** com Selenium e AWS. Os componentes principais são:

- **Scraper**: coleta **DADOS REAIS** do site da B3 usando Selenium WebDriver.
- **S3**: armazenamento dos arquivos brutos em formato parquet particionado por data.
- **Lambda**: acionada quando novos arquivos chegam no bucket e inicia o Job do Glue.
- **Glue Job**: realiza transformações, salva no bucket *refined* e cataloga os dados.
- **Athena**: consulta dos dados refinados.

## 🎯 **SCRAPING REAL IMPLEMENTADO!**

✅ **Dados reais da B3** - Não são mais dados mockados!  
✅ **Selenium WebDriver** - Renderiza JavaScript para acessar dados dinâmicos  
✅ **22 ações do Ibovespa** - Códigos reais como PETR4, VALE3, ITUB4, etc.  
✅ **Composição oficial** - Qtde. Teórica e participação percentual  

## Desenho da Arquitetura

```
+----------+          +-------+          +---------+       +-------+
| Scraper  +--parquet-> S3    +--event--> Lambda  +--> Glue Job |
| REAL     |          +-------+          +---------+       +-------+
| Selenium |                                                   |
+----------+                                                   v
                                                            Athena
```

1. O *scraper* usa **Selenium** para renderizar JavaScript e extrair dados reais da composição do Ibovespa.
2. Os dados são salvos no bucket S3 em `raw/date=YYYY-MM-DD/`.
3. O S3 aciona a Lambda que dispara o Glue Job.
4. O Glue Job lê os dados brutos, executa as transformações e grava em `refined/`.
5. O Glue cria a tabela no Glue Catalog, permitindo consultas pelo Athena.

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

### 2. Execução com Dados REAIS

**Scraping real da B3:**
```bash
python -m src.scraper
```

**Demonstração completa com dados reais:**
```bash
python demo.py
```

### 3. Exemplo de Uso Programático

```python
from src.scraper import B3Scraper
from src.uploader import S3Uploader
import pandas as pd

# Coletar dados REAIS da B3
scraper = B3Scraper(headless=True)  # headless=False para ver o navegador
df = scraper.fetch_with_fallback()

print(f"Coletadas {len(df)} ações reais!")
print(df.head())

# Para upload S3 (requer credenciais AWS)
uploader = S3Uploader(bucket="seu-bucket", prefix="raw")
key = uploader.upload_parquet(df, pd.Timestamp.now())
```

## 📊 Dados Coletados (REAIS)

O scraper agora coleta dados reais da composição do Ibovespa:

- **Código**: Código da ação (ex: PETR4, VALE3)
- **Ação**: Nome da empresa
- **Tipo**: Tipo de ação (ON, PN, etc.)
- **Qtde. Teórica**: Quantidade teórica na carteira
- **Part. (%)**: Participação percentual no índice
- **data_ref**: Data de referência dos dados

## 📈 Exemplo de Saída Real

```
Código         Ação     Tipo Qtde. Teórica  Part. (%)
ALOS3        ALLOS  ON ED NM   476.976.044      495.0
ABEV3    AMBEV S/A       ON 4.394.835.131     2666.0
ASAI3        ASSAI    ON NM 1.345.897.506      617.0
AURE3        AUREN    ON NM   323.738.747      146.0
AZZA3   AZZAS 2154    ON NM   136.643.320      237.0
```

## 🛠️ Funcionalidades

### Scraper Real (src/scraper.py)
- **Selenium WebDriver** para renderizar JavaScript
- **Chrome headless** para scraping automatizado
- **Dados reais** da composição do Ibovespa
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
│   ├── scraper.py      # Scraping REAL com Selenium
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

## 🎯 **Resultados Comprovados**

✅ **22 ações reais** coletadas do Ibovespa  
✅ **Dados estruturados** em CSV e Excel  
✅ **Pipeline completo** pronto para deploy  
✅ **Scraping robusto** com Selenium  

---

🚀 **Teste agora:** `python demo.py` - **DADOS REAIS DA B3!**