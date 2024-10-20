# import streamlit as st
# import cv2
# import pytesseract
# from PIL import Image
# import numpy as np
# import sqlite3
# import tempfile

# # Configuração do Tesseract
# pytesseract.pytesseract.tesseract_cmd = r'D:\Asimov\TCC\tesseract\tesseract.exe'  # Ajuste o caminho conforme necessário

# # Função para inicializar o banco de dados SQLite e ajustar a tabela
# def init_db():
#     conn = sqlite3.connect('chamada_escolar.db')
#     c = conn.cursor()

#     # Criação da tabela se ela não existir
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS chamada (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             nome TEXT,
#             status TEXT
#         )
#     ''')
    
#     # Verifica se a coluna "semana" já existe
#     c.execute("PRAGMA table_info(chamada)")
#     columns = [col[1] for col in c.fetchall()]
    
#     if "semana" not in columns:
#         # Se a coluna "semana" não existir, altere a tabela para adicioná-la
#         c.execute("ALTER TABLE chamada ADD COLUMN semana INTEGER")
    
#     conn.commit()
#     conn.close()

# # Função para inserir dados no banco de dados
# def insert_data(nome, status, semana):
#     conn = sqlite3.connect('chamada_escolar.db')
#     c = conn.cursor()
#     c.execute('INSERT INTO chamada (nome, status, semana) VALUES (?, ?, ?)', (nome, status, semana))
#     conn.commit()
#     conn.close()

# # Função para processar a imagem e extrair o texto
# def process_image(image):
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     # Pré-processamento da imagem (remoção de ruído e melhoria de contraste)
#     gray = cv2.medianBlur(gray, 3)
#     text = pytesseract.image_to_string(gray)
#     return text

# # Função para capturar imagem da câmera do dispositivo
# def capture_image():
#     st.title("Leitura de Chamada Escolar")
    
#     # Componente para o upload da imagem
#     uploaded_image = st.file_uploader("Faça o upload de uma imagem ou use a câmera do seu dispositivo", type=["jpg", "jpeg", "png"])

#     if uploaded_image is not None:
#         image = Image.open(uploaded_image)
#         img_array = np.array(image)
#         st.image(img_array, caption="Imagem Capturada", use_column_width=True)
#         return img_array
#     return None

# # Função principal
# def main():
#     init_db()  # Inicializa o banco de dados e ajusta a tabela, se necessário
    
#     # Captura da imagem
#     image = capture_image()
    
#     if image is not None:
#         if st.button("Processar Imagem e Extrair Dados"):
#             extracted_text = process_image(image)
            
#             st.subheader("Texto Extraído")
#             st.text(extracted_text)
            
#             # Aqui, assumimos que o texto contém a lista de presença com as colunas separadas por espaços
#             lines = extracted_text.splitlines()
            
#             for line in lines:
#                 # Ignora linhas vazias ou com informações irrelevantes
#                 if len(line.strip()) > 0 and any(char.isalpha() for char in line):
#                     # Supondo que a linha seja algo como: "João Silva P P F C P"
#                     parts = line.split()
#                     nome_aluno = ' '.join(parts[:-5])  # O nome do aluno
#                     status_semanas = parts[-5:]  # Status das 5 semanas
                    
#                     # Armazena cada semana no banco de dados
#                     for semana, status in enumerate(status_semanas, 1):
#                         insert_data(nome_aluno, status, semana)
#                         st.success(f"Dados de {nome_aluno} (Semana {semana}) armazenados com sucesso!")
    
#     # Exibe os dados armazenados
#     st.subheader("Dados Armazenados no Banco de Dados")
#     conn = sqlite3.connect('chamada_escolar.db')
#     c = conn.cursor()
#     c.execute("SELECT nome, status, semana FROM chamada")
#     rows = c.fetchall()
#     conn.close()
    
#     for row in rows:
#         st.text(f"Aluno: {row[0]}, Status: {row[1]}, Semana: {row[2]}")
    
# if __name__ == '__main__':
#     main()




import cv2
import pytesseract
from PIL import Image
import sqlite3
import streamlit as st
import re
import pandas as pd
import numpy as np
import os

# Configuração do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'D:\Asimov\App-Lista-chamada\tesseract\tesseract.exe'  # Ajuste o caminho conforme necessário
os.environ['TESSDATA_PREFIX'] = r'D:\Asimov\App-Lista-chamada\tesseract\tessdata'  # Verifique se este caminho está correto

# Função para pré-processar a imagem
def process_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    text = pytesseract.image_to_string(gray, lang='por')  # Especificando o idioma
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
        extracted_text = extract_text(np.array(image))
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
