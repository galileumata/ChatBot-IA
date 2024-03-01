# Importa as bibliotecas necessárias
import threading
import socket
import logging
from database import init_database, save_message  # Importa funções relacionadas ao banco de dados
from ldap_auth import authenticate_ldap  # Importa a função de autenticação LDAP

# Configurações do servidor
SERVER_ADDRESS = ('192.168.10.101', 7777)  # Endereço IP e porta do servidor
MESSAGE_BUFFER_SIZE = 2048  # Tamanho do buffer para mensagens
USERNAME_BUFFER_SIZE = 1024  # Tamanho do buffer para nomes de usuário

# Configuração do registro de log
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Classe principal do servidor de chat
class ChatServer:
    def __init__(self):
        # Dicionário para armazenar informações sobre as salas de chat
        self.rooms = {room: {'clients': [], 'messages': []} for room in ['RH', 'Financeiro', 'TI']}
        
        # Configuração do socket do servidor
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(SERVER_ADDRESS)
        self.server_socket.listen()
        
        # Inicialização do banco de dados
        init_database()
        print("Servidor de chat iniciado. Aguardando conexões...\n")

    # Método para executar o servidor
    def run(self):
        while True:
            try:
                client, addr = self.server_socket.accept()  # Aceita novas conexões dos clientes
                logging.info(f"Novo cliente conectado: {addr[0]}:{addr[1]}")
                threading.Thread(target=self.handle_client, args=(client,)).start()  # Inicia uma nova thread para lidar com o cliente
            except Exception as e:
                logging.error(f"Erro durante a conexão do cliente: {e}")

    # Método para lidar com um cliente
    def handle_client(self, client):
        try:
            # Recebe o nome de usuário e senha do cliente para autenticação
            username = client.recv(USERNAME_BUFFER_SIZE).decode('utf-8')
            password = client.recv(USERNAME_BUFFER_SIZE).decode('utf-8')

            # Autentica o cliente usando o servidor LDAP
            if authenticate_ldap(username, password):
                client.send("Autenticado com sucesso. Bem-vindo ao chat.".encode('utf-8'))
                self.send_available_rooms(client)  # Envia as salas de chat disponíveis para o cliente
                room_choice = self.select_client_room(client)  # Permite que o cliente escolha uma sala
                if room_choice:
                    self.rooms[room_choice]['clients'].append(client)  # Adiciona o cliente à sala escolhida
                    self.listen_client_messages(client, username)  # Escuta as mensagens do cliente
                else:
                    client.send("Sala inválida. Desconectado.".encode('utf-8'))
                    client.close()
            else:
                logging.warning("Falha na autenticação. Cliente desconectado.")
                client.send("Falha na autenticação. Desconectado.".encode('utf-8'))
                client.close()
        except Exception as e:
            logging.error(f"Erro durante a conexão do cliente: {e}")

    # Método para escutar as mensagens de um cliente
    def listen_client_messages(self, client, username):
        while True:
            try:
                msg = client.recv(MESSAGE_BUFFER_SIZE).decode('utf-8')  # Recebe a mensagem do cliente
                if not msg:
                    break

                client_room = self.get_client_room(client)  # Obtém a sala do cliente

                if msg.strip():
                    save_message(username, msg)  # Salva a mensagem no banco de dados
                    self.broadcast(client_room, f"{username}: {msg}", client)  # Envia a mensagem para os outros clientes na sala
            except Exception as e:
                logging.error(f"Erro durante o tratamento da mensagem: {e}")
                break
        self.delete_client(client)  # Remove o cliente da sala quando a conexão é encerrada

    # Método para permitir que o cliente escolha uma sala
    def select_client_room(self, client):
        while True:
            room_choice = client.recv(USERNAME_BUFFER_SIZE).decode('utf-8').strip()
            if room_choice in self.rooms:
                return room_choice
            else:
                client.send("Sala inválida. Tente novamente.".encode('utf-8'))

    # Método para enviar as salas de chat disponíveis para o cliente
    def send_available_rooms(self, client):
        rooms_string = ", ".join(self.rooms.keys())
        client.send(f"{rooms_string}".encode('utf-8'))

    # Método para enviar uma mensagem para todos os clientes em uma sala específica
    def broadcast(self, room, message, sender_client):
        for client in self.rooms[room]['clients']:
            if client != sender_client:
                try:
                    client.send(message.encode('utf-8'))
                except Exception as e:
                    logging.error(f"Erro durante a transmissão da mensagem: {e}")
                    self.delete_client(client)

    # Método para remover um cliente de uma sala
    def delete_client(self, client):
        try:
            client_room = self.get_client_room(client)
            if client_room:
                self.rooms[client_room]['clients'].remove(client)
                logging.info(f"Cliente desconectado: {client.getpeername()[0]}:{client.getpeername()[1]}")
                disconnected_message = f"O cliente {client.getpeername()[0]}:{client.getpeername()[1]} desconectou."
                self.broadcast(client_room, disconnected_message, client)
                client.close()
        except Exception as e:
            logging.error(f"Erro ao remover cliente: {e}")

    # Método para obter a sala de um cliente
    def get_client_room(self, client):
        for room, data in self.rooms.items():
            if client in data['clients']:
                return room
        return None

# Ponto de entrada do programa
if __name__ == "__main__":
    server = ChatServer()
    server.run()
