# 🚀 Guia Completo de Deploy - Tech Challenge B3

## 📋 Visão Geral
Este guia detalha como fazer o deploy completo do pipeline de dados da B3, cumprindo todos os requisitos obrigatórios do Tech Challenge.

## ✅ Pré-requisitos
- AWS CLI configurado (`aws configure`)
- Python 3.7+ instalado
- Google Chrome (para Selenium)
- Bucket S3 com nome único escolhido

## 🎯 Arquitetura Final
```
┌─────────────┐   ┌─────────┐   ┌─────────┐   ┌─────────────┐   ┌─────────┐
│   Scraper   │──▶│   S3    │──▶│ Lambda  │──▶│ Glue Visual │──▶│ Athena  │
│  (Selenium) │   │  Raw    │   │Trigger  │   │    Job      │   │Queries  │
└─────────────┘   └─────────┘   └─────────┘   └─────────────┘   └─────────┘
                       │                             │
                       ▼                             ▼
                  ┌─────────┐                 ┌─────────────┐
                  │   S3    │                 │    Glue     │
                  │Refined  │                 │  Catalog    │
                  └─────────┘                 └─────────────┘
```

## 🚀 Deploy Automatizado

### Opção 1: Script Automatizado (Recomendado)
```bash
# 1. Clonar/navegar para o diretório
cd tech-challenge-b3-bigdata

# 2. Ativar ambiente virtual
source venv/bin/activate

# 3. Executar deploy completo
python deploy/deploy_pipeline.py meu-bucket-unico-b3 --region us-east-1
```

### Opção 2: Deploy Manual

#### Passo 1: Infraestrutura AWS
```bash
# Deploy via CloudFormation
aws cloudformation create-stack \
  --stack-name tech-challenge-b3-pipeline \
  --template-body file://infrastructure/cloudformation-template.yaml \
  --parameters ParameterKey=BucketName,ParameterValue=meu-bucket-unico-b3 \
  --capabilities CAPABILITY_IAM
```

#### Passo 2: Upload dos Scripts
```bash
# Upload do script ETL
aws s3 cp src/etl_job_with_catalog.py s3://meu-bucket-unico-b3/scripts/etl_job.py
```

#### Passo 3: Configurar Job Glue Visual
Siga o guia: `docs/GLUE_VISUAL_JOB_SETUP.md`

## 📊 Teste do Pipeline Completo

### 1. Executar Scraping Local
```bash
# Testar scraping
python demo.py
```

### 2. Upload e Trigger Automático
```bash
# Upload manual para testar trigger
python -c "
from src.scraper import B3Scraper
from src.uploader import S3Uploader
import pandas as pd

scraper = B3Scraper(headless=True)
df = scraper.fetch_with_fallback()

uploader = S3Uploader(bucket='meu-bucket-unico-b3', prefix='raw')
key = uploader.upload_parquet(df, pd.Timestamp.now())
print(f'Dados enviados: {key}')
"
```

### 3. Monitorar Execução
```bash
# Verificar logs da Lambda
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/b3-pipeline-trigger

# Verificar execução do job Glue
aws glue get-job-runs --job-name b3-etl-job-visual --max-results 5
```

### 4. Verificar no Athena
```sql
-- No AWS Console → Athena
SHOW DATABASES;
SHOW TABLES IN b3_database;
SELECT * FROM b3_database.b3_refined_data LIMIT 10;
```

## 🎯 Validação dos Requisitos

### ✅ Checklist de Cumprimento

| Requisito | Status | Localização | Validação |
|-----------|--------|-------------|-----------|
| **Req 1**: Scraping B3 | ✅ | `src/scraper.py` | `python demo.py` |
| **Req 2**: S3 Parquet + Partição | ✅ | `src/uploader.py` | Verificar S3 `raw/date=*/` |
| **Req 3**: S3 → Lambda → Glue | ✅ | CloudFormation | Upload arquivo, verificar logs |
| **Req 4**: Lambda trigger | ✅ | `infrastructure/cloudformation-template.yaml` | Logs Lambda |
| **Req 5**: Job Glue visual | ✅ | `docs/GLUE_VISUAL_JOB_SETUP.md` | Glue Studio |
| **Req 5A**: Agrupamento | ✅ | Aggregate transform | Job visual |
| **Req 5B**: Renomear colunas | ✅ | Rename Field transform | Job visual |
| **Req 5C**: Cálculo data | ✅ | Derived Column transform | Job visual |
| **Req 6**: Refined particionado | ✅ | S3 Target config | Verificar S3 `refined/` |
| **Req 7**: Glue Catalog | ✅ | Target config | `SHOW TABLES` |
| **Req 8**: Athena legível | ✅ | Automatic | Queries funcionando |
| **Req 9**: Notebook (opcional) | ⚠️ | `athena_queries/` | Queries exemplo |

## 🔧 Solução de Problemas

### Lambda não dispara
```bash
# Verificar configuração S3 Event
aws s3api get-bucket-notification-configuration --bucket meu-bucket-unico-b3
```

### Job Glue falha
```bash
# Verificar logs
aws logs get-log-events --log-group-name /aws-glue/jobs/logs-v2 --log-stream-name <job-run-id>
```

### Athena não vê tabela
```sql
-- Atualizar partições
MSCK REPAIR TABLE b3_database.b3_refined_data;
```

### Selenium falha
```bash
# Instalar dependências
pip install selenium webdriver-manager
```

## 📈 Monitoramento e Observabilidade

### CloudWatch Dashboards
1. **Lambda**: Invocações, Erros, Duração
2. **Glue**: Job success rate, Processing time
3. **S3**: Requests, Storage utilization

### Alertas Configurados
- Lambda failures
- Glue job failures  
- S3 upload errors

## 🎉 Validação Final

### 1. Pipeline End-to-End
```bash
# Executar pipeline completo
python -c "
from src.scraper import B3Scraper
from src.uploader import S3Uploader
import pandas as pd
import time

# 1. Scraping
print('1. Scraping...')
scraper = B3Scraper(headless=True)
df = scraper.fetch_with_fallback()

# 2. Upload
print('2. Upload...')
uploader = S3Uploader(bucket='meu-bucket-unico-b3', prefix='raw')
key = uploader.upload_parquet(df, pd.Timestamp.now())

print('3. Pipeline iniciado automaticamente!')
print(f'Arquivo: {key}')
print('4. Aguarde ~5 minutos e verifique Athena')
"
```

### 2. Verificação Athena
```sql
-- Query completa de validação
SELECT 
    codigo_acao,
    nome_acao,
    quantidade_teorica_total,
    percentual_participacao,
    dias_desde_referencia,
    mes_referencia,
    ano_referencia,
    data_ref
FROM b3_database.b3_refined_data 
WHERE data_ref = (SELECT MAX(data_ref) FROM b3_database.b3_refined_data)
ORDER BY percentual_participacao DESC;
```

## 📊 Resultados Esperados

### Dados no S3
```
meu-bucket-b3/
├── raw/
│   └── date=2025-08-01/
│       └── data.parquet
├── refined/
│   └── data_ref=2025-08-01/
│       └── codigo_acao=PETR4/
│           └── data.parquet
└── scripts/
    └── etl_job.py
```

### Tabela no Athena
- **Database**: `b3_database`
- **Table**: `b3_refined_data`
- **Columns**: 12 colunas incluindo transformações
- **Partitions**: `data_ref` + `codigo_acao`
- **Records**: ~22 ações do Ibovespa

## 🎯 Conclusão
Após seguir este guia, você terá um pipeline completo que:
- ✅ Atende todos os 9 requisitos obrigatórios
- ✅ Funciona de forma automatizada
- ✅ Está pronto para produção
- ✅ Inclui monitoramento e observabilidade

**Pipeline Status**: 100% dos requisitos implementados! 🎉 