#!/usr/bin/env python3
"""
Script de deploy completo para o Tech Challenge B3
"""

import boto3
import time
import os
import json
from datetime import datetime

class B3PipelineDeployer:
    def __init__(self, bucket_name, region='us-east-1'):
        self.bucket_name = bucket_name
        self.region = region
        self.stack_name = 'tech-challenge-b3-pipeline'
        
        # Clientes AWS
        self.cloudformation = boto3.client('cloudformation', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)
        self.glue = boto3.client('glue', region_name=region)
        
    def deploy_infrastructure(self):
        """Deploy da infraestrutura usando CloudFormation"""
        print("🚀 Iniciando deploy da infraestrutura...")
        
        try:
            # Ler template CloudFormation
            with open('infrastructure/cloudformation-template.yaml', 'r') as f:
                template_body = f.read()
            
            # Verificar se stack já existe
            try:
                self.cloudformation.describe_stacks(StackName=self.stack_name)
                print("Stack já existe, fazendo update...")
                operation = 'update'
                response = self.cloudformation.update_stack(
                    StackName=self.stack_name,
                    TemplateBody=template_body,
                    Parameters=[
                        {
                            'ParameterKey': 'BucketName',
                            'ParameterValue': self.bucket_name
                        }
                    ],
                    Capabilities=['CAPABILITY_IAM']
                )
            except self.cloudformation.exceptions.ClientError:
                print("Stack não existe, criando nova...")
                operation = 'create'
                response = self.cloudformation.create_stack(
                    StackName=self.stack_name,
                    TemplateBody=template_body,
                    Parameters=[
                        {
                            'ParameterKey': 'BucketName',
                            'ParameterValue': self.bucket_name
                        }
                    ],
                    Capabilities=['CAPABILITY_IAM']
                )
            
            print(f"CloudFormation {operation} iniciado...")
            
            # Aguardar conclusão
            waiter = self.cloudformation.get_waiter(f'stack_{operation}_complete')
            waiter.wait(StackName=self.stack_name)
            
            print("✅ Infraestrutura criada com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro no deploy da infraestrutura: {e}")
            return False
    
    def upload_scripts(self):
        """Upload dos scripts para S3"""
        print("📤 Fazendo upload dos scripts...")
        
        try:
            # Upload do script ETL
            self.s3.upload_file(
                'src/etl_job_with_catalog.py',
                self.bucket_name,
                'scripts/etl_job.py'
            )
            
            print("✅ Scripts enviados para S3!")
            return True
            
        except Exception as e:
            print(f"❌ Erro no upload dos scripts: {e}")
            return False
    
    def test_pipeline(self):
        """Testar pipeline completo"""
        print("🧪 Testando pipeline...")
        
        try:
            # 1. Executar scraping e upload
            from src.scraper import B3Scraper
            from src.uploader import S3Uploader
            import pandas as pd
            
            print("1. Coletando dados da B3...")
            scraper = B3Scraper(headless=True)
            df = scraper.fetch_with_fallback()
            
            print("2. Fazendo upload para S3...")
            uploader = S3Uploader(bucket=self.bucket_name, prefix="raw")
            key = uploader.upload_parquet(df, pd.Timestamp.now())
            
            print(f"✅ Dados enviados para: s3://{self.bucket_name}/{key}")
            
            # 2. Aguardar trigger da Lambda (automático)
            print("3. Lambda será acionada automaticamente pelo S3...")
            print("4. Job Glue será iniciado pela Lambda...")
            
            time.sleep(10)  # Aguardar processamento
            
            # 3. Verificar job Glue
            jobs = self.glue.get_job_runs(JobName='b3-etl-job', MaxResults=1)
            if jobs['JobRuns']:
                job_run = jobs['JobRuns'][0]
                print(f"Status do job: {job_run['JobRunState']}")
                
            print("✅ Pipeline testado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste do pipeline: {e}")
            return False
    
    def create_athena_queries(self):
        """Criar queries de exemplo para Athena"""
        print("📊 Criando queries de exemplo para Athena...")
        
        queries = {
            "consulta_basica.sql": """
-- Consulta básica dos dados refinados
SELECT 
    codigo_acao,
    nome_acao,
    quantidade_teorica_total,
    percentual_participacao,
    dias_desde_referencia,
    data_ref
FROM b3_database.b3_refined_data
ORDER BY percentual_participacao DESC
LIMIT 10;
            """,
            
            "analise_por_mes.sql": """
-- Análise por mês
SELECT 
    mes_referencia,
    ano_referencia,
    COUNT(DISTINCT codigo_acao) as total_acoes,
    SUM(percentual_participacao) as participacao_total,
    AVG(quantidade_teorica_total) as qtde_media
FROM b3_database.b3_refined_data
GROUP BY mes_referencia, ano_referencia
ORDER BY ano_referencia, mes_referencia;
            """,
            
            "top_acoes.sql": """
-- Top 5 ações por participação
SELECT 
    codigo_acao,
    nome_acao,
    tipo_acao,
    MAX(percentual_participacao) as max_participacao,
    MAX(quantidade_teorica_total) as max_quantidade
FROM b3_database.b3_refined_data
GROUP BY codigo_acao, nome_acao, tipo_acao
ORDER BY max_participacao DESC
LIMIT 5;
            """,
            
            "evolucao_temporal.sql": """
-- Evolução temporal das ações
SELECT 
    data_ref,
    COUNT(codigo_acao) as total_acoes,
    SUM(percentual_participacao) as participacao_total,
    AVG(dias_desde_referencia) as dias_media
FROM b3_database.b3_refined_data
GROUP BY data_ref
ORDER BY data_ref DESC;
            """
        }
        
        # Criar diretório se não existir
        os.makedirs('athena_queries', exist_ok=True)
        
        # Salvar queries
        for filename, query in queries.items():
            with open(f'athena_queries/{filename}', 'w') as f:
                f.write(query.strip())
        
        print("✅ Queries de exemplo criadas em athena_queries/")
        return True
    
    def deploy_complete(self):
        """Deploy completo do pipeline"""
        print("🎯 Iniciando deploy completo do pipeline B3...")
        print("=" * 60)
        
        steps = [
            ("Infraestrutura AWS", self.deploy_infrastructure),
            ("Upload de scripts", self.upload_scripts),
            ("Queries Athena", self.create_athena_queries),
            ("Teste do pipeline", self.test_pipeline)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"❌ Falha no passo: {step_name}")
                return False
            print(f"✅ {step_name} concluído!")
        
        print("\n🎉 DEPLOY COMPLETO REALIZADO COM SUCESSO!")
        print("=" * 60)
        print("\n📚 Próximos passos:")
        print("1. Acesse o AWS Console → Glue → Jobs")
        print("2. Encontre o job 'b3-etl-job'")
        print("3. Acesse Athena para executar queries")
        print("4. Execute 'python demo.py' para testar o scraping")
        
        return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy do pipeline B3')
    parser.add_argument('bucket_name', help='Nome do bucket S3 (deve ser único)')
    parser.add_argument('--region', default='us-east-1', help='Região AWS')
    
    args = parser.parse_args()
    
    # Verificar se AWS CLI está configurado
    try:
        boto3.client('sts').get_caller_identity()
    except Exception:
        print("❌ AWS não configurado. Execute: aws configure")
        return
    
    # Executar deploy
    deployer = B3PipelineDeployer(args.bucket_name, args.region)
    deployer.deploy_complete()

if __name__ == "__main__":
    main() 