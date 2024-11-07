import sqlite3
import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import spacy

# Carregar o modelo do spaCy
nlp = spacy.load("pt_core_news_sm")


def ocr_space_file(image, overlay=False, api_key='K85585257288957', language='por', file_type='jpg'):
    """Utiliza a API OCR.space para realizar a leitura de texto em imagens"""
    img_buffer = BytesIO()

    # Convertendo a imagem para o modo RGB se necessário
    if image.mode != 'RGB':
        image = image.convert('RGB')

    image.save(img_buffer, format='JPEG')
    img_buffer.seek(0)

    payload = {
        'isOverlayRequired': overlay,
        'apikey': api_key,
        'language': language,
        'filetype': file_type
    }
    files = {'filename': img_buffer}
    r = requests.post('https://api.ocr.space/parse/image', files=files, data=payload)
    
    # Verificando o código de saída da API
    if r.status_code != 200:
        return {'error': f"Erro na requisição: {r.status_code}"}
    
    return r.json()


# Função para organizar os dados extraídos
def organizar_dados(texto_extraido):
    doc = nlp(texto_extraido)
    dados_organizados = []
    semana = 1  # Variável para controlar a semana (1 a 5)

    # Tentando identificar informações diretamente sobre presenças/faltas
    for ent in doc.ents:
        if ent.label_ == 'PER':  # Identifica pessoas (nomes)
            nome_aluno = ent.text.strip()
            status_semana = {'semana_1': 'ausente', 'semana_2': 'ausente', 'semana_3': 'ausente', 'semana_4': 'ausente', 'semana_5': 'ausente'}

            # Se você tiver mais informações sobre presenças ou faltas por semana, pode incluir aqui
            # Por exemplo, mapeando "presente" e "ausente" de acordo com as semanas:
            if f"semana {semana}" in texto_extraido:
                status_semana[f'semana_{semana}'] = 'presente'

            dados_organizados.append({
                "nome": nome_aluno,
                "semana_1": status_semana["semana_1"],
                "semana_2": status_semana["semana_2"],
                "semana_3": status_semana["semana_3"],
                "semana_4": status_semana["semana_4"],
                "semana_5": status_semana["semana_5"],
                "observacao": ""  # Inicialmente vazio, para observações adicionais
            })
            semana += 1

    # Caso não encontre nenhuma semana nas entidades, podemos organizar o texto de forma simples
    if not dados_organizados:
        linhas = texto_extraido.split('\n')
        for linha in linhas:
            if linha.strip():  # Ignora linhas vazias
                dados_organizados.append({
                    "nome": linha.strip(),
                    "semana_1": "ausente",  # Atribui status fixo por enquanto
                    "semana_2": "ausente",
                    "semana_3": "ausente",
                    "semana_4": "ausente",
                    "semana_5": "ausente",
                    "observacao": ""
                })
    
    return dados_organizados


# Função para carregar dados do banco de dados
def carregar_dados_bd():
    conn = sqlite3.connect('chamada_escolar.db')
    df = pd.read_sql_query("SELECT * FROM chamada", conn)
    conn.close()
    return df


# Função para criar a tabela caso não exista
def criar_tabela_se_nao_existir():
    try:
        conn = sqlite3.connect('chamada_escolar.db')
        cursor = conn.cursor()
        cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS chamada (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            semana_1 TEXT,  -- Presença ou falta na primeira semana
            semana_2 TEXT,  -- Presença ou falta na segunda semana
            semana_3 TEXT,  -- Presença ou falta na terceira semana
            semana_4 TEXT,  -- Presença ou falta na quarta semana
            semana_5 TEXT,  -- Presença ou falta na quinta semana
            observacao TEXT  -- Observações adicionais (transferência, justificativa, etc.)
        )
        ''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"Erro ao criar a tabela: {e}")
    else:
        st.success("Tabela criada com sucesso (ou já existe).")


# Função para inserir dados sem sobrescrever
def inserir_dados_bd(dados_organizados):
    try:
        conn = sqlite3.connect('chamada_escolar.db')
        cursor = conn.cursor()

        for dado in dados_organizados:
            cursor.execute(''' 
            INSERT INTO chamada (nome, semana_1, semana_2, semana_3, semana_4, semana_5, observacao) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (dado['nome'], dado['semana_1'], dado['semana_2'], dado['semana_3'], dado['semana_4'], dado['semana_5'], dado['observacao']))
        
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"Erro ao inserir dados: {e}")
    else:
        st.success("Dados inseridos com sucesso!")


# Título da aplicação
st.title("OCR para Listas de Chamada Escolar com IA")

# Navegação entre páginas
page = st.sidebar.selectbox("Selecione a página", ["Captura de Imagem", "Verificar Dados Armazenados"])

if page == "Captura de Imagem":
    # Opções de entrada de imagem
    st.subheader("Escolha como deseja carregar a imagem:")
    opcao_entrada = st.radio("Selecione uma opção:", ("Carregar Imagem", "Usar Câmera"))

    if opcao_entrada == "Carregar Imagem":
        uploaded_file = st.file_uploader("Escolha uma imagem", type=["png", "jpg", "jpeg"])

        if uploaded_file is not None:
            st.image(uploaded_file, caption="Imagem Carregada", use_column_width=True)
            image = Image.open(uploaded_file)

            st.text("Enviando imagem para OCR API...")
            extracted_data = ocr_space_file(image)

            if extracted_data.get('OCRExitCode') == 1:
                st.text("Texto extraído com sucesso!")
                parsed_text = extracted_data['ParsedResults'][0]['ParsedText']
                st.subheader("Texto Extraído")
                st.text(parsed_text)

                st.text("Organizando dados extraídos com IA...")
                dados_organizados = organizar_dados(parsed_text)

                st.subheader("Dados Organizados (Reconhecidos com IA):")
                df = pd.DataFrame(dados_organizados)
                st.dataframe(df)

                # Adicionar Observações
                for index, row in df.iterrows():
                    with st.expander(f"Observações para {row['nome']}"):
                        observacao = st.text_area(f"Observações para {row['nome']}", value=row['observacao'], key=index)
                        if observacao != row['observacao']:
                            df.at[index, 'observacao'] = observacao

                st.text("Inserindo dados no banco de dados...")

                # Cria a tabela caso não exista
                criar_tabela_se_nao_existir()

                # Insere os dados sem sobrescrever os existentes
                inserir_dados_bd(dados_organizados)

            else:
                st.error(f"A extração de texto falhou: {extracted_data.get('ErrorMessage', 'Erro desconhecido')}")
                
    elif opcao_entrada == "Usar Câmera":
        picture = st.camera_input("Tirar uma foto")
        
        if picture is not None:
            st.image(picture, caption="Imagem Capturada", use_column_width=True)
            image = Image.open(picture)
            
            st.text("Enviando imagem para OCR API...")
            extracted_data = ocr_space_file(image)
            
            if extracted_data.get('OCRExitCode') == 1:
                st.text("Texto extraído com sucesso!")
                parsed_text = extracted_data['ParsedResults'][0]['ParsedText']
                st.subheader("Texto Extraído")
                st.text(parsed_text)
                
                st.text("Organizando dados extraídos com IA...")
                dados_organizados = organizar_dados(parsed_text)
                
                st.subheader("Dados Organizados (Reconhecidos com IA):")
                df = pd.DataFrame(dados_organizados)
                st.dataframe(df)

                # Adicionar Observações
                for index, row in df.iterrows():
                    with st.expander(f"Observações para {row['nome']}"):
                        observacao = st.text_area(f"Observações para {row['nome']}", value=row['observacao'], key=index)
                        if observacao != row['observacao']:
                            df.at[index, 'observacao'] = observacao

                st.text("Inserindo dados no banco de dados...")

                # Cria a tabela caso não exista
                criar_tabela_se_nao_existir()

                # Insere os dados sem sobrescrever os existentes
                inserir_dados_bd(dados_organizados)

            else:
                st.error(f"A extração de texto falhou: {extracted_data.get('ErrorMessage', 'Erro desconhecido')}")

elif page == "Verificar Dados Armazenados":
    st.subheader("Dados Armazenados no Banco de Dados")
    st.text("Carregando dados do banco de dados...")

    dados_bd = carregar_dados_bd()

    if not dados_bd.empty:
        st.dataframe(dados_bd)
        # Botão para baixar os dados em CSV
        st.download_button(label="Baixar dados como CSV", data=dados_bd.to_csv(index=False), file_name="dados_chamada.csv", mime="text/csv")
    else:
        st.warning("Nenhum dado encontrado no banco de dados.")

