import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
import pyspark.sql.functions as F
from datetime import datetime

# Obter argumentos do job
args = getResolvedOptions(sys.argv, [
    'JOB_NAME', 
    'S3_SOURCE', 
    'S3_TARGET',
    'DATABASE_NAME',
    'TABLE_NAME'
])

# Inicializar contextos
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

print(f"Iniciando job ETL: {args['JOB_NAME']}")
print(f"Source: {args['S3_SOURCE']}")
print(f"Target: {args['S3_TARGET']}")

try:
    # 1. Ler dados brutos do S3
    print("1. Lendo dados brutos...")
    raw_df = spark.read.parquet(args['S3_SOURCE'])
    print(f"Registros lidos: {raw_df.count()}")
    
    # Mostrar schema dos dados de entrada
    print("Schema dos dados brutos:")
    raw_df.printSchema()
    
    # 2. TRANSFORMAÇÃO A: Agrupamento e sumarização
    print("2. Executando transformação A: Agrupamento e sumarização...")
    
    # Agrupamento por código da ação com múltiplas agregações
    agg_df = raw_df.groupBy('Código', 'data_ref').agg(
        F.first('Ação').alias('nome_acao'),
        F.first('Tipo').alias('tipo_acao'),
        F.sum(F.col('Qtde. Teórica').cast('double')).alias('qtde_total'),
        F.sum(F.col('Part. (%)').cast('double')).alias('participacao_total'),
        F.count('*').alias('contagem_registros'),
        F.avg(F.col('Part. (%)').cast('double')).alias('participacao_media')
    )
    
    print(f"Registros após agrupamento: {agg_df.count()}")
    
    # 3. TRANSFORMAÇÃO B: Renomear duas colunas
    print("3. Executando transformação B: Renomeação de colunas...")
    
    renamed_df = agg_df \
        .withColumnRenamed('Código', 'codigo_acao') \
        .withColumnRenamed('qtde_total', 'quantidade_teorica_total') \
        .withColumnRenamed('participacao_total', 'percentual_participacao')
    
    # 4. TRANSFORMAÇÃO C: Cálculo com campos de data
    print("4. Executando transformação C: Cálculo com campos de data...")
    
    # Adicionar colunas de data calculadas
    final_df = renamed_df \
        .withColumn('data_processamento', F.current_timestamp()) \
        .withColumn('dias_desde_referencia', 
                   F.datediff(F.current_date(), F.col('data_ref'))) \
        .withColumn('mes_referencia', 
                   F.month(F.col('data_ref'))) \
        .withColumn('ano_referencia', 
                   F.year(F.col('data_ref'))) \
        .withColumn('data_ref_formatada', 
                   F.date_format(F.col('data_ref'), 'yyyy-MM-dd'))
    
    print("5. Schema final dos dados:")
    final_df.printSchema()
    
    # 6. Salvar dados refinados no S3 com particionamento
    print("6. Salvando dados refinados...")
    
    # Particionamento por data_ref e codigo_acao (requisito 6)
    final_df.write \
        .mode('overwrite') \
        .partitionBy('data_ref', 'codigo_acao') \
        .option("compression", "snappy") \
        .parquet(args['S3_TARGET'])
    
    print(f"Dados salvos em: {args['S3_TARGET']}")
    
    # 7. REQUISITO 7: Catalogar dados automaticamente no Glue Catalog
    print("7. Catalogando dados no Glue Catalog...")
    
    # Converter para DynamicFrame para catalogação
    dynamic_frame = DynamicFrame.fromDF(final_df, glueContext, "refined_data")
    
    # Escrever no Glue Catalog (cria tabela automaticamente)
    glueContext.write_dynamic_frame.from_catalog(
        frame=dynamic_frame,
        database=args['DATABASE_NAME'],
        table_name=args['TABLE_NAME'],
        additional_options={
            "path": args['S3_TARGET'],
            "partitionKeys": ["data_ref", "codigo_acao"]
        }
    )
    
    print(f"Tabela '{args['TABLE_NAME']}' criada/atualizada no database '{args['DATABASE_NAME']}'")
    
    # 8. Estatísticas finais
    print("8. Estatísticas finais:")
    print(f"Total de ações processadas: {final_df.select('codigo_acao').distinct().count()}")
    print(f"Registros finais: {final_df.count()}")
    print(f"Partições criadas: {final_df.select('data_ref', 'codigo_acao').distinct().count()}")
    
    # Mostrar amostra dos dados
    print("Amostra dos dados processados:")
    final_df.select('codigo_acao', 'nome_acao', 'quantidade_teorica_total', 
                   'percentual_participacao', 'dias_desde_referencia').show(10)

except Exception as e:
    print(f"Erro durante processamento: {str(e)}")
    raise e

finally:
    # Finalizar job
    job.commit()
    print("Job ETL finalizado com sucesso!") 