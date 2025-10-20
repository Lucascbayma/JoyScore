import time
from selenium import webdriver
from selenium.webdriver.common.by import By
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

def rodar_teste_login(driver, wait):
    print("--- Iniciando Teste de Login ---")

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

def rodar_teste_registro(driver, wait):
    print("\n--- Iniciando Teste de Registro ---")

    try:
        driver.get(BASE_URL) 
        print("Página de login aberta (para ir ao registro)")
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

def rodar_teste_filtro(driver, wait):
    print("\n--- Iniciando Teste de Filtro de Gêneros ---")
    try:
        print("Página principal (com filtro) aberta")
        time.sleep(DELAY_PARA_VER)

        filtro_link = wait.until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Filtrar Gêneros"))
        )
        
        print("Clicando em 'Filtrar Gêneros'")
        filtro_link.click()

        wait.until(EC.url_contains("/filtrar"))
        print("Redirecionado para a página de filtro")
        time.sleep(DELAY_PARA_VER)
        
        assert "/filtrar" in driver.current_url
        print(">>> Teste de Filtro: SUCESSO")

    except Exception as e:
        print(f"XXX Teste de Filtro: FALHOU XXX")
        print(f"Erro: {e}")
        time.sleep(2)
    finally:
        print("--- Finalizando Teste de Filtro ---")
def rodar_teste_aplicar_filtro(driver, wait):
    print("\n--- Iniciando Teste de Aplicação de Filtro ---")
    try:
        print("Página de filtro aberta")
        time.sleep(DELAY_PARA_VER) 
        
        label_action_locator = (By.XPATH, "//label[normalize-space()='Action']")
        label_action = wait.until(EC.visibility_of_element_located(label_action_locator))
        driver.execute_script("arguments[0].click();", label_action)
        print("Selecionou o gênero 'Action' (via JS)")
        time.sleep(0.5) 

        label_indie_locator = (By.XPATH, "//label[normalize-space()='Indie']")
        label_indie = wait.until(EC.visibility_of_element_located(label_indie_locator))
        driver.execute_script("arguments[0].click();", label_indie)
        print("Selecionou o gênero 'Indie' (via JS)")
        
        time.sleep(1) 

        button_locator = (By.CSS_SELECTOR, "button.filter-button")
        
        print("Procurando o botão 'Filtrar Jogos' (com seletor button.filter-button)...")
        submit_button = wait.until(EC.element_to_be_clickable(button_locator))
        
        print("Clicando em 'Filtrar Jogos' (via JS)")
        driver.execute_script("arguments[0].click();", submit_button)

        print("Aguardando carregamento da página de resultados...")
        wait.until(EC.url_contains("genres="))
        print("Página de resultados do filtro carregada")
        time.sleep(DELAY_PARA_VER)

        assert "genres=" in driver.current_url
        print(">>> Teste de Aplicação de Filtro: SUCESSO")

    except Exception as e:
        print(f"XXX Teste de Aplicação de Filtro: FALHOU XXX")
        print(f"Erro: {e}")
        time.sleep(2)
    finally:
        print("--- Finalizando Teste de Aplicação de Filtro ---")

if __name__ == "__main__":
    print("=== Iniciando Suíte de Testes ===")
    
    driver, wait = configurar_driver() 
    
    if driver:
        try:
            rodar_teste_login(driver, wait)
            rodar_teste_registro(driver, wait)
            rodar_teste_filtro(driver, wait)
            rodar_teste_aplicar_filtro(driver, wait)
            
            print("\nTodos os testes foram executados.")
            print("O navegador permanecerá aberto por mais 5 segundos...")
            time.sleep(5) 

        except Exception as e:
            print(f"XXX Um erro crítico interrompeu a suíte de testes: {e}")
        finally:
            print("=== Finalizando Suíte de Testes ===")
            driver.quit()
    else:
        print("Testes não executados devido à falha ao iniciar o WebDriver.")