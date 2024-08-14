import os.path
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import mysql.connector

# Scopes e credenciais do Google Sheets API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = None

# Configurar credenciais
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("clinte.json", SCOPES)
        creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
        token.write(creds.to_json())

# Construir serviço Sheets API
service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId="1HEqQoV1RcuauuVZS0n_1sXnroAZNO7RN-UxiDx4Kxi8", range="Seg - Sexta!B6:F76").execute()
values = result.get("values", [])

# Conectar ao banco de dados MySQL
db_config = {
    'user': 'root',
    'password': '95175353Jo*',
    'host': '127.0.0.1',
    'database': 'lojas',
}

conn_mysql = mysql.connector.connect(**db_config)
conn_mysql_cursor = conn_mysql.cursor()

# Nome da tabela no banco de dados
table_name = "lojas_tabela"

# Criar a tabela se não existir
create_table_query = f"""
   CREATE TABLE IF NOT EXISTS {table_name} (
       id INT AUTO_INCREMENT PRIMARY KEY,
       numero_loja INT
   )
"""
conn_mysql_cursor.execute(create_table_query)

# Inserir os novos dados na tabela
numeros_inseridos = set()

for row in values:
    if row:
        # Filtrar apenas os números da linha
        numeros = [int(num) for num in re.findall(r'\d+', ' '.join(row))]

        # Armazenar os números no banco de dados
        for numero in numeros:
            if numero not in numeros_inseridos:
                conn_mysql_cursor.execute(
                    f"INSERT INTO {table_name} (numero_loja) VALUES (%s)",
                    (numero,)
                )
                numeros_inseridos.add(numero)

# Commit e fechar conexões
conn_mysql.commit()
conn_mysql_cursor.close()
conn_mysql.close()
