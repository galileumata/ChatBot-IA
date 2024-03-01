# Importa as bibliotecas necessárias
import threading
import socket
import sys
import getpass

# Classe principal do atendente de chat
class ChatAtendente:
    def __init__(self):
        self.SERVER_HOST = '192.168.10.101'  # Endereço IP do servidor
        self.SERVER_PORT = 7777  # Porta do servidor

    # Método para iniciar o atendente
    def run(self):
        self.connect_to_conventional_chat()

    # Método para conectar-se a um chat convencional
    def connect_to_conventional_chat(self):
        print("Atendimento")
        print("Efetue o login.\n")

        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.SERVER_HOST, self.SERVER_PORT))  # Conecta ao servidor
        except Exception as e:
            print(f'\nNão foi possível conectar ao servidor: {e}\n')
            return

        self.authenticate()

    # Método para autenticar o atendente
    def authenticate(self):
        username = input('Digite seu nome de usuário: ')
        password = getpass.getpass('Digite sua senha: ')

        # Envia primeiro o nome de usuário e depois a senha para autenticação
        self.client.send(username.encode('utf-8'))
        self.client.send(password.encode('utf-8'))

        try:
            response = self.client.recv(1024).decode('utf-8')
        except ConnectionResetError:
            print('\nConexão encerrada pelo servidor.\n')
            sys.exit()

        if response == "Autenticado com sucesso. Bem-vindo ao chat.":
            print('\nConectado')
            self.show_available_rooms()
        else:
            print(response)
            self.client.close()

    # Método para mostrar as salas de chat disponíveis
    def show_available_rooms(self):
        rooms = self.receive_available_rooms()
        print("Salas disponíveis:\n")
        for idx, room in enumerate(rooms):
            print(f"{idx + 1}. {room}")

        while True:
            room_choice = input("Digite o nome da sala: ")
            if room_choice in rooms:
                self.client.send(room_choice.encode('utf-8'))
                break
            else:
                print("Sala inválida. Tente novamente.")

        # Inicia threads para receber e enviar mensagens
        thread1 = threading.Thread(target=self.receive_messages)
        thread2 = threading.Thread(target=self.send_messages)

        thread1.start()
        thread2.start()

    # Método para receber as salas de chat disponíveis do servidor
    def receive_available_rooms(self):
        try:
            rooms_data = self.client.recv(1024).decode('utf-8')
            rooms = rooms_data.split(', ')
            return rooms
        except ConnectionResetError:
            print('\nConexão encerrada pelo servidor.\n')
            sys.exit()

    # Método para receber mensagens do servidor
    def receive_messages(self):
        while True:
            try:
                msg = self.client.recv(2048).decode('utf-8')
                print(msg+'\n')
            except ConnectionResetError:
                print('\nConexão encerrada pelo servidor.\n')
                sys.exit()

    # Método para enviar mensagens para o servidor
    def send_messages(self):
        while True:
            try:
                msg = input('\n')
                self.client.send(msg.encode('utf-8'))
            except ConnectionResetError:
                print('\nConexão encerrada pelo servidor.\n')
                sys.exit()

# Ponto de entrada do programa
if __name__ == "__main__":
    chat_atendente = ChatAtendente()
    chat_atendente.run()
