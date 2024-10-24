# Leitura de Chamada Escolar

Este projeto é uma aplicação web desenvolvida em Streamlit que utiliza a tecnologia de Reconhecimento Óptico de Caracteres (OCR) para ler dados de presença escolar a partir de imagens. A aplicação extrai informações sobre alunos e seus status de presença, armazena esses dados em um banco de dados SQLite e os exibe em uma tabela.

## Funcionalidades

- **Carregamento de Imagem**: Permite que os usuários carreguem imagens de suas listas de chamada em formatos PNG, JPG ou JPEG.
- **Captura de Imagem**: Os usuários podem tirar uma foto diretamente pela aplicação usando a câmera.
- **Extração de Texto**: Utiliza a API OCR.Space para converter a imagem carregada em texto.
- **Organização de Dados**: Estrutura os dados extraídos em um formato que associa nomes de alunos ao seu status de presença.
- **Armazenamento em Banco de Dados**: Insere os dados organizados em uma tabela SQLite.
- **Exibição de Dados**: Mostra os dados de presença em uma tabela na interface da aplicação.

## Tecnologias Usadas

- Python
- Streamlit
- SQLite
- PIL (Python Imaging Library)
- Requests
- Pandas
- OCR.Space API

## Como Usar

1. Clone o repositório:
    ```bash
    git clone https://github.com/heliogald/app_lista_de_chamada.git
    cd app_lista_de_chamada
    ```

2. Instale as dependências necessárias:
    ```bash
    pip install -r requirements.txt
    ```

3. Substitua `'your_api_key'` no código pela sua chave de API da OCR.Space.

4. Execute a aplicação:
    ```bash
    streamlit run app.py
    ```

5. Acesse a aplicação em seu navegador na URL: `http://localhost:8501`.

## Estrutura do Código

- **ocr_space_file(image)**: Função para realizar a requisição à API OCR.Space e retornar o texto extraído.
- **organize_data(text)**: Organiza os dados extraídos em um formato estruturado, relacionando alunos e seus status de presença.
- **create_table(weeks)**: Cria dinamicamente uma tabela no banco de dados SQLite com base nas semanas extraídas.
- **insert_into_db(data, weeks)**: Insere os dados organizados na tabela do banco de dados.
- **main()**: Função principal que inicia a aplicação Streamlit.

## Contribuições

Contribuições são bem-vindas! Se você quiser contribuir, por favor, siga estas etapas:

1. Fork o projeto.
2. Crie uma nova branch (`git checkout -b feature/nova_funcionalidade`).
3. Faça suas alterações e commit (`git commit -m 'Adiciona nova funcionalidade'`).
4. Envie para o branch (`git push origin feature/nova_funcionalidade`).
5. Abra um Pull Request.

## Licença

Este projeto é licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
