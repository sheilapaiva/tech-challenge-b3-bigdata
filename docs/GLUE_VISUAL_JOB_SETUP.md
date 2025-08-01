# Configuração do Job Glue no Modo Visual (Requisito 5)

## 📋 Requisito Obrigatório
O **Requisito 5** do Tech Challenge especifica que "o job Glue deve ser feito no modo visual". Este documento detalha como configurar o job usando o AWS Glue Studio (interface visual).

## 🎯 Transformações Obrigatórias
O job deve conter as seguintes transformações:
- **A**: Agrupamento numérico, sumarização, contagem ou soma
- **B**: Renomear duas colunas existentes além das de agrupamento  
- **C**: Realizar um cálculo com campos de data

## 🚀 Passo a Passo - Criação no Glue Studio

### 1. Acesso ao AWS Glue Studio
1. Acesse o AWS Console
2. Navegue para **AWS Glue**
3. No menu lateral, clique em **Jobs**
4. Clique em **Create job**
5. Selecione **Visual with a source and target**

### 2. Configuração da Fonte (Source)
1. **Adicionar Data Source**:
   - Node type: **S3**
   - S3 URL: `s3://seu-bucket/raw/`
   - Data format: **Parquet**
   - Name: `RawB3Data`

2. **Configurações adicionais**:
   - Partition predicate: `date >= '2025-01-01'`
   - Include paths: `s3://seu-bucket/raw/date=*/`

### 3. Transformação A - Agrupamento e Sumarização
1. **Adicionar Transform Node**:
   - Selecione a fonte `RawB3Data`
   - Adicione transform: **Aggregate**
   - Nome: `AggregateByStock`

2. **Configurar Aggregate**:
   - **Group by**: 
     - `Código` 
     - `data_ref`
   - **Aggregations**:
     - `sum(cast(Qtde. Teórica, double))` → `qtde_total`
     - `sum(cast(Part. (%), double))` → `participacao_total`
     - `count(*)` → `contagem_registros`
     - `first(Ação)` → `nome_acao`
     - `first(Tipo)` → `tipo_acao`

### 4. Transformação B - Renomeação de Colunas
1. **Adicionar Transform Node**:
   - Selecione `AggregateByStock`
   - Adicione transform: **Rename Field**
   - Nome: `RenameColumns`

2. **Configurar Rename Field**:
   - `Código` → `codigo_acao`
   - `qtde_total` → `quantidade_teorica_total`
   - `participacao_total` → `percentual_participacao`

### 5. Transformação C - Cálculos com Data
1. **Adicionar Transform Node**:
   - Selecione `RenameColumns`
   - Adicione transform: **Derived Column**
   - Nome: `DateCalculations`

2. **Configurar Derived Column**:
   ```sql
   -- Adicionar as seguintes colunas calculadas:
   
   dias_desde_referencia = datediff(current_date(), data_ref)
   mes_referencia = month(data_ref)
   ano_referencia = year(data_ref)
   data_processamento = current_timestamp()
   data_ref_formatada = date_format(data_ref, 'yyyy-MM-dd')
   ```

### 6. Configuração do Target (Destino)
1. **Adicionar Data Target**:
   - Selecione `DateCalculations`
   - Node type: **S3**
   - Format: **Parquet**
   - S3 URL: `s3://seu-bucket/refined/`
   - Data Catalog table: **Create table in Data Catalog**

2. **Configurações do Target**:
   - **Database**: `b3_database`
   - **Table name**: `b3_refined_data`
   - **Partition keys**: 
     - `data_ref`
     - `codigo_acao`
   - **Compression**: `snappy`

### 7. Configurações do Job
1. **Job Details**:
   - **Name**: `b3-etl-job-visual`
   - **IAM Role**: `GlueJobRole` (criado pelo CloudFormation)
   - **Glue version**: `3.0`
   - **Language**: `Python 3`

2. **Advanced properties**:
   - **Worker type**: `G.1X`
   - **Number of workers**: `2`
   - **Job timeout**: `60 minutes`
   - **Job bookmark**: `Enable`

3. **Monitoring**:
   - **CloudWatch Logs**: `Enable`
   - **Spark UI**: `Enable`
   - **Job metrics**: `Enable`

### 8. Parâmetros do Job
Adicionar os seguintes parâmetros:
```
--DATABASE_NAME: b3_database
--TABLE_NAME: b3_refined_data
--TempDir: s3://seu-bucket/temp/
--enable-metrics: true
--enable-continuous-cloudwatch-log: true
```

## 🔧 Diagrama Visual do Job

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌──────────────────┐    ┌─────────────┐
│   S3 Raw    │───▶│   Aggregate     │───▶│  Rename Fields  │───▶│ Date Calculations│───▶│ S3 Refined  │
│   Source    │    │ (Transform A)   │    │ (Transform B)   │    │  (Transform C)   │    │   Target    │
└─────────────┘    └─────────────────┘    └─────────────────┘    └──────────────────┘    └─────────────┘
```

## ✅ Validação das Transformações

### Transform A - Agrupamento ✅
- Agrupamento por `Código` e `data_ref`
- Soma de `Qtde. Teórica` e `Part. (%)`
- Contagem de registros
- First functions para campos categóricos

### Transform B - Renomeação ✅  
- `Código` → `codigo_acao`
- `qtde_total` → `quantidade_teorica_total`
- `participacao_total` → `percentual_participacao`

### Transform C - Cálculo de Data ✅
- Diferença entre data atual e data de referência
- Extração de mês e ano
- Formatação de data
- Timestamp de processamento

## 💾 Catalogação Automática (Requisito 7)
O job visual automaticamente:
1. Cria tabela no Glue Catalog
2. Define partições por `data_ref` e `codigo_acao`
3. Atualiza schema automaticamente
4. Disponibiliza dados para Athena

## 🚀 Execução e Monitoramento

### Como executar:
1. No Glue Studio, clique em **Save** para salvar o job
2. Clique em **Run** para executar manualmente
3. O job também será executado automaticamente via Lambda trigger

### Monitoramento:
1. **AWS Glue Console** → Jobs → `b3-etl-job-visual`
2. **CloudWatch Logs** para detalhes de execução
3. **Spark UI** para performance metrics

## 📊 Verificação no Athena (Requisito 8)
Após execução do job, verifique no Athena:

```sql
-- Verificar se tabela foi criada
SHOW TABLES IN b3_database;

-- Consultar dados
SELECT * FROM b3_database.b3_refined_data LIMIT 10;

-- Verificar partições
SHOW PARTITIONS b3_database.b3_refined_data;
```

## 🎯 Cumprimento dos Requisitos

| Requisito | Status | Implementação |
|-----------|--------|---------------|
| **Req 5**: Job modo visual | ✅ | Configurado no Glue Studio |
| **Req 5A**: Agrupamento | ✅ | Aggregate transform |
| **Req 5B**: Renomear colunas | ✅ | Rename Field transform |
| **Req 5C**: Cálculo data | ✅ | Derived Column transform |
| **Req 6**: Particionamento | ✅ | data_ref + codigo_acao |
| **Req 7**: Catalogação | ✅ | Automática no target |
| **Req 8**: Athena | ✅ | Tabela disponível |

## 📝 Notas Importantes
1. O job visual substitui o `etl_job.py` (código Python)
2. Todas as transformações são configuradas via interface gráfica
3. O resultado final é idêntico ao código Python
4. Catalogação é automática quando configurado no target
5. Particionamento é definido no S3 target configuration 