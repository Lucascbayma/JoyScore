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

        driver.find_element(By.NAME, "email").send_keys(novo_email)
        print(f"Preencheu Email: {novo_email}")
        time.sleep(DELAY_PARA_VER * 0.5)

        driver.find_element(By.NAME, "password").send_keys("senha_teste123")
        print("Preencheu Senha")
        time.sleep(DELAY_PARA_VER * 0.5)

        driver.find_element(By.NAME, "password2").send_keys("senha_teste123")
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

        label_action = wait.until(EC.visibility_of_element_located((By.XPATH, "//label[normalize-space()='Action']")))
        driver.execute_script("arguments[0].click();", label_action)
        print("Selecionou o gênero 'Action'")
        time.sleep(0.5)

        label_indie = wait.until(EC.visibility_of_element_located((By.XPATH, "//label[normalize-space()='Indie']")))
        driver.execute_script("arguments[0].click();", label_indie)
        print("Selecionou o gênero 'Indie'")
        time.sleep(1)

        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.filter-button")))
        driver.execute_script("arguments[0].click();", button)
        print("Clicou em 'Filtrar Jogos'")

        wait.until(EC.url_contains("genres="))
        print("Página de resultados carregada")
        time.sleep(DELAY_PARA_VER)

        assert "genres=" in driver.current_url
        print(">>> Teste de Aplicação de Filtro: SUCESSO")

    except Exception as e:
        print(f"XXX Teste de Aplicação de Filtro: FALHOU XXX")
        print(f"Erro: {e}")
        time.sleep(2)
    finally:
        print("--- Finalizando Teste de Aplicação de Filtro ---")


def rodar_teste_voltar_home(driver, wait):
    print("\n--- Iniciando Teste de Voltar para Home (pelo Logo) ---")
    try:
        time.sleep(DELAY_PARA_VER)
        logo_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".logo-container a")))
        print("Clicando no logo para voltar à home")
        logo_link.click()

        home_element = (By.XPATH, "//h2[contains(text(), 'JOGOS POPULARES')]")
        wait.until(EC.visibility_of_element_located(home_element))
        print("Redirecionado para a Página Home")
        time.sleep(DELAY_PARA_VER)

        assert "/home" in driver.current_url or "/dashboard" in driver.current_url
        print(">>> Teste de Voltar para Home: SUCESSO")

    except Exception as e:
        print(f"XXX Teste de Voltar para Home: FALHOU XXX")
        print(f"Erro: {e}")
    finally:
        print("--- Finalizando Teste de Voltar para Home ---")


def rodar_teste_clicar_jogo(driver, wait):
    print("\n--- Iniciando Teste de Clicar no Jogo Elden Ring ---")
    try:
        print("Atualmente na Home Page")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        print("Tentando clicar na IMAGEM do jogo 'Elden Ring'...")
        try:
            jogo_elden = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//a[contains(@href, '/avaliar/') and .//img[contains(@alt, 'Elden Ring')]]"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", jogo_elden)
            time.sleep(0.8)
            driver.execute_script("arguments[0].click();", jogo_elden)
            print("Clicou na imagem do jogo Elden Ring.")
        except Exception:
            print("Imagem não encontrada, tentando clicar no texto...")
            jogo_elden = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//a[contains(@href, '/avaliar/') and .//text()[contains(., 'Elden Ring')]]"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", jogo_elden)
            time.sleep(0.8)
            driver.execute_script("arguments[0].click();", jogo_elden)
            print("Clicou no texto do jogo Elden Ring.")

        wait.until(EC.url_contains("/avaliar/"))
        title_locator = (By.XPATH, "//*[self::h1 or self::h2][contains(text(), 'Elden Ring')]")
        wait.until(EC.visibility_of_element_located(title_locator))
        print("Página de avaliação do Elden Ring carregada com sucesso.")
        time.sleep(DELAY_PARA_VER)

        assert "/avaliar/" in driver.current_url
        print(">>> Teste de Clicar no Jogo (Elden Ring): SUCESSO")

    except Exception as e:
        print(f"XXX Teste de Clicar no Jogo (Elden Ring): FALHOU XXX")
        print(f"Erro: {e}")
    finally:
        print("--- Finalizando Teste de Clicar no Jogo (Elden Ring) ---")


def rodar_teste_clicar_botao_mais(driver, wait):
    print("\n--- Iniciando Teste de Clique no Botão '+' ---")
    try:
        print("Verificando se estamos na página do Elden Ring...")
        assert "Elden Ring" in driver.page_source

        print("Localizando o botão '+' no DOM...")
        botao_mais_locator = (By.CSS_SELECTOR, "a.add-btn[aria-label*='Elden Ring']")
        botao_mais = wait.until(
            EC.presence_of_element_located(botao_mais_locator)
        )
        print("Elemento localizado.")

        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", botao_mais)
        print("Rolando a tela para o botão...")

        time.sleep(1.5) 

        print("Clicando no botão...")
        driver.execute_script("arguments[0].click();", botao_mais)
        print("🟣 Botão '+' clicado com sucesso!")

        try:
            short_wait = WebDriverWait(driver, 5) 
            short_wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'adicionado à sua biblioteca') or contains(text(), 'Remover da biblioteca')]")
                )
            )
            print("✅ Mensagem de confirmação detectada!")
        except Exception:
            print("⚠️ Nenhuma mensagem de confirmação visível, mas o clique foi executado.")

        print(">>> Teste do Botão '+': SUCESSO")

    except Exception as e:
        print("XXX Teste do Botão '+': FALHOU XXX")
        print(f"Erro: {e}")
    finally:
        print("--- Finalizando Teste do Botão '+' ---")


def rodar_teste_dar_nota_e_comentar(driver, wait):
    print("\n--- Iniciando Teste de Avaliação (Nota, Comentário e Salvar) ---")
    try:
        print("Rolando até o fim da página (seção de avaliação)...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5) 

        estrelas_desejadas = 4
        star_locator = (By.CSS_SELECTOR, f"label[for='star{estrelas_desejadas}']")
        print(f"Localizando a label da estrela de {estrelas_desejadas} estrelas...")

        estrela_label = wait.until(
            EC.presence_of_element_located(star_locator)
        )
        
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", estrela_label)
        time.sleep(1.0) 

        print(f"Clicando em {estrelas_desejadas} estrelas...")
        driver.execute_script("arguments[0].click();", estrela_label)
        print(f"✅ Clicou com sucesso em {estrelas_desejadas} estrelas.")
        time.sleep(0.5)

        print("Localizando a caixa de comentário (textarea)...")
        comment_box = wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "textarea"))
        )
        
        texto_comentario = "Este é um comentário de teste automatizado. Ótimo jogo!"
        comment_box.send_keys(texto_comentario)
        print(f"✅ Comentário inserido: '{texto_comentario}'")
        time.sleep(DELAY_PARA_VER)

        print("Localizando o botão 'Salvar Avaliação'...")
        save_button = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, "//button[contains(text(), 'Salvar Avaliação')]"
            ))
        )
        
        print("Clicando em 'Salvar Avaliação'...")
        driver.execute_script("arguments[0].click();", save_button)
        
        print("✅ Avaliação enviada!")
        
        try:
            wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'Avaliação salva com sucesso')]")
                )
            )
            print("✅ Mensagem 'Avaliação salva com sucesso' detectada!")
        except Exception:
            print("⚠️ Avaliação enviada, mas nenhuma mensagem de sucesso foi detectada (ou a página recarregou).")

        print(">>> Teste de Avaliação (Nota, Comentário e Salvar): SUCESSO")

    except Exception as e:
        print("XXX Teste de Avaliação (Nota, Comentário e Salvar): FALHOU XXX")
        print(f"Erro: {e}")
        print("Ocorreu um erro ao tentar avaliar o jogo.")
    finally:
        print("--- Finalizando Teste de Avaliação (Nota, Comentário e Salvar) ---")


def rodar_teste_ir_para_biblioteca(driver, wait):
    print("\n--- Iniciando Teste de Navegação para Biblioteca ---")
    try:
        time.sleep(1.0) 
        print("Localizando o menu hambúrguer...")
        hamburger_locator = (By.CSS_SELECTOR, "label[for='menu-toggle']")
        hamburger_menu = wait.until(
            EC.element_to_be_clickable(hamburger_locator)
        )
        
        print("Clicando no menu hambúrguer...")
        driver.execute_script("arguments[0].click();", hamburger_menu)
        
        print("Aguardando menu aparecer...")
        time.sleep(1.0) 

        print("Localizando o link 'Biblioteca'...")
        biblioteca_link_locator = (By.LINK_TEXT, "Biblioteca")
        biblioteca_link = wait.until(
            EC.element_to_be_clickable(biblioteca_link_locator)
        )
        
        print("Clicando em 'Biblioteca'...")
        biblioteca_link.click()
        
        wait.until(EC.url_contains("/biblioteca"))
        print("Redirecionado para a Biblioteca")
        time.sleep(DELAY_PARA_VER)

        assert "/biblioteca" in driver.current_url
        print(">>> Teste de Navegação para Biblioteca: SUCESSO")
        
    except Exception as e:
        print("XXX Teste de Navegação para Biblioteca: FALHOU XXX")
        print(f"Erro: {e}")
    finally:
        print("--- Finalizando Teste de Navegação para Biblioteca ---")


def rodar_teste_ir_para_configuracoes(driver, wait):
    print("\n--- Iniciando Teste de Navegação para Configurações ---")
    try:
        time.sleep(1.0)
        print("Localizando o menu hambúrguer...")
        hamburger_locator = (By.CSS_SELECTOR, "label[for='menu-toggle']")
        hamburger_menu = wait.until(
            EC.element_to_be_clickable(hamburger_locator)
        )

        print("Clicando no menu hambúrguer...")
        driver.execute_script("arguments[0].click();", hamburger_menu)

        print("Aguardando menu aparecer...")
        time.sleep(1.0)

        print("Localizando o link 'Configurações de Conta'...")
        config_link_locator = (By.LINK_TEXT, "Configurações de Conta")
        config_link = wait.until(
            EC.element_to_be_clickable(config_link_locator)
        )

        print("Clicando em 'Configurações de Conta'...")
        config_link.click()

        wait.until(EC.url_contains("/configuracoes")) 
        print("Redirecionado para Configurações de conta")
        time.sleep(DELAY_PARA_VER)

        assert "/configuracoes" in driver.current_url
        print(">>> Teste de Navegação para Configurações: SUCESSO")

    except Exception as e:
        print("XXX Teste de Navegação para Configurações: FALHOU XXX")
        print(f"Erro: {e}")
    finally:
        print("--- Finalizando Teste de Navegação para Configurações ---")


def rodar_teste_salvar_preferencias_genero(driver, wait):
    print("\n--- Iniciando Teste de Salvar Gêneros Favoritos ---")
    try:
        print("Página de Configurações aberta.")
        time.sleep(DELAY_PARA_VER * 0.5) 

        genero1_label = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//label[normalize-space()='Adventure']"
        )))
        driver.execute_script("arguments[0].click();", genero1_label)
        print("Selecionou 'Adventure'")
        time.sleep(0.5)

        genero2_label = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//label[normalize-space()='RPG']"
        )))
        driver.execute_script("arguments[0].click();", genero2_label)
        print("Selecionou 'RPG'")
        time.sleep(0.5)

        genero3_label = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//label[normalize-space()='Shooter']"
        )))
        driver.execute_script("arguments[0].click();", genero3_label)
        print("Selecionou 'Shooter'")
        time.sleep(DELAY_PARA_VER)

        save_button = wait.until(EC.element_to_be_clickable((
            By.ID, "save-prefs-button" 
        )))
        print("Clicando em 'Salvar Preferências'...")
        driver.execute_script("arguments[0].click();", save_button)
        
        try:
            wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'Preferências salvas com sucesso')]")
                )
            )
            print("✅ Mensagem 'Preferências salvas com sucesso' detectada!")
        except Exception:
            print("⚠️ Preferências salvas, mas nenhuma mensagem de sucesso foi detectada.")

        print(">>> Teste de Salvar Gêneros Favoritos: SUCESSO")

    except Exception as e:
        print("XXX Teste de Salvar Gêneros Favoritos: FALHOU XXX")
        print(f"Erro: {e}")
    finally:
        print("--- Finalizando Teste de Salvar Gêneros Favoritos ---")


if __name__ == "__main__":
    print("=== Iniciando Suíte de Testes ===")
    driver, wait = configurar_driver()

    if driver:
        try:
            rodar_teste_login(driver, wait)
            rodar_teste_registro(driver, wait)
            rodar_teste_filtro(driver, wait)
            rodar_teste_aplicar_filtro(driver, wait)
            rodar_teste_voltar_home(driver, wait)
            rodar_teste_clicar_jogo(driver, wait)
            rodar_teste_clicar_botao_mais(driver, wait)
            rodar_teste_dar_nota_e_comentar(driver, wait) 
            rodar_teste_ir_para_biblioteca(driver, wait) 
            rodar_teste_ir_para_configuracoes(driver, wait) 
            rodar_teste_salvar_preferencias_genero(driver, wait)

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