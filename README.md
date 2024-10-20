Leitura de Chamada Escolar com OCR
Este é um aplicativo desenvolvido em Streamlit que usa a API OCR.Space para extrair dados de listas de chamada escolar a partir de imagens. O texto extraído é processado e os dados organizados são armazenados em um banco de dados SQLite. O aplicativo permite carregar imagens a partir de um arquivo ou capturar imagens com a câmera do dispositivo.

Funcionalidades
Captura de imagem via upload ou câmera.
Extração de texto de listas de chamada usando a API OCR.Space.
Organização dos dados extraídos para identificar alunos e suas presenças/ausências por semana.
Criação e inserção dinâmica de dados em uma tabela de um banco de dados SQLite.
Exibição dos dados inseridos em formato de tabela.
Requisitos
Python 3.7 ou superior
Streamlit
OCR.Space API Key (criar conta em OCR.Space para obter a chave de API)
Bibliotecas Necessárias
Instale as dependências utilizando o pip:

bash
Copiar código
pip install requests pillow sqlite3 pandas streamlit
Como Executar
Obtenha uma chave de API da OCR.Space aqui.

Clone este repositório:

bash
Copiar código
git clone https://github.com/seu_usuario/seu_repositorio.git
cd seu_repositorio
Substitua a chave de API:

No arquivo app.py, substitua 'your_api_key' pela sua chave de API no trecho:
python
Copiar código
extracted_text = ocr_space_file(image, api_key='your_api_key')
Inicie o aplicativo:

No terminal, execute o seguinte comando para iniciar o Streamlit:
bash
Copiar código
streamlit run app.py
Acesse a aplicação:

Acesse a aplicação em http://localhost:8501 no seu navegador.
Uso
Carregar Imagem
Escolha a opção "Carregar Imagem" e faça o upload de uma imagem no formato PNG, JPG ou JPEG. A imagem será exibida na interface e você poderá processá-la para extrair os dados.
Usar Câmera
Escolha a opção "Usar Câmera" para capturar uma imagem diretamente. Após capturar a imagem, ela será exibida e estará pronta para o processamento.
Extrair e Inserir Dados
Clique no botão "Extrair Dados" para processar a imagem usando a API OCR. O texto extraído será exibido, e o sistema organizará os dados, criando uma tabela no banco de dados SQLite local.
Após a inserção dos dados, a tabela com os registros será exibida diretamente no aplicativo.
Estrutura do Projeto
plaintext
Copiar código
|-- app.py               # Arquivo principal com o código do aplicativo Streamlit
|-- chamada_escolar.db    # Banco de dados SQLite onde os dados são armazenados
|-- README.md             # Documentação do projeto
Banco de Dados
O banco de dados SQLite será criado automaticamente no primeiro uso do aplicativo. Ele armazena os nomes dos alunos e seus respectivos status de presença/ausência por semana.

Funções Principais
ocr_space_file(image, api_key, language): Realiza a requisição à API OCR.Space e retorna o texto extraído.
organize_data(text): Organiza o texto extraído, identificando os alunos e o status de presença/ausência por semana.
create_table(weeks): Cria uma tabela no banco de dados com colunas dinâmicas para as semanas encontradas.
insert_into_db(data, weeks): Insere os dados organizados no banco de dados SQLite.
Observações
Certifique-se de ter uma conexão com a internet para que a API OCR.Space funcione corretamente.
Este aplicativo foi desenvolvido para processar listas de chamada escolar em português (language='por'), mas pode ser adaptado para outros idiomas, alterando o parâmetro de linguagem.
Melhorias Futuras
Suporte para processamento em lote de imagens.
Melhor tratamento de erros e logs para monitoramento.
Opção de exportar os dados para diferentes formatos (CSV, Excel).
