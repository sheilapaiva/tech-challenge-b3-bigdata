#!/usr/bin/env python3
"""
Demonstração completa do Tech Challenge B3 Big Data
"""

import datetime as dt
from src.scraper import B3Scraper
from src.uploader import S3Uploader
import pandas as pd

def main():
    print("🚀 Tech Challenge B3 Big Data - Demonstração")
    print("=" * 50)
    
    # 1. Coleta de dados
    print("\n📊 1. Coletando dados da B3...")
    scraper = B3Scraper()
    df = scraper.fetch()
    
    print(f"✅ Dados coletados: {df.shape[0]} ações")
    print(f"📅 Data de referência: {df['data_ref'].iloc[0]}")
    
    # 2. Mostrar dados
    print("\n📈 2. Dados coletados:")
    print("-" * 30)
    print(df.to_string(index=False))
    
    # 3. Estatísticas básicas
    print(f"\n📊 3. Estatísticas:")
    print("-" * 30)
    print(f"Volume total: {df['Volume'].sum():,}")
    print(f"Maior alta: {df['Variação (%)'].max():.2f}%")
    print(f"Maior baixa: {df['Variação (%)'].min():.2f}%")
    print(f"Preço médio: R$ {df['Último'].mean():.2f}")
    
    # 4. Salvar dados localmente
    print(f"\n💾 4. Salvando dados...")
    data_hoje = dt.date.today().strftime("%Y-%m-%d")
    filename = f"dados_b3_{data_hoje}.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Arquivo salvo: {filename}")
    
    # 5. Simulação do pipeline completo
    print(f"\n🔄 5. Pipeline completo (simulação):")
    print("-" * 30)
    print("1. ✅ Scraper executado")
    print("2. 📦 Dados em formato parquet (ready)")
    print("3. ☁️  Upload S3 (configurar AWS credentials)")
    print("4. ⚡ Lambda trigger (deploy necessário)")
    print("5. 🛠️  Glue Job ETL (deploy necessário)")
    print("6. 🔍 Consulta Athena (deploy necessário)")
    
    # 6. Próximos passos
    print(f"\n📋 6. Próximos passos para deploy completo:")
    print("-" * 30)
    print("• Configurar credenciais AWS")
    print("• Criar bucket S3")
    print("• Deploy da função Lambda")
    print("• Configurar Glue Job")
    print("• Configurar Athena e Glue Catalog")
    
    print(f"\n🎉 Demonstração concluída com sucesso!")

if __name__ == "__main__":
    main() 