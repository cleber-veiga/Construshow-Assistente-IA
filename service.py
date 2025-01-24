import signal
import sys
import threading
import time
from waitress import serve
from app import create_the_application
from config import loger, conf

class ViasoftServerConstruShowIA:
    def __init__(self):
        self.running = True
        self.host = conf.get_server_config()['server_host']
        self.port = conf.get_server_config()['server_port']
        self.server_thread = None

    def run_flask_application(self):
        """
        Função para iniciar o servidor Flask usando Waitress em uma thread separada.
        """
        try:
            loger.log('DEBUG', 'Iniciando a criação do app')
            app = create_the_application()

            # Servir o Flask usando Waitress
            serve(app, host=self.host, port=self.port)
        except Exception as e:
            loger.log('ERROR', f'Erro ao iniciar o servidor serviço: {e}')
        finally:
            loger.log('WARNING', 'Serviço interrompido')

    def start_server_thread(self):
        """
        Inicia o servidor em uma thread separada.
        """
        self.server_thread = threading.Thread(target=self.run_flask_application, daemon=True)
        self.server_thread.start()
        loger.log('DEBUG', 'Servidor iniciado em uma thread separada.')

    def monitor(self):
        """
        Monitoramento do serviço principal.
        """
        try:
            while self.running:
                time.sleep(5)
        except KeyboardInterrupt:
            loger.log('WARNING', 'Interrupção manual recebida. Encerrando serviço...')
            self.stop()

    def stop(self):
        """
        Encerra o serviço e aguarda o término da thread do servidor.
        """
        loger.log('DEBUG', 'Encerrando o serviço...')
        self.running = False

        if self.server_thread and self.server_thread.is_alive():
            loger.log('DEBUG', 'Aguardando o término da thread do servidor...')
            # Espera por um tempo definido e força o encerramento se necessário
            self.server_thread.join(timeout=5)

        # Força o encerramento do programa se a thread não finalizar
        if self.server_thread and self.server_thread.is_alive():
            loger.log('ERROR', 'A thread do servidor não foi encerrada. Forçando o término do programa.')
            import os
            os._exit(0)

        loger.log('INFO', 'Serviço encerrado com sucesso.')

    def start(self):
        """
        Inicia o serviço completo, incluindo o servidor e o monitoramento.
        """
        try:
            loger.log('DEBUG', 'Serviço sendo inicializado')

            # Captura o sinal SIGTERM para encerramento seguro
            signal.signal(signal.SIGTERM, lambda sig, frame: self.stop())

            # Inicia o servidor em uma thread separada
            self.start_server_thread()

            # Monitoramento do serviço
            self.monitor()

        except SystemExit:
            loger.log('INFO', 'Serviço finalizado com segurança.')
        except Exception as e:
            loger.log('ERROR', f'Erro inesperado na inicialização do serviço: {e}')
        finally:
            self.stop()


# Início do script
if __name__ == '__main__':
    server = ViasoftServerConstruShowIA()

    # Verifica se foi iniciado em modo de depuração
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        loger.log('DEBUG', 'Executando em modo de depuração (sem serviço do Windows)')
        try:
            def signal_handler(sig, frame):
                loger.log('DEBUG', 'Interrupção recebida. Encerrando o modo de depuração.')
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            server.start_server_thread()
            server.monitor()
        except Exception as e:
            loger.log('ERROR', f'Erro ao iniciar aplicação: {e}')
    else:
        loger.log('DEBUG', 'Executando como serviço via NSSM.')
        server.start()
