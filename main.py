from flask import Flask, request, jsonify, render_template
import psycopg2
import webbrowser
import threading
import os

app = Flask(__name__)

# Configuração do banco de dados
DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST"),
    "port": os.environ.get("DB_PORT")
}

def executar_query(sql):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(sql)
        colunas = [desc[0] for desc in cur.description]
        dados = cur.fetchall()
        cur.close()
        conn.close()
        return {"colunas": colunas, "dados": dados}
    except Exception as e:
        return {"erro": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/executar', methods=['POST'])
def executar():
    sql = request.json.get("query")
    resultado = executar_query(sql)
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


index_html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Query Executor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body class="container mt-5">
    <h2 class="mb-4">Executar Query SQL</h2>
    <textarea id="query" class="form-control" rows="4" placeholder="Digite sua query SQL..."></textarea>
    <button id="executar" class="btn btn-primary mt-3">Executar</button>
    
    <h3 class="mt-4">Resultado</h3>
    <div id="resultado" class="mt-3"></div>
    
    <script>
        $(document).ready(function() {
            $('#executar').click(function() {
                let query = $('#query').val();
                $.ajax({
                    url: '/executar',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ query: query }),
                    success: function(response) {
                        if (response.erro) {
                            $('#resultado').html('<div class="alert alert-danger">' + response.erro + '</div>');
                        } else {
                            let tabela = '<div class="table-responsive"><table class="table table-bordered table-striped table-hover">';
                            tabela += '<thead class="table-dark"><tr>';
                            response.colunas.forEach(coluna => {
                                tabela += '<th>' + coluna + '</th>';
                            });
                            tabela += '</tr></thead><tbody>';
                            response.dados.forEach(linha => {
                                tabela += '<tr>';
                                linha.forEach(valor => {
                                    tabela += '<td>' + valor + '</td>';
                                });
                                tabela += '</tr>';
                            });
                            tabela += '</tbody></table></div>';
                            $('#resultado').html(tabela);
                        }
                    }
                });
            });
        });
    </script>
</body>
</html>
"""

# Criando o arquivo index.html
with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(index_html)
