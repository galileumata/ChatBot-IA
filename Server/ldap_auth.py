# Importa as classes necessárias do módulo ldap3
from ldap3 import Server, Connection, SYNC, SUBTREE

# Define as informações de conexão LDAP
LDAP_SERVER = '192.168.10.100'  # Endereço IP do servidor LDAP
LDAP_BASE_DN = 'dc=seudominio,dc=local' # Base DN do domínio LDAP
LDAP_ADMIN_DN = 'cn=Administrador,cn=Users,dc=grupotcc,dc=local' # DN do administrador LDAP
LDAP_ADMIN_PASSWORD = 'senha_useradmin' # Senha do administrador LDAP

# Define uma função para autenticar um usuário no servidor LDAP
def authenticate_ldap(username, password):
    try:
        # Cria um objeto de servidor LDAP
        server = Server(LDAP_SERVER, get_info=SYNC)

        # Estabelece uma conexão com o servidor LDAP usando as credenciais do administrador
        conn = Connection(server, LDAP_ADMIN_DN, LDAP_ADMIN_PASSWORD, auto_bind=True)

        # Define um filtro de pesquisa LDAP com base no nome de usuário fornecido
        search_filter = f'(sAMAccountName={username})'

        # Realiza uma pesquisa no diretório LDAP usando o filtro especificado
        conn.search(LDAP_BASE_DN, search_filter, SUBTREE)

        # Verifica se a pesquisa retornou alguma entrada
        if not conn.entries:
            # Se não houver entradas correspondentes, significa que o usuário não foi encontrado
            conn.unbind()
            return False

        # Obtém o DN (Distinguished Name) do usuário encontrado
        user_dn = conn.entries[0].entry_dn

        # Tenta estabelecer uma nova conexão com o servidor LDAP usando as credenciais do usuário
        user_conn = Connection(server, user_dn, password, auto_bind=True)

        # Verifica se a conexão com o usuário foi bem-sucedida
        if user_conn.bound:
            # Se a conexão for bem-sucedida, o usuário é autenticado
            user_conn.unbind()
            conn.unbind()
            return True

        # Se a conexão falhar, o usuário não é autenticado
        conn.unbind()
        return False

    except Exception as e:
        # Se ocorrer algum erro durante o processo de autenticação, imprime o erro
        print(f'Erro de autenticação LDAP: {e}')
        return False
