import os
import sys
import subprocess
import tempfile
import psutil
import json
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def is_admin():
    """Verifica se o script está sendo executado como administrador"""
    try:
        return os.geteuid() == 0  # Para sistemas Unix, mas no Windows precisamos de outra verificação
    except AttributeError:
        # Para sistemas Windows, tentamos verificar via subprocess
        try:
            result = subprocess.run(["net", "session"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
        except subprocess.SubprocessError:
            return False

def run_as_admin():
    """Tenta executar o script como administrador"""
    script = sys.argv[0]
    params = ' '.join(sys.argv[1:])
    cmd = f'python "{script}" {params}'

    # Usando subprocess para chamar a elevação
    try:
        subprocess.run(["runas", "/user:Administrator", cmd])
    except Exception as e:
        print(f"Erro ao tentar executar como administrador: {e}")

class Navigation:
    _driver = None
    _driver_service = None
    url = "https://servicexperience.satelitti.com.br/suite-new/auth/login"

    def kill_processes_by_name(self, process_name):
        """Função para matar processos pelo nome"""
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if process_name in proc.info['name'].lower():
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def start_edge(self, hide_cmd_window):
        """Inicia o Edge com as opções configuradas"""
        # Garantir que os processos do Edge sejam encerrados
        self.kill_processes_by_name('msedge')
        self.kill_processes_by_name('msedgewebview2')

        # Espera para garantir que o processo foi encerrado
        time.sleep(2)

        try:
            # Instalar automaticamente o driver do Edge
            driver_path = EdgeChromiumDriverManager().install()

            # Criar o serviço para o EdgeDriver
            self._driver_service = Service(driver_path)
            if hide_cmd_window:
                self._driver_service.creationflags = 0x08000000  # Ocultar a janela de comando

            # Criar um diretório temporário único para o perfil de usuário
            temp_dir = tempfile.mkdtemp(prefix="edge_profile_")

            # Configurar as opções do Edge
            options = Options()
            options.add_argument("--disable-extensions")  # Desabilitar extensões
            options.add_argument("--no-sandbox")  # Para evitar erros em algumas configurações
            options.add_argument("--disable-gpu")  # Desabilitar GPU para evitar erros gráficos
            options.add_argument("--disable-software-rasterizer")  # Evitar o uso de software rasterizer
            options.add_argument("--disable-accelerated-2d-canvas")  # Desabilitar aceleração de gráficos 2D
            options.add_argument("--disable-accelerated-3d-canvas")  # Desabilitar aceleração de gráficos 3D
            options.add_argument("--disable-gpu-compositing")  # Desabilitar composição gráfica usando GPU
            options.add_argument("--no-gl")  # Desabilitar OpenGL
            options.add_argument("disable-features=IdentityConsistency,Signin,Sync")  # Desabilitar sincronização de identidade
            options.add_argument("--disable-identity-consistency")
            options.add_argument("--disable-credentials-consistency")  # Desabilitar credenciais do sistema
            options.add_argument("--disable-login-redirect")  # Impedir redirecionamento de login
            options.add_argument("--no-auth-negotiate")  # Desabilitar autenticação negociada
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument(f"user-data-dir={temp_dir}")  # Garantir um novo diretório de perfil

            # Inicializar o WebDriver
            self._driver = webdriver.Edge(service=self._driver_service, options=options)

            # Navegar para a URL e esperar o carregamento do elemento de login
            self._driver.get(self.url)
            WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.ID, "id_do_elemento_de_login"))  # Troque pelo ID do seu elemento
            )
            time.sleep(30)

        except Exception as e:
            print("Erro ao iniciar o Edge: ", json.dumps(str(e)))

# Verificar se o script está sendo executado como administrador
if not is_admin():
    print("Não está executando como administrador. Tentando executar como administrador...")
    run_as_admin()  # Executar o script com privilégios elevados
else:
    # Exemplo de uso
    nav = Navigation()
    nav.start_edge(hide_cmd_window=True)  # Inicia o Edge com a configuração desejada
