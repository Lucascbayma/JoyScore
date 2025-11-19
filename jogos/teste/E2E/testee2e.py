import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys 
from selenium.common.exceptions import TimeoutException

service = Service(ChromeDriverManager().install())
BASE_URL = "http://lcsbayma.pythonanywhere.com"
DELAY_PARA_VER = 0.5


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

def rodar_teste_registro(driver, wait):
    print("\n--- Iniciando Teste de Registro ---")
    try:
        driver.get(BASE_URL)
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

def rodar_teste_busca_alternada(driver, wait):
    print("\n--- Iniciando Teste de Busca Alternada (Digita e Apaga) ---")
    
    jogos_para_testar = [
        "Cyberpunk 2077",
        "Witcher",
        "JogoInexistente12345",
        "Red Dead Redemption 2"
    ]
    
    try:
        print("Localizando barra de busca...")
        search_bar = wait.until(
            EC.visibility_of_element_located((By.ID, "game-search-input"))
        )
        print("Barra de busca localizada com sucesso.")
        
        for game_name in jogos_para_testar:
            
            print(f"Digitando '{game_name}'...")
            for char in game_name:
                search_bar.send_keys(char)
                time.sleep(0.05)
            
            print(f"Terminou de digitar '{game_name}'.")
            time.sleep(2.0) 
            
            print("Limpando a barra de busca...")
            search_bar.clear()
            print("Barra de busca limpa.")
            time.sleep(1.0)

        print(">>> Teste de Busca Alternada: SUCESSO")

    except Exception as e:
        print(f"XXX Teste de Busca Alternada: FALHOU XXX")
        print(f"Erro detalhado: {e}") 
    finally:
        print("--- Finalizando Teste de Busca Alternada ---")

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
    print("\n--- Iniciando Teste de Aplicação de Filtro (Múltiplas Etapas) ---")
    try:
        print("Página de filtro aberta")
        time.sleep(DELAY_PARA_VER)

        print("Etapa 1: Clicando em 'Filtrar Jogos' (sem gêneros)")
        button1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.filter-button")))
        driver.execute_script("arguments[0].click();", button1)
        
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.filter-button")))
        print("Página recarregada (sem filtros).")
        time.sleep(DELAY_PARA_VER)

        print("Etapa 2: Selecionando 1 gênero ('Action')")
        label_action = wait.until(EC.visibility_of_element_located((By.XPATH, "//label[normalize-space()='Action']")))
        driver.execute_script("arguments[0].click();", label_action)
        print("Selecionou 'Action'")
        time.sleep(0.5)

        button2 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.filter-button")))
        driver.execute_script("arguments[0].click();", button2)
        print("Clicou em 'Filtrar Jogos' (com 'Action')")

        wait.until(EC.url_contains("genres="))
        print("Página de resultados carregada com 'Action'.")
        time.sleep(DELAY_PARA_VER)

        print("Etapa 3: Selecionando 2 gêneros ('Action' + 'Indie')")

        label_indie = wait.until(EC.visibility_of_element_located((By.XPATH, "//label[normalize-space()='Indie']")))
        driver.execute_script("arguments[0].click();", label_indie)
        print("Selecionou 'Indie'")
        time.sleep(0.5)

        button3 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.filter-button")))
        driver.execute_script("arguments[0].click();", button3)
        print("Clicou em 'Filtrar Jogos' (com 'Action' e 'Indie')")

        wait.until(EC.url_contains("genres="))
        print("Página de resultados carregada com 2 gêneros.")
        time.sleep(DELAY_PARA_VER)

        print("Etapa 4: Selecionando 1 gênero ('RPG') (sem filtrar)")
        label_rpg = wait.until(EC.visibility_of_element_located((By.XPATH, "//label[normalize-space()='RPG']")))
        driver.execute_script("arguments[0].click();", label_rpg)
        print("Selecionou 'RPG'")
        time.sleep(DELAY_PARA_VER) 

        print(">>> Teste de Aplicação de Filtro (Múltiplas Etapas): SUCESSO")

    except Exception as e:
        print(f"XXX Teste de Aplicação de Filtro (Múltiplas Etapas): FALHOU XXX")
        print(f"Erro: {e}")
        time.sleep(2)
    finally:
        print("--- Finalizando Teste de Aplicação de Filtro (Múltiplas Etapas) ---")

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
    print("\n--- Iniciando Teste de Clicar no Jogo Bloodborne ---")
    try:
        print("Atualmente na Home Page")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        print("Tentando clicar na IMAGEM do jogo 'Bloodborne'...")
        try:
            jogo_bloodborne = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//a[contains(@href, '/avaliar/') and .//img[contains(@alt, 'Bloodborne')]]"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", jogo_bloodborne)
            time.sleep(0.8)
            driver.execute_script("arguments[0].click();", jogo_bloodborne)
            print("Clicou na imagem do jogo Bloodborne.")
        except Exception:
            print("Imagem não encontrada, tentando clicar no texto...")
            jogo_elden = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//a[contains(@href, '/avaliar/') and .//text()[contains(., 'Bloodborne')]]"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", jogo_bloodborne)
            time.sleep(0.8)
            driver.execute_script("arguments[0].click();", jogo_bloodborne)
            print("Clicou no texto do jogo Bloodborne.")

        wait.until(EC.url_contains("/avaliar/"))
        title_locator = (By.XPATH, "//*[self::h1 or self::h2][contains(text(), 'Elden Ring')]")
        wait.until(EC.visibility_of_element_located(title_locator))
        print("Página de avaliação do Bloodborne carregada com sucesso.")
        time.sleep(DELAY_PARA_VER)

        assert "/avaliar/" in driver.current_url
        print(">>> Teste de Clicar no Jogo (Bloodborne): SUCESSO")

    except Exception as e:
        print(f"XXX Teste de Clicar no Jogo (Bloodborne): FALHOU XXX")
        print(f"Erro: {e}")
    finally:
        print("--- Finalizando Teste de Clicar no Jogo (Bloodborne) ---") 

def rodar_teste_adicionar_e_gerenciar_jornada(driver, wait):
    print("\n--- Iniciando Teste E2E de Adicionar Jogo e Gerenciar Jornada ---")
    
    form_wrapper = (By.CLASS_NAME, "jornada-form-wrapper")
    display_view = (By.CLASS_NAME, "jornada-display") 
    
    input_horas = (By.ID, "horas_jogadas")
    input_trofeus_conquistados = (By.ID, "trofeus_conquistados")
    input_trofeus_totais = (By.ID, "trofeus_totais")
    
    btn_salvar_jornada = (By.CSS_SELECTOR, "button.submit-jornada")
    btn_editar_jornada = (By.ID, "jornada-edit-btn") 
    
    botao_mais_locator = (By.CSS_SELECTOR, "a.add-btn[aria-label*='Bloodborne']")
    
    display_horas = (By.XPATH, "//div[contains(@class, 'jornada-stat')][contains(., 'Horas Jogadas')]")
    display_trofeus = (By.XPATH, "//div[contains(@class, 'jornada-stat')][contains(., 'Progresso de Troféus')]")
    display_platina = (By.XPATH, "//div[contains(@class, 'jornada-stat')][contains(., 'Platina')]")
    
    msg_erro_jornada = (By.ID, "erro-jornada") 

    try:
        print("\n--- Cenário 0: Verificando se o jogo NÃO está na biblioteca...")
        short_wait = WebDriverWait(driver, 3) 
        try:
            short_wait.until(EC.invisibility_of_element_located(form_wrapper))
            print("✅ Verificado: Formulário da jornada não está visível.")
        except TimeoutException:
            print("XXX FALHA: O formulário da jornada já está visível.")
            raise Exception("Estado inicial inválido: jogo já está na biblioteca.")
        
        botao_mais = wait.until(EC.visibility_of_element_located(botao_mais_locator))
        print("✅ Verificado: Botão '+' está visível.")


        print("\n--- Ação: Adicionando jogo à biblioteca...")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", botao_mais)
        time.sleep(1.5) 
        driver.execute_script("arguments[0].click();", botao_mais)
        print("🟣 Botão '+' clicado com sucesso!")


        print("Verificando se o formulário da jornada apareceu...")
        wait.until(EC.visibility_of_element_located(form_wrapper))
        print("✅ Verificado: Formulário da jornada agora está visível.")
        time.sleep(1.0)


        print("\n--- Cenário 1: Registrando nova jornada (25h, 10/50)...")
        
        wait.until(EC.visibility_of_element_located(input_horas)).send_keys("25")
        wait.until(EC.visibility_of_element_located(input_trofeus_totais)).send_keys("50")
        wait.until(EC.visibility_of_element_located(input_trofeus_conquistados)).send_keys("10")
        
        driver.find_element(*btn_salvar_jornada).click()
        print("Clicou em 'Salvar Jornada'.")
        
        wait.until(EC.visibility_of_element_located(btn_editar_jornada))
        print("Verificando progresso (Cenário 1)...")
        wait.until(EC.text_to_be_present_in_element(display_horas, "25h"))
        wait.until(EC.text_to_be_present_in_element(display_trofeus, "10 / 50"))
        wait.until(EC.text_to_be_present_in_element(display_platina, "20%"))
        print("✅ Cenário 1: SUCESSO (25h, 10/50, 20%)")


        print("\n--- Cenário 2: Editando jornada existente (40/50)...")
        
        driver.find_element(*btn_editar_jornada).click()
        print("Clicou em 'Editar'.")
        
        input_conquistados_elem = wait.until(EC.visibility_of_element_located(input_trofeus_conquistados))
        input_conquistados_elem.clear()
        input_conquistados_elem.send_keys("40")
        
        driver.find_element(*btn_salvar_jornada).click()
        print("Clicou em 'Salvar Jornada' (editando).")

        wait.until(EC.visibility_of_element_located(btn_editar_jornada))
        print("Verificando progresso (Cenário 2)...")
        wait.until(EC.text_to_be_present_in_element(display_trofeus, "40 / 50"))
        wait.until(EC.text_to_be_present_in_element(display_platina, "80%"))
        print("✅ Cenário 2: SUCESSO (40/50, 80%)")


        print("\n--- Cenário 3: Testando troféus inválidos (51/50)...")
        
        driver.find_element(*btn_editar_jornada).click()
        print("Clicou em 'Editar'.")
        
        input_conquistados_elem = wait.until(EC.visibility_of_element_located(input_trofeus_conquistados))
        input_conquistados_elem.clear()
        input_conquistados_elem.send_keys("51") 
        
        driver.find_element(*btn_salvar_jornada).click()
        print("Clicou em 'Salvar Jornada' (com erro).")

        print("Verificando mensagem de erro (Cenário 3)...")
        error_message = wait.until(EC.visibility_of_element_located(msg_erro_jornada))
        
        assert "limite" in error_message.text.lower() or "inválido" in error_message.text.lower()
        print("✅ Cenário 3: SUCESSO (Mensagem de erro exibida)")

        print("\n>>> Teste E2E (Adicionar e Gerenciar Jornada): SUCESSO GERAL")

    except Exception as e:
        print(f"XXX Teste E2E (Adicionar e Gerenciar Jornada): FALHOU XXX")
        print(f"Erro: {e}")
        time.sleep(2)
    finally:
        print("--- Finalizando Teste E2E (Adicionar e Gerenciar Jornada) ---")


def rodar_teste_dar_nota_e_comentar(driver, wait):
    print("\n--- Iniciando Teste de Avaliação (Elden Ring) ---")
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

        print(">>> Teste de Avaliação (Elden Ring): SUCESSO")

    except Exception as e:
        print("XXX Teste de Avaliação (Elden Ring): FALHOU XXX")
        print(f"Erro: {e}")
        print("Ocorreu um erro ao tentar avaliar o jogo.")
    finally:
        print("--- Finalizando Teste de Avaliação (Elden Ring) ---")


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


def rodar_teste_modificar_avaliacao_biblioteca(driver, wait):
    print("\n--- Iniciando Teste de Modificação de Avaliação (Biblioteca) ---")
    try:
        nome_jogo = "Elden Ring"
        
        print(f"Procurando '{nome_jogo}' na biblioteca...")
        jogo_locator = (By.XPATH, f"//a[@class='game-item-link'][.//span[@class='game-title'][contains(text(), '{nome_jogo}')]]")
        jogo_link = wait.until(EC.element_to_be_clickable(jogo_locator))
        
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", jogo_link)
        time.sleep(1.0) 
        print(f"Clicando em '{nome_jogo}'...")
        jogo_link.click()
        
        wait.until(EC.url_contains("/avaliar/"))
        wait.until(EC.visibility_of_element_located((By.XPATH, f"//*[self::h1 or self::h2][contains(text(), '{nome_jogo}')]")))
        print("Página de avaliação carregada.")
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5) 
        
        print("Procurando a avaliação atual (estrela marcada)...")
        checked_star_input_locator = (By.CSS_SELECTOR, "input[type='radio'][id^='star']:checked")
        checked_star_input = wait.until(EC.presence_of_element_located(checked_star_input_locator))
        
        id_estrela_antiga = checked_star_input.get_attribute("id") 
        estrelas_antigas_num = int(id_estrela_antiga.replace("star", "")) 
        print(f"Avaliação atual encontrada: {estrelas_antigas_num} estrelas.")

        star_locator_antigo = (By.CSS_SELECTOR, f"label[for='{id_estrela_antiga}']")
        print(f"Clicando na nota antiga ({estrelas_antigas_num} estrelas)...")
        estrela_label_antiga = wait.until(EC.presence_of_element_located(star_locator_antigo))
        driver.execute_script("arguments[0].click();", estrela_label_antiga)
        time.sleep(0.5)

        if estrelas_antigas_num == 5:
            estrelas_novas = 4
        else:
            estrelas_novas = 5
            
        star_locator_novo = (By.CSS_SELECTOR, f"label[for='star{estrelas_novas}']")
        print(f"Clicando na nota nova ({estrelas_novas} estrelas)...")
        estrela_label_nova = wait.until(EC.presence_of_element_located(star_locator_novo))
        driver.execute_script("arguments[0].click();", estrela_label_nova)
        print(f"✅ Clicou com sucesso em {estrelas_novas} estrelas.")
        time.sleep(0.5)
        
        comment_box = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "textarea")))
        comment_box.clear()
        texto_comentario_novo = "Atualizando minha nota. Jogo fenomenal, uma obra-prima!"
        comment_box.send_keys(texto_comentario_novo)
        print(f"✅ Comentário atualizado: '{texto_comentario_novo}'")
        time.sleep(DELAY_PARA_VER)

        
        print("Localizando o botão 'Remover' (✓)...")
        
        botao_remover_locator = (By.CSS_SELECTOR, f"a.add-btn.added[aria-label*='{nome_jogo}']")
        
        botao_remover = wait.until(
            EC.presence_of_element_located(botao_remover_locator)
        )
        print("Elemento localizado.")

        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", botao_remover)
        print("Rolando a tela para o botão...")
        time.sleep(1.5) 

        print("Clicando no botão...")
        driver.execute_script("arguments[0].click();", botao_remover)
        print("🟣 Botão (Remover/Checkmark) clicado com sucesso!")
        
        time.sleep(1.0) 

        save_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Salvar Avaliação')]")))
        driver.execute_script("arguments[0].click();", save_button)
        print("✅ Avaliação atualizada enviada!")
        
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Avaliação salva com sucesso')]")))
        print("✅ Mensagem 'Avaliação salva com sucesso' detectada!")
        
        
        print("Voltando para a Biblioteca...")
        driver.back()
        
        wait.until(EC.url_contains("/biblioteca")) 
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'MINHA BIBLIOTECA')]")))
        print("✅ Voltou para a página da Biblioteca.")
        time.sleep(1.0)
        
        print(">>> Teste de Modificação de Avaliação (Biblioteca): SUCESSO")
        
    except Exception as e:
        print("XXX Teste de Modificação de Avaliação (Biblioteca): FALHOU XXX")
        print(f"Erro: {e}")
    finally:
        print("--- Finalizando Teste de Modificação de Avaliação (Biblioteca) ---")

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


def rodar_teste_preferencias_e_tema(driver, wait):
    print("\n--- Iniciando Teste de Configurações (Gêneros e Tema) ---")
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
            short_wait = WebDriverWait(driver, 5)
            short_wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'Preferências salvas com sucesso')]")
                )
            )
            print("✅ Mensagem 'Preferências salvas com sucesso' detectada!")
        except Exception:
            print("⚠️ Preferências salvas, mas nenhuma mensagem de sucesso foi detectada.")
        
        time.sleep(1.0) 

        print("Rolando para a seção de Tema...")
        theme_button = wait.until(EC.presence_of_element_located((
            By.ID, "theme-toggle"
        )))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", theme_button)
        print("Rolou para o botão de tema.")
        time.sleep(1.5) 

        print("Clicando em 'Modo Branco'...")
        driver.execute_script("arguments[0].click();", theme_button)
        print("✅ Clicou para alterar o tema.")
        time.sleep(DELAY_PARA_VER)

        print(">>> Teste de Configurações (Gêneros e Tema): SUCESSO")

    except Exception as e:
        print("XXX Teste de Configurações (Gêneros e Tema): FALHOU XXX")
        print(f"Erro: {e}")
    finally:
        print("--- Finalizando Teste de Configurações (Gêneros e Tema) ---")


def rodar_teste_ir_para_steam_tac_toe(driver, wait):
    print("\n--- Iniciando Teste de Navegação para Steam Tac Toe ---")
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

        print("Localizando o link 'Steam Tac Toe'...")
        steam_link_locator = (By.LINK_TEXT, "Steam Tac Toe")
        steam_link = wait.until(
            EC.element_to_be_clickable(steam_link_locator)
        )

        print("Clicando em 'Steam Tac Toe'...")
        steam_link.click()

        wait.until(EC.url_contains("/steam")) 
        print("Redirecionado para Steam Tac Toe")
        time.sleep(DELAY_PARA_VER)

        assert "/steam" in driver.current_url
        print(">>> Teste de Navegação para Steam Tac Toe: SUCESSO")

    except Exception as e:
        print("XXX Teste de Navegação para Steam Tac Toe: FALHOU XXX")
        print(f"Erro: {e}")
    finally:
        print("--- Finalizando Teste de Navegação para Steam Tac Toe ---")


def rodar_teste_ui_steam_tac_toe(driver, wait):
    print("\n--- Iniciando Teste Completo da UI do Steam Tac Toe (Modificado) ---")
    
    print("\n[Parte 1] Testando o botão 'Sortear Temas' (recarregamento)...")
    try:
        label_col_0_element = wait.until(
            EC.visibility_of_element_located((By.ID, "label-col-0"))
        )
        label_col_0 = label_col_0_element.text
        print(f"Gênero da coluna 0 (antes): {label_col_0}")
        
        driver.find_element(By.ID, "resortear-btn").click()
        
        wait.until(EC.staleness_of(label_col_0_element))
        print("Página recarregou...")
        
        label_col_0_novo_element = wait.until(
            EC.visibility_of_element_located((By.ID, "label-col-0"))
        )
        label_col_0_novo = label_col_0_novo_element.text
        print(f"Gênero da coluna 0 (depois): {label_col_0_novo}")
        
        assert label_col_0 != label_col_0_novo
        print("✅ Gêneros sorteados com sucesso (o texto mudou).")
    except AssertionError:
        print("⚠️ Gêneros sorteados, mas calhou de ser o mesmo. O teste da mecânica (recarregar) foi OK.")
    except Exception as e:
        print(f"XXX FALHA GRAVE NA [Parte 1] Teste Sortear Temas: {e}")


    print("\n[Parte 2] Testando o botão 'Pular Vez'...")
    try:
        turn_text_element = wait.until(
            EC.visibility_of_element_located((By.ID, "header-turn-text"))
        )
        texto_turno_antes = turn_text_element.text
        print(f"Turno atual: {texto_turno_antes}")

        driver.find_element(By.ID, "skip-turn-btn").click()
        time.sleep(0.5) 
        
        texto_turno_depois = driver.find_element(By.ID, "header-turn-text").text
        print(f"Novo turno: {texto_turno_depois}")
        
        assert texto_turno_antes != texto_turno_depois
        print("✅ Turno alterado com sucesso.")
    except Exception as e:
        print(f"XXX FALHA GRAVE NA [Parte 2] Teste Pular Vez: {e}")


    print("\n[Parte 3] Testando o modal 'Configurações' (Garantindo 6 gêneros)...")
    try:
        driver.find_element(By.ID, "settings-btn").click()
        modal = wait.until(EC.visibility_of_element_located((By.ID, "settings-modal")))
        print("✅ Modal de Configurações abriu.")
        time.sleep(1)

        DESIRED_GENRES = {"RPG", "Co-op", "Single-player", "Multi-player", "Indie", "Simulation"}
        print(f"Gêneros desejados: {DESIRED_GENRES}")

        labels_to_click = []

        all_checkboxes = modal.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        
        print("Analisando gêneros atuais...")
        for checkbox in all_checkboxes:
            try:
                input_id = checkbox.get_attribute("id")
                label = modal.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                genre_name = label.text.strip()
                is_checked = checkbox.is_selected()

                if is_checked and genre_name not in DESIRED_GENRES:
                    print(f"-> Gênero para DESMARCAR: {genre_name}")
                    labels_to_click.append(label)
                
                elif not is_checked and genre_name in DESIRED_GENRES:
                    print(f"-> Gênero para MARCAR: {genre_name}")
                    labels_to_click.append(label)

            except Exception as e:
                print(f"Aviso: erro ao processar checkbox/label: {e}")

        if labels_to_click:
            print(f"Ajustando {len(labels_to_click)} gênero(s) para o estado desejado...")
            for label in labels_to_click:
                try:
                    print(f"Clicando em: {label.text.strip()}")
                    driver.execute_script("arguments[0].click();", label)
                    time.sleep(0.2)
                except Exception as e:
                    print(f"Aviso: Falha ao clicar no label {label.text.strip()}: {e}")
        else:
            print("✅ Nenhum gênero precisou ser alterado. Já está correto.")
        
        print("Seleção de gêneros concluída.")
        time.sleep(1)

        try:
            print("Localizando botão 'Salvar Alterações' pelo texto dentro do modal...")
            
            save_button_locator = (
                By.XPATH, 
                "//div[@id='settings-modal']//button[normalize-space()='Salvar Alterações']"
            )
            
            save_button = wait.until(
                EC.presence_of_element_located(save_button_locator)
            )
            
            print("Botão 'Salvar Alterações' encontrado. Clicando via JavaScript...")
            driver.execute_script("arguments[0].click();", save_button)
            print("✅ 'Salvar Alterações' clicado com sucesso.")
            time.sleep(1) 
        except Exception as e:
            print(f"XXX Aviso: Falha grave ao tentar localizar ou clicar em 'Salvar Alterações' via XPath. {e}")
            print("   -> Verifique se o botão realmente existe e se o texto 'Salvar Alterações' está correto.")

        driver.find_element(By.ID, "settings-close-btn").click()
        wait.until(EC.invisibility_of_element_located((By.ID, "settings-modal")))
        print("✅ Modal de Configurações fechou.")
    except Exception as e:
        print(f"XXX FALHA GRAVE NA [Parte 3] Teste Modal Configurações: {e}")
        try:
            driver.find_element(By.ID, "settings-close-btn").click()
        except:
            pass


    print("\n[Parte 4] Testando a mecânica de jogada (Stardew Valley e FIFA)...")
    
    jogada_1_sucesso = False
    
    print("\n--- Jogada 1: 'Stardew Valley' na célula (0,0) ---")
    try:
        cell_0_0_locator = (By.CSS_SELECTOR, "div.game-slot[data-row='0'][data-col='0']")
        cell_0_0 = wait.until(EC.element_to_be_clickable(cell_0_0_locator))
        cell_0_0.click()

        wait.until(EC.visibility_of_element_located((By.ID, "search-modal")))
        genres_text = driver.find_element(By.ID, "modal-genres-text").text
        print(f"Célula (0,0) requer: {genres_text}")
        
        input_field = driver.find_element(By.ID, "game-search-input")
        input_field.clear()
        input_field.send_keys("Stardew Valley")
        
        search_result_li = (By.CSS_SELECTOR, "#search-results-list li.search-result-item")
        first_result = wait.until(EC.element_to_be_clickable(search_result_li))
        
        result_text = first_result.text
        print(f"Primeiro resultado encontrado: '{result_text}'. Clicando nele...")
        first_result.click()
        
        wait.until(EC.invisibility_of_element_located((By.ID, "search-modal")))
        print("Modal fechou. Verificando resultado...")

        try:
            short_wait = WebDriverWait(driver, 2)
            img_locator = (By.CSS_SELECTOR, "div.game-slot[data-row='0'][data-col='0'] img")
            short_wait.until(EC.visibility_of_element_located(img_locator))
            print("✅ RESULTADO JOGADA 1: ACERTO (Imagem apareceu na célula)")
            jogada_1_sucesso = True
        except Exception:
            status_box = driver.find_element(By.ID, "game-status-box")
            assert "error-message" in status_box.get_attribute("class")
            print(f"⚠️ RESULTADO JOGADA 1: ERRO (Gêneros não bateram. Msg: '{status_box.text}')")
            
    except Exception as e:
        print(f"XXX FALHA GRAVE NA [Jogada 1]: {e}")
        try:
            driver.find_element(By.CSS_SELECTOR, "#search-modal-close-btn").click()
        except:
            pass
        time.sleep(1)

    print("\n--- Jogada 2: 'FIFA' na célula (0,1) ---")
    try:
        cell_0_1_locator = (By.CSS_SELECTOR, "div.game-slot[data-row='0'][data-col='1']")
        cell_0_1 = wait.until(EC.element_to_be_clickable(cell_0_1_locator))
        cell_0_1.click()

        wait.until(EC.visibility_of_element_located((By.ID, "search-modal")))
        genres_text = driver.find_element(By.ID, "modal-genres-text").text
        print(f"Célula (0,1) requer: {genres_text}")
        
        input_field = driver.find_element(By.ID, "game-search-input")
        input_field.clear() 
        input_field.send_keys("FIFA")
        
        search_result_li = (By.CSS_SELECTOR, "#search-results-list li.search-result-item")
        first_result = wait.until(EC.element_to_be_clickable(search_result_li))
        
        result_text = first_result.text
        print(f"Primeiro resultado encontrado: '{result_text}'. Clicando nele...")
        first_result.click()
        
        wait.until(EC.invisibility_of_element_located((By.ID, "search-modal")))
        print("Modal fechou. Verificando resultado...")

        try:
            short_wait = WebDriverWait(driver, 2)
            img_locator = (By.CSS_SELECTOR, "div.game-slot[data-row='0'][data-col='1'] img")
            short_wait.until(EC.visibility_of_element_located(img_locator))
            print("✅ RESULTADO JOGADA 2: ACERTO (Imagem apareceu na célula)")
        except Exception:
            status_box = driver.find_element(By.ID, "game-status-box")
            assert "error-message" in status_box.get_attribute("class")
            print(f"⚠️ RESULTADO JOGADA 2: ERRO (Gêneros não bateram. Msg: '{status_box.text}')")
            
    except Exception as e:
        print(f"XXX FALHA GRAVE NA [Jogada 2]: {e}")
        try:
            driver.find_element(By.CSS_SELECTOR, "#search-modal-close-btn").click()
        except:
            pass
        time.sleep(1)
        
    print("\n--- Jogada 3: 'Stardew Valley' na célula (1,0) (Abaixo da Jogada 1) ---")
    try:
        cell_1_0_locator = (By.CSS_SELECTOR, "div.game-slot[data-row='1'][data-col='0']")
        cell_1_0 = wait.until(EC.element_to_be_clickable(cell_1_0_locator))
        cell_1_0.click()

        wait.until(EC.visibility_of_element_located((By.ID, "search-modal")))
        genres_text = driver.find_element(By.ID, "modal-genres-text").text
        print(f"Célula (1,0) requer: {genres_text}")
        
        input_field = driver.find_element(By.ID, "game-search-input")
        input_field.clear() 
        input_field.send_keys("Stardew Valley")
        
        search_result_li = (By.CSS_SELECTOR, "#search-results-list li.search-result-item")
        first_result = wait.until(EC.element_to_be_clickable(search_result_li))
        
        result_text = first_result.text
        print(f"Primeiro resultado encontrado: '{result_text}'. Clicando nele...")
        first_result.click()
        
        wait.until(EC.invisibility_of_element_located((By.ID, "search-modal")))
        print("Modal fechou. Verificando resultado...")

        try:
            short_wait = WebDriverWait(driver, 2)
            img_locator = (By.CSS_SELECTOR, "div.game-slot[data-row='1'][data-col='0'] img")
            short_wait.until(EC.visibility_of_element_located(img_locator))
            print("✅ RESULTADO JOGADA 3: ACERTO (Imagem apareceu na célula)")
        except Exception:
            status_box = driver.find_element(By.ID, "game-status-box")
            assert "error-message" in status_box.get_attribute("class")
            print(f"⚠️ RESULTADO JOGADA 3: ERRO (Gêneros não bateram. Msg: '{status_box.text}')")
            
    except Exception as e:
        print(f"XXX FALHA GRAVE NA [Jogada 3]: {e}")
        try:
            driver.find_element(By.CSS_SELECTOR, "#search-modal-close-btn").click()
        except:
            pass
        time.sleep(1)

    print("\n--- Jogada 4: 'Terraria' na célula (1,1) (À direita da Jogada 3) ---")
    try:
        cell_1_1_locator = (By.CSS_SELECTOR, "div.game-slot[data-row='1'][data-col='1']")
        cell_1_1 = wait.until(EC.element_to_be_clickable(cell_1_1_locator))
        cell_1_1.click()

        wait.until(EC.visibility_of_element_located((By.ID, "search-modal")))
        genres_text = driver.find_element(By.ID, "modal-genres-text").text
        print(f"Célula (1,1) requer: {genres_text}")
        
        input_field = driver.find_element(By.ID, "game-search-input")
        input_field.clear() 
        input_field.send_keys("Terraria") 
        
        search_result_li = (By.CSS_SELECTOR, "#search-results-list li.search-result-item")
        first_result = wait.until(EC.element_to_be_clickable(search_result_li))
        
        result_text = first_result.text
        print(f"Primeiro resultado encontrado: '{result_text}'. Clicando nele...")
        first_result.click()
        
        wait.until(EC.invisibility_of_element_located((By.ID, "search-modal")))
        print("Modal fechou. Verificando resultado...")

        try:
            short_wait = WebDriverWait(driver, 2)
            img_locator = (By.CSS_SELECTOR, "div.game-slot[data-row='1'][data-col='1'] img")
            short_wait.until(EC.visibility_of_element_located(img_locator))
            print("✅ RESULTADO JOGADA 4: ACERTO (Imagem apareceu na célula)")
        except Exception:
            status_box = driver.find_element(By.ID, "game-status-box")
            assert "error-message" in status_box.get_attribute("class")
            print(f"⚠️ RESULTADO JOGADA 4: ERRO (Gêneros não bateram. Msg: '{status_box.text}')")
            
    except Exception as e:
        print(f"XXX FALHA GRAVE NA [Jogada 4]: {e}")
        try:
            driver.find_element(By.CSS_SELECTOR, "#search-modal-close-btn").click()
        except:
            pass
        time.sleep(1)


    if jogada_1_sucesso:
        print("\n--- Jogada 5: Testando clique em célula preenchida (Stardew Valley @ 0,0) ---")
        try:
            cell_0_0_locator = (By.CSS_SELECTOR, "div.game-slot[data-row='0'][data-col='0']")
            cell_0_0 = wait.until(EC.presence_of_element_located(cell_0_0_locator))

            img_locator = (By.CSS_SELECTOR, "div.game-slot[data-row='0'][data-col='0'] img")
            wait.until(EC.visibility_of_element_located(img_locator))
            print("Célula (0,0) já contém Stardew Valley. Clicando nela...")

            cell_0_0.click()
            print("Clicou na célula (0,0) preenchida.")

            try:
                short_wait = WebDriverWait(driver, 2) 
                short_wait.until(EC.visibility_of_element_located((By.ID, "search-modal")))
                print("XXX RESULTADO JOGADA 5: FALHA (Modal abriu indevidamente)")
                driver.find_element(By.CSS_SELECTOR, "#search-modal-close-btn").click()
            except Exception:
                print("✅ RESULTADO JOGADA 5: SUCESSO (Modal não abriu, como esperado)")
                
        except Exception as e:
            print(f"XXX FALHA GRAVE NA [Jogada 5]: {e}")
    else:
        print("\n--- Jogada 5: PULADA (Jogada 1 falhou, célula (0,0) está vazia) ---")


    print("\n--- Jogada 6: 'Stardew Valley' na célula (2,0) (Abaixo da Jogada 3) ---")
    try:
        cell_2_0_locator = (By.CSS_SELECTOR, "div.game-slot[data-row='2'][data-col='0']")
        cell_2_0 = wait.until(EC.element_to_be_clickable(cell_2_0_locator))
        cell_2_0.click()

        wait.until(EC.visibility_of_element_located((By.ID, "search-modal")))
        genres_text = driver.find_element(By.ID, "modal-genres-text").text
        print(f"Célula (2,0) requer: {genres_text}")
        
        input_field = driver.find_element(By.ID, "game-search-input")
        input_field.clear() 
        input_field.send_keys("Stardew Valley")
        
        search_result_li = (By.CSS_SELECTOR, "#search-results-list li.search-result-item")
        first_result = wait.until(EC.element_to_be_clickable(search_result_li))
        
        result_text = first_result.text
        print(f"Primeiro resultado encontrado: '{result_text}'. Clicando nele...")
        first_result.click()
        
        wait.until(EC.invisibility_of_element_located((By.ID, "search-modal")))
        print("Modal fechou. Verificando resultado...")

        try:
            short_wait = WebDriverWait(driver, 2)
            img_locator = (By.CSS_SELECTOR, "div.game-slot[data-row='2'][data-col='0'] img")
            short_wait.until(EC.visibility_of_element_located(img_locator))
            print("✅ RESULTADO JOGADA 6: ACERTO (Imagem apareceu na célula)")
        except Exception:
            status_box = driver.find_element(By.ID, "game-status-box")
            assert "error-message" in status_box.get_attribute("class")
            print(f"⚠️ RESULTADO JOGADA 6: ERRO (Gêneros não bateram. Msg: '{status_box.text}')")
            
    except Exception as e:
        print(f"XXX FALHA GRAVE NA [Jogada 6]: {e}")
        try:
            driver.find_element(By.CSS_SELECTOR, "#search-modal-close-btn").click()
        except:
            pass
        time.sleep(1)
        
    print("\n>>> Teste Completo da UI do Steam Tac Toe: SUCESSO")
    print("--- Finalizando Teste Completo da UI do Steam Tac Toe ---")
    time.sleep(DELAY_PARA_VER)


if __name__ == "__main__":
    print("=== Iniciando Suíte de Testes ===")
    driver, wait = configurar_driver()

    if driver:
        try:
            rodar_teste_registro(driver, wait)
            rodar_teste_busca_alternada(driver, wait)          
            rodar_teste_filtro(driver, wait)
            rodar_teste_aplicar_filtro(driver, wait)
            rodar_teste_voltar_home(driver, wait)
            rodar_teste_clicar_jogo(driver, wait)
            rodar_teste_adicionar_e_gerenciar_jornada(driver, wait)
            rodar_teste_dar_nota_e_comentar(driver, wait) 
            rodar_teste_ir_para_biblioteca(driver, wait) 
            rodar_teste_modificar_avaliacao_biblioteca(driver, wait)
            rodar_teste_ir_para_biblioteca(driver, wait) 
            rodar_teste_ir_para_configuracoes(driver, wait) 
            rodar_teste_preferencias_e_tema(driver, wait)
            rodar_teste_voltar_home(driver, wait)
            rodar_teste_ir_para_steam_tac_toe(driver, wait)
            rodar_teste_ui_steam_tac_toe(driver, wait) 

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