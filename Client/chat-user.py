# Importa as bibliotecas necessárias
import threading
import socket
import sys
import requests
import getpass

# Classe principal do cliente de chat
class ChatClient:
    def __init__(self):
        self.openai_api_key = 'seu_token_api' # Token da API OpenAI
        self.SERVER_HOST = '192.168.10.101' # Endereço IP do servidor host da aplicação 
        self.SERVER_PORT = 7777 # Porta do servidor
        self.last_question = "" # Armazena a última pergunta feita pelo usuário

    # Método para iniciar o cliente
    def run(self):
        self.interact_with_chatbot()

    # Método para interagir com o chatbot
    def interact_with_chatbot(self):
        print("Você está conectado como CLIENTE e está falando com CHATBOT!")
        print("APENAS DIGA O PROBLEMA NO QUAL ESTÁ ENFRENTANDO")
        print("------------------ EM ATENDIMENTO ------------------\n")

        while True:
            try:
                user_input = input("\nVocê: ")

                # Verifica se o usuário deseja falar com um agente humano
                if self.wants_to_talk_to_agent(user_input):
                    print("\nHmm, percebo que você quer falar com um agente. Vou direcionar você para o atendente.\n")
                    print("\nDigite seu usuário de rede para conversar com um agente.\n")
                    self.connect_to_conventional_chat()
                    break

                if user_input.lower() == self.last_question.lower():
                    print("\nHmm, percebo que não estou ajudando. Vou direcionar você para o atendente.\n")
                    print("\nDigite seu usuário de rede para conversar com um agente.\n")
                    self.connect_to_conventional_chat()
                    break
                else:
                    self.last_question = user_input

                # Faz uma solicitação à API OpenAI para obter uma resposta do chatbot
                response = self.openai_request(user_input)
                print(f'\nChatbot: {response} \nCaso as dicas acima não funcione, digite: "Falar com atendente"')
                
            except KeyboardInterrupt:
                print("\nEncerrando o chatbot...")
                sys.exit()
            except Exception as e:
                print(f"Ocorreu um erro ao interagir com o chatbot: {e}")

    # Método para verificar se o usuário deseja falar com um agente humano
    def wants_to_talk_to_agent(self, user_input):
        agent_keywords = ["agente", "atendente", "falar com alguém", "falar com humano", "quero falar com suporte tecnico", "eu quero falar com", "eu quero falar",
                          "quero falar", "quero falar com"]
        for keyword in agent_keywords:
            if keyword in user_input.lower():
                return True
        return False

    # Método para fazer uma solicitação à API OpenAI
    def openai_request(self, prompt):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    # Método para conectar-se a um chat convencional com um agente humano
    def connect_to_conventional_chat(self):
        print("Conectando ao servidor...")

        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.SERVER_HOST, self.SERVER_PORT))
        except Exception as e:
            print(f'\nNão foi possível conectar ao servidor: {e}\n')
            return

        self.authenticate()

    # Método para autenticar o cliente
    def authenticate(self):
        username = input('Digite seu nome de usuário: ')
        password = getpass.getpass('Digite sua senha: ')

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
    chat_client = ChatClient()
    chat_client.run()
