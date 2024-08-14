from flask import Flask, render_template, request
import csv
from io import StringIO

app = Flask(__name__)

def processar_csv(file):
    try:
        conteudo_csv = file.stream.read().decode('utf-8')
        csv_reader = csv.DictReader(StringIO(conteudo_csv), delimiter=';')

        linhas_em_execucao = []
        linhas_finalizadas = []
        lojas_em_execucao_set = set()
        lojas_finalizadas_set = set()
        borda_vermelha = False  # Flag para indicar borda vermelha

        for linha in csv_reader:
            trun_resultado = linha.get('trun_resultado', '')
            lojas = linha.get('lojas', '')
            trun_codigo = linha.get('trun_codigo', '')

            if trun_resultado == 'Em execucao':
                if not any(lojas in l.get('lojas', '') and 'Finalizado com sucesso' in l.get('trun_resultado', '') for l in linhas_finalizadas):
                    linhas_em_execucao.append({'lojas': lojas, 'trun_codigo': trun_codigo, 'nome': linha.get('nome', '')})
                    lojas_em_execucao_set.add(lojas)

            if len(linhas_em_execucao) == 1 and lojas in lojas_em_execucao_set and not any(lojas in l.get('lojas', '') and 'Finalizado com sucesso' in l.get('trun_resultado', '') for l in linhas_finalizadas):
                borda_vermelha = True


            elif trun_resultado == 'Finalizado com sucesso':
                linhas_finalizadas.append({'lojas': lojas, 'trun_codigo': trun_codigo, 'nome': linha.get('nome', '')})
                lojas_finalizadas_set.add(lojas)

        return {
            'linhas_em_execucao': linhas_em_execucao,
            'linhas_finalizadas': linhas_finalizadas,
            'lojas_em_execucao_set': lojas_em_execucao_set,
            'lojas_finalizadas_set': lojas_finalizadas_set,
            'mensagem': 'TODO PROCESSO CORRETO' if not linhas_em_execucao else None,
            'borda_vermelha': borda_vermelha  # Passa a flag para o HTML
        }

    except csv.Error as e:
        return {
            'erro': f"Erro ao processar o arquivo CSV: {e}"
        }
    except Exception as e:
        return {
            'erro': f"Ocorreu um erro inesperado: {e}"
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    informacoes_csv = None

    if request.method == 'POST':
        csv_file = request.files['csv_file']
        informacoes_csv = processar_csv(csv_file)

    return render_template('index.html', informacoes_csv=informacoes_csv)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

