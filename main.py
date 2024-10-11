import tkinter as tk
import socket
import struct

class Driver:
    def __init__(self, host_ip: str, port: int, unit_id: int = 1) -> None:
        self.host_ip = host_ip
        self.port = port
        self.unit_id = unit_id
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host_ip, self.port))

    def __create_message(self, transaction_id, function_code, address, value):
        protocol_id_modbus = 0
        length = 6
        header = struct.pack('>HHHB', transaction_id, protocol_id_modbus, length, self.unit_id)
        body = struct.pack('>BHH', function_code, address, value)
        return header + body

    def send_action_button(self, address: int, value: bool):
        try:
            modbus_value = 0xFF00 if value else 0x0000
            request = self.__create_message(1, 0x05, address, modbus_value)
            self.socket.sendall(request)

            response = self.socket.recv(1024)
            print(f"Tamanho da resposta: {len(response)} bytes")
            print(f"Resposta bruta: {response}")

            if len(response) < 9:
                raise ValueError("Resposta incompleta, verifique a conexão ou o dispositivo.")

            transacao, protocolo, tamanho, unidade = struct.unpack('>HHHB', response[:7])
            funcao = response[7]

            if funcao > 0x80:
                codigo_excecao = response[8]
                print(f"Erro Modbus: Função {hex(funcao)}, Código de exceção: {hex(codigo_excecao)}")
                if codigo_excecao == 0x02:
                    print("Exceção 0x02: Illegal Data Address. Verifique o endereço do coil.")
                return

            endereco, valor = struct.unpack('>HH', response[8:12])

            print(f"Transação: {transacao}, Protocolo: {protocolo}, Tamanho: {tamanho}, Unidade: {unidade}")
            print(f"Função: {funcao}, Endereço: {endereco}, Valor: {valor}")

            if funcao == 0x05 and endereco == address and valor == modbus_value:
                print(f"Coil {address} atualizado com sucesso.")
            else:
                print(f"Erro ao atualizar o coil {address}, verifique a resposta.")

        except Exception as e:
            print(f"Erro: {e}")

    def close_socket(self):
        self.socket.close()

class App:
    def __init__(self, root, driver):
        self.driver = driver
        
        # Configurar a janela principal
        self.root = root
        self.root.title("Controle de Coils via Modbus")

        # Criar 6 botões para os coils de 0 a 5
        for i in range(6):
            button = tk.Button(root, text=f"Pressionar Coil {i}", width=20, height=2, bg="blue", 
                               command=lambda i=i: self.push_button_action(i))
            button.pack(pady=10)

    def push_button_action(self, address):
        if address in [4, 5]:
            # Para os endereços 4 e 5, inverte a ordem: primeiro envia False, depois True
            self.driver.send_action_button(address, False)  # Enviar False primeiro
            # Esperar um curto período e depois enviar True
            self.root.after(200, lambda: self.driver.send_action_button(address, True))
        else:
            # Para os outros endereços, envia True primeiro
            self.driver.send_action_button(address, True)   
            # Esperar um curto período e depois enviar False
            self.root.after(200, lambda: self.driver.send_action_button(address, False))

    def on_closing(self):
        # Fechar o socket antes de sair
        self.driver.close_socket()
        self.root.destroy()

if __name__ == '__main__':
    # Criar driver para conexão Modbus
    driver = Driver('192.168.15.1', 502, 1)

    # Criar janela principal do tkinter
    root = tk.Tk()
    app = App(root, driver)

    # Detectar o fechamento da janela para encerrar o socket
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Iniciar a interface gráfica
    root.mainloop()
