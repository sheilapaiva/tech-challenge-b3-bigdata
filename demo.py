#!/usr/bin/env python3
"""
Demonstração completa do Tech Challenge B3 Big Data - SCRAPING REAL
"""

import datetime as dt
from src.scraper import B3Scraper
from src.uploader import S3Uploader
import pandas as pd

def main():
    print("🚀 Tech Challenge B3 Big Data - SCRAPING DA B3")
    print("=" * 60)
    
    # 1. Coleta de dados
    print("\n📡 1. Fazendo scraping do site da B3...")
    scraper = B3Scraper(headless=True)  # headless=False para ver o navegador
    df = scraper.fetch_with_fallback()
    
    print(f"✅ Dados coletados: {df.shape[0]} ações do Ibovespa")
    print(f"📅 Data de referência: {df['data_ref'].iloc[0]}")
    print(f"📊 Colunas disponíveis: {list(df.columns)}")
    
    # 2. Mostrar dados reais
    print(f"\n📈 2. Primeiros dados coletados:")
    print("-" * 40)
    # Mostrar apenas algumas colunas para melhor visualização
    display_cols = [col for col in df.columns if col != 'data_ref'][:4]
    print(df[display_cols].head(8).to_string(index=False))
    
    # 3. Análise dos dados reais
    print(f"\n📊 3. Análise dos dados:")
    print("-" * 40)
    
    # Verificar se temos dados numéricos para análise
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        for col in numeric_cols[:3]:  # Mostrar até 3 colunas numéricas
            if df[col].notna().sum() > 0:
                print(f"{col}:")
                print(f"  • Total: {df[col].sum():,.0f}")
                print(f"  • Média: {df[col].mean():,.2f}")
                print(f"  • Máximo: {df[col].max():,.0f}")
    
    # Contagem de tipos de ações
    if 'Tipo' in df.columns:
        print("\nTipos de ações:")
        tipo_counts = df['Tipo'].value_counts()
        for tipo, count in tipo_counts.head(5).items():
            print(f"  • {tipo}: {count} ações")
    
    # 4. Salvar dados localmente
    print(f"\n💾 4. Salvando dados...")
    data_hoje = dt.date.today().strftime("%Y-%m-%d")
    filename = f"dados_b3_{data_hoje}.csv"
    df.to_csv(filename, index=False)
    
    # Também salvar em formato Excel para melhor visualização
    filename_excel = f"dados_b3_{data_hoje}.xlsx"
    df.to_excel(filename_excel, index=False)
    
    print(f"✅ Arquivos salvos:")
    print(f"  📄 CSV: {filename}")
    print(f"  📊 Excel: {filename_excel}")
    
    # 5. Resumo técnico
    print(f"\n🔧 5. Detalhes técnicos:")
    print("-" * 40)
    print(f"• Método: Selenium WebDriver com Chrome")
    print(f"• Site: https://sistemaswebb3-listados.b3.com.br")
    print(f"• Dados: Composição do Ibovespa em tempo real")
    print(f"• Formato: {df.shape[0]} linhas × {df.shape[1]} colunas")
    
    # 6. Pipeline completo (simulação)
    print(f"\n🔄 6. Pipeline completo (próximos passos):")
    print("-" * 40)
    print("1. ✅ Scraper executado com Selenium")
    print("2. 📦 Dados prontos para conversão Parquet")
    print("3. ☁️  Upload S3 (configurar AWS credentials)")
    print("4. ⚡ Lambda trigger (deploy necessário)")
    print("5. 🛠️  Glue Job ETL (deploy necessário)")
    print("6. 🔍 Consulta Athena (deploy necessário)")
    
    # 7. Exemplo de uso do uploader (simulado)
    print(f"\n📤 7. Simulação do upload S3:")
    print("-" * 40)
    try:
        uploader = S3Uploader(bucket="meu-bucket-b3", prefix="raw")
        print(f"✅ Uploader configurado para bucket: {uploader.bucket}")
        print(f"🗂️  Prefix: {uploader.prefix}")
        print(f"📊 Dados prontos para upload: {len(df)} registros")
        print("💡 Configure AWS credentials para fazer upload real")
    except Exception as e:
        print(f"⚠️  Uploader: {e}")
    
    print(f"\n🎉 SCRAPING CONCLUÍDO COM SUCESSO!")
    print(f"📈 Coletadas {df.shape[0]} ações do Ibovespa da B3!")

if __name__ == "__main__":
    main() 