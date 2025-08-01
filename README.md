Tech Challenge - Big Data B3

Este projeto demonstra uma arquitetura de pipeline batch para coleta e processamento de dados do pregão da B3 utilizando AWS. Os componentes principais são:

- **Scraper**: coleta os dados do site da B3.
- **S3**: armazenamento dos arquivos brutos em formato parquet particionado por data.
- **Lambda**: acionada quando novos arquivos chegam no bucket e inicia o Job do Glue.
- **Glue Job**: realiza transformações, salva no bucket *refined* e cataloga os dados.
- **Athena**: consulta dos dados refinados.

## Desenho da Arquitetura

```
+----------+          +-------+          +---------+       +-------+
| Scraper  +--parquet-> S3    +--event--> Lambda  +--> Glue Job |
+----------+          +-------+          +---------+       +-------+
                                                               |
                                                               v
                                                            Athena
```

1. O *scraper* faz download da tabela de cotações do dia e envia para o bucket S3 em `raw/date=YYYY-MM-DD/`.
2. O S3 aciona a Lambda que dispara o Glue Job.
3. O Glue Job lê os dados brutos, executa as transformações (agrupamentos, renomeia colunas e calcula diferença de datas) e grava em `refined/` particionado por `data_ref` e `acao`.
4. O Glue cria a tabela no Glue Catalog, permitindo consultas pelo Athena.

O link de origem dos dados é obrigatório e está disponível [aqui](https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br).

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.7+
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

### 2. Execução Local

**Executar apenas o scraper:**
```bash
python -m src.scraper
```

**Demonstração completa:**
```bash
python demo.py
```

### 3. Exemplo de Uso Programático

```python
from src.scraper import B3Scraper
from src.uploader import S3Uploader
import pandas as pd

# Coletar dados
scraper = B3Scraper()
df = scraper.fetch()

# Para upload S3 (requer credenciais AWS)
uploader = S3Uploader(bucket="seu-bucket", prefix="raw")
key = uploader.upload_parquet(df, pd.Timestamp.now())
```

## 📊 Funcionalidades

### Scraper (src/scraper.py)
- Coleta dados do Ibovespa via web scraping
- Fallback para dados de exemplo quando o site não está disponível
- Headers apropriados para simular navegador
- Tratamento robusto de erros

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
│   ├── scraper.py      # Web scraping da B3
│   ├── uploader.py     # Upload para S3
│   ├── lambda_handler.py # Função Lambda
│   └── etl_job.py      # Job do Glue
├── demo.py             # Demonstração completa
├── requirements.txt    # Dependências
└── README.md          # Este arquivo
```

## 📝 Dependências

- boto3: Cliente AWS
- pandas: Manipulação de dados
- requests: Requisições HTTP
- pyarrow: Formato Parquet
- lxml: Parser HTML
- html5lib: Parser HTML alternativo
- beautifulsoup4: Parser HTML robusto

## 🔧 Solução de Problemas

**Erro "No module named 'lxml'":**
```bash
pip install lxml html5lib beautifulsoup4
```

**Erro "No tables found":**
O projeto inclui dados de exemplo quando o scraping falha.

**Erro de credenciais AWS:**
Configure com `aws configure` ou variáveis de ambiente.

## 📈 Exemplo de Saída

```
📊 Dados coletados: 5 ações
📅 Data de referência: 2025-08-01

 Nome  Último  Variação (%)   Volume   
PETR4   28.50          2.15  45000000 
VALE3   62.30         -1.30  78000000 
ITUB4   25.10          0.85  32000000 
BBDC4   13.45         -0.95  25000000 
MGLU3    8.90          3.20  18000000 

Volume total: 198,000,000
```

---

🎯 **Teste rápido:** `python demo.py`