# Importa o conector MySQL para interagir com o banco de dados MariaDB e função de hash bcrypt para segurança de senha
import mysql.connector
from passlib.hash import bcrypt

# Configuração do banco de dados MariaDB
db_config = {
    'host': 'localhost',  # Host onde o banco de dados está localizado
    'user': 'username',   # Nome de usuário para acessar o banco de dados
    'password': 'senha_DB',  # Senha para acessar o banco de dados
    'database': 'nome_database',  # Nome do banco de dados
}

# Função para inicializar o banco de dados criando uma tabela para armazenar mensagens
def init_database():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Criação da tabela para armazenar as mensagens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender VARCHAR(255),
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# Função para salvar uma mensagem no banco de dados
def save_message(sender, content):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Insere a mensagem na tabela
    cursor.execute('INSERT INTO messages (sender, content) VALUES (%s, %s)', (sender, content))

    conn.commit()
    conn.close()

# Função para recuperar mensagens do banco de dados
def retrieve_messages():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Seleciona todas as mensagens da tabela ordenadas pelo timestamp
    cursor.execute('SELECT sender, content, timestamp FROM messages ORDER BY timestamp')

    # Recupera todas as mensagens
    messages = cursor.fetchall()

    conn.close()

    return messages

# Função para gerar o hash da senha usando bcrypt
def hash_password(password):
    return bcrypt.hash(password)

# Função para verificar se a senha fornecida corresponde à senha armazenada
def verify_password(hashed_password, password):
    return bcrypt.verify(password, hashed_password)
