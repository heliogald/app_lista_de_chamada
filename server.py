import streamlit as st
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/chamadas', methods=['POST'])
def receive_call_data():
    data = request.json
    chamada_info = data.get('dados_chamada')

    if chamada_info:
        st.write(f"Dados da chamada recebidos: {chamada_info}")
        return jsonify({'status': 'sucesso', 'message': 'Dados recebidos com sucesso!'}), 200
    else:
        return jsonify({'status': 'erro', 'message': 'Nenhum dado foi enviado!'}), 400

# Roda o servidor Flask embutido no Streamlit
def run():
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    from werkzeug.serving import run_simple

    app.wsgi_app = DispatcherMiddleware(st, {"/api": app})
    run_simple('0.0.0.0', 8501, app)

if __name__ == '__main__':
    run()
