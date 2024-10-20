import pytesseract
from PIL import Image, ImageOps
import sqlite3
import streamlit as st
import re
import pandas as pd
import numpy as np

# Configuração do Tesseract
# Ajuste o caminho do Tesseract conforme necessário, ou remova essa linha se estiver usando Streamlit Cloud
# pytesseract.pytesseract.tesseract_cmd = r'D:\Asimov\App-Lista-chamada\tesseract\tesseract.exe'

# Função para pré-processar a imagem usando Pillow
def process_image(image):
    gray = ImageOps.grayscale(image)  # Convertendo a imagem para tons de cinza
    text = pytesseract.image_to_string(gray, lang='por')  # Extraindo o texto com o Tesseract
    return text

# Função para extrair texto da imagem
def extract_text(image):
    # Pré-processar a imagem e aplicar OCR
    text = process_image(image)
    return text

# Função para organizar os dados extraídos
def organize_data(text):
    lines = text.splitlines()
    organized_data = []
    
    weeks = []
    for line in lines:
        if line.strip():
            # Detectar as semanas (seções com números que indicam semanas)
            if re.search(r'\d+\s+\d+\s+\d+\s+\d+', line):  # Linha com números de semanas
                weeks = re.findall(r'\d+', line)  # Captura as semanas
                continue
            
            # Verificar se a linha contém o nome do aluno e status de presença
            if any(char.isdigit() for char in line):  # Checa se a linha contém números
                parts = line.split()
                nome = ' '.join(parts[:-len(weeks)])  # Nome do aluno
                status_semanas = parts[-len(weeks):]  # Status de presença/ausência
                organized_data.append({"nome": nome, "status": status_semanas})
    
    return organized_data, weeks

# Função para criar a tabela automaticamente
def create_table(weeks):
    conn = sqlite3.connect('chamada_escolar.db')
    c = conn.cursor()
    
    # Verificar se weeks está vazio
    if not weeks:
        st.warning("Nenhuma semana encontrada. A tabela não será criada.")
        return
    
    # Criar a tabela com colunas dinâmicas baseadas nas semanas
    columns = ', '.join([f"semana_{week} TEXT" for week in weeks])
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS chamada (
        nome TEXT,
        {columns}
    )
    """
    c.execute(create_table_query)
    conn.commit()
    conn.close()

# Função para inserir os dados no banco de dados
def insert_into_db(data, weeks):
    conn = sqlite3.connect('chamada_escolar.db')
    c = conn.cursor()
    
    # Verificar se weeks está vazio
    if not weeks:
        st.warning("Nenhuma semana encontrada. Os dados não serão inseridos.")
        return

    # Inserir os dados organizados
    for item in data:
        nome = item['nome']
        status_values = ', '.join([f"'{status}'" for status in item['status']])
        insert_query = f"""
        INSERT INTO chamada (nome, {', '.join([f'semana_{week}' for week in weeks])})
        VALUES ('{nome}', {status_values})
        """
        c.execute(insert_query)
    
    conn.commit()
    conn.close()

# Função principal para o Streamlit
def main():
    st.title("Leitura de Chamada Escolar")

    # Opções de carregamento de imagem
    option = st.radio("Escolha como deseja carregar a imagem:", ("Carregar Imagem", "Usar Câmera"))

    image = None

    if option == "Carregar Imagem":
        # Upload de imagem
        uploaded_file = st.file_uploader("Escolha uma imagem", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Imagem Carregada", use_column_width=True)

    elif option == "Usar Câmera":
        # Captura de imagem usando a câmera
        captured_image = st.camera_input("Tire uma foto")
        if captured_image is not None:
            image = Image.open(captured_image)
            st.image(image, caption="Imagem Capturada", use_column_width=True)

    # Botão para processar a imagem
    if image and st.button("Extrair Dados"):
        # Extrair texto da imagem
        extracted_text = extract_text(image)
        st.subheader("Texto Extraído")
        st.text(extracted_text)
        
        # Organizar os dados
        organized_data, weeks = organize_data(extracted_text)
        
        # Criar a tabela dinamicamente
        create_table(weeks)
        
        # Inserir dados no banco de dados
        insert_into_db(organized_data, weeks)
        st.success("Dados inseridos com sucesso no banco de dados!")
        
        # Exibir dados em tabela
        conn = sqlite3.connect('chamada_escolar.db')
        df = pd.read_sql_query("SELECT * FROM chamada", conn)
        st.table(df)

if __name__ == '__main__':
    main()
