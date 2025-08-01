import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import pyspark.sql.functions as F

# Glue boilerplate
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'S3_SOURCE', 'S3_TARGET'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read raw data
raw_df = spark.read.parquet(args['S3_SOURCE'])

# Example transformations
# A: summarization - count volume by ticker
agg_df = raw_df.groupBy('Nome').agg(
    F.sum('Volume').alias('soma_volume'),
    F.count('*').alias('contagem')
)

# B: rename two columns
renamed_df = agg_df.withColumnRenamed('Nome', 'acao').withColumnRenamed('soma_volume', 'volume_total')

# C: create date diff with current date
renamed_df = renamed_df.withColumn('dias_desde', F.datediff(F.current_date(), F.col('data_ref')))

# Write to target
renamed_df.write.mode('overwrite').partitionBy('data_ref', 'acao').parquet(args['S3_TARGET'])

job.commit()