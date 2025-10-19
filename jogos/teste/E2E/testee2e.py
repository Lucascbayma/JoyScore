from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install())

BASE_URL = "http://lcsbayma.pythonanywhere.com"

DELAY_PARA_VER = 1.5 

def configurar_driver():
    try:
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        wait = WebDriverWait(driver, 10)
        return driver, wait
    except Exception as e:
        print(f"ERRO CRÍTICO: Não foi possível iniciar o WebDriver: {e}")
        print("(Verifique se o Google Chrome está instalado no computador)")
        return None, None

def rodar_teste_login():
    print("--- Iniciando Teste de Login ---")
    driver, wait = configurar_driver()
    if driver is None: return

    try:
        driver.get(BASE_URL) 
        print("Página de login aberta")
        time.sleep(DELAY_PARA_VER) 
        USUARIO_REAL = "usuario_teste" 
        SENHA_REAL = "senha123"       

        username_field = wait.until(
            EC.visibility_of_element_located((By.NAME, "username"))
        )
        username_field.send_keys(USUARIO_REAL)
        print(f"Preencheu usuário: {USUARIO_REAL}")
        time.sleep(DELAY_PARA_VER) 
        
        driver.find_element(By.NAME, "password").send_keys(SENHA_REAL)
        print("Preencheu a senha")
        time.sleep(DELAY_PARA_VER) 
        
        submit_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit_button.click()
        print("Clicou em Login")
        
        wait.until(EC.url_contains("/dashboard"))
        print("Redirecionado para o Dashboard")
        time.sleep(DELAY_PARA_VER) 
        
        assert "/dashboard" in driver.current_url
        print(">>> Teste de Login: SUCESSO")

    except Exception as e:
        print(f"XXX Teste de Login: FALHOU XXX")
        print(f"Erro: {e}")
        time.sleep(2) 
    finally:
        print("--- Finalizando Teste de Login ---")
        driver.quit()

def rodar_teste_registro():
    print("\n--- Iniciando Teste de Registro ---")
    driver, wait = configurar_driver()
    if driver is None: return

    try:
        driver.get(BASE_URL) 
        print("Página de login aberta")
        time.sleep(DELAY_PARA_VER) 

        register_link = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Registre-se"))
        )
        register_link.click()
        print("Clicou em 'Registre-se'")

        wait.until(EC.url_contains("/registro"))
        print("Página de registro aberta")
        time.sleep(DELAY_PARA_VER) 
        
        unique_id = int(time.time())
        novo_usuario = f"teste_user_{unique_id}"
        novo_email = f"teste_{unique_id}@email.com"
        
        wait.until(EC.visibility_of_element_located((By.NAME, "username"))).send_keys(novo_usuario)
        print(f"Preencheu Apelido: {novo_usuario}")
        time.sleep(DELAY_PARA_VER * 0.5) 
        
        NOME_CAMPO_EMAIL = "email" 
        driver.find_element(By.NAME, NOME_CAMPO_EMAIL).send_keys(novo_email)
        print(f"Preencheu Email: {novo_email}")
        time.sleep(DELAY_PARA_VER * 0.5)

        driver.find_element(By.NAME, "password").send_keys("senha_teste123")
        print("Preencheu Senha")
        time.sleep(DELAY_PARA_VER * 0.5)

        NOME_CAMPO_CONFIRMACAO = "password2" 
        driver.find_element(By.NAME, NOME_CAMPO_CONFIRMACAO).send_keys("senha_teste123") 
        print("Preencheu Confirmação de Senha")
        time.sleep(DELAY_PARA_VER)

        submit_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit_button.click()
        print("Clicou em Inscrever-se")

        wait.until(EC.url_contains("/home"))
        print("Redirecionado para a Página Home")
        time.sleep(DELAY_PARA_VER) 
        
        assert "/home" in driver.current_url
        print(">>> Teste de Registro: SUCESSO")

    except Exception as e:
        print(f"XXX Teste de Registro: FALHOU XXX")
        print(f"Erro: {e}")
        time.sleep(2) 
    finally:
        print("--- Finalizando Teste de Registro ---")
        driver.quit()

if __name__ == "__main__":
    rodar_teste_login()
    rodar_teste_registro()
    print("\nTodos os testes foram executados.")