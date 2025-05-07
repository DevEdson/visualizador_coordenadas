import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class Navigation:
    url = "https://servicexperience.satelitti.com.br/suite-new/auth/login"

    def start_chrome(self):
        # Configurar opções do Chrome
        options = Options()
        options.add_argument("--disable-features=ChromeIdentity")
        options.add_argument("--start-maximized")

        # Criar serviço para o ChromeDriver
        service = Service(ChromeDriverManager().install())
        service.creationflags = 0x08000000  # Oculta a janela de comando

        # Iniciar o Chrome
        driver = webdriver.Chrome(service=service, options=options)
        
        # Navegar para a URL
        driver.get(self.url)

        # Delay de 5 segundos antes de fechar
        time.sleep(5)

        # Fecha o navegador
        driver.quit()


# Exemplo de uso
nav = Navigation()
nav.start_chrome()
