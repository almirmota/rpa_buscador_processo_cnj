from Utils.functions import connect_db,buscar_movimentacoes_por_oab,inserir_sucesso,retornar_fila,formatar_processo
# Import for the Web Bot
from botcity.web import WebBot, Browser, By

from webdriver_manager.chrome import ChromeDriverManager

# Import for integration with BotCity Maestro SDK
from botcity.maestro import *

from datetime import datetime

from Utils.class_advogado import Advogado
from Utils.class_email import Email

from loguru import logger

from mysql.connector import Error

import pandas as pd

import pyautogui

from time import sleep

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False

# Instanciando a class advogado
nome = 'Vitor Monteiro Mota' 
oab = '1234567890' 
especialidade = 'Direito Penal'

advogado = Advogado(nome,oab,especialidade)
email = Email()

logger.add("arquivo.log")

#Enviar e-mail de sucesso
# email.email_sucesso()

conn = connect_db()

def main():
    # Runner passes the server url, the id of the task being executed,
    # the access token and the parameters that this task receives (when applicable).
    maestro = BotMaestroSDK.from_sys_args()
    ## Fetch the BotExecution with details from the task, including parameters
    execution = maestro.get_execution()

    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    bot = WebBot()

    # Configure whether or not to run on headless mode
    bot.headless = False

    # Uncomment to change the default Browser to Firefox
    bot.browser = Browser.CHROME

    # Setando o caminho do WebDriver do Chromedriver através do Webdriver manager
    bot.driver_path = ChromeDriverManager().install()
    

    buscar = True
    
    while buscar == True:
        # Opens the BotCity website.
        bot.browse("https://comunica.pje.jus.br/consulta")
        sleep(2)
            
        
        # Buscar a informação da fila
        dados = buscar_movimentacoes_por_oab(oab,conn)
        
        descricao = ''

        if dados:
            try:
                logger.info(f'Processo recuperado pela Store Procedure: {dados.processo}')
                data_pesquisa =  dados.data_movimento

                # Formatar para dd/mm/aaaa
                data_pesquisa_formatada = data_pesquisa.strftime("%d/%m/%Y")
            
                
                # data_inicial = bot.find_element('/html/body/app-root/uikit-layout/mat-sidenav-container/mat-sidenav-content/div[2]/app-consulta/div/div/div[1]/div/form/div/div/div[5]/div[1]/mat-form-field/div/div[1]/div[3]/input',By.XPATH)
                # data_inicial.send_keys(data_pesquisa_formatada)
                # bot.tab()
                # bot.wait(1000)

                # data_final = bot.find_element('/html/body/app-root/uikit-layout/mat-sidenav-container/mat-sidenav-content/div[2]/app-consulta/div/div/div[1]/div/form/div/div/div[5]/div[2]/mat-form-field/div/div[1]/div[3]/input',By.XPATH)
                # data_final.send_keys(data_pesquisa_formatada)
                # bot.tab()
                # bot.wait(1000)
                
                # Formatação
                processo_formatado = formatar_processo(dados.processo)
                
                logger.info(f'Digitando o processo numero: {processo_formatado}')
                input_processo = bot.find_element('/html/body/app-root/uikit-layout/mat-sidenav-container/mat-sidenav-content/div[2]/app-consulta/div/div/div[1]/div/form/div/div/div[6]/mat-form-field/div/div[1]/div[3]/input', by=By.XPATH)
                input_processo.send_keys(processo_formatado)
                sleep(4)
                    
                btn_pesquisar = bot.find_element(selector='//button[@class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" and @type="button"]', by=By.XPATH)
                ## Perform a default click action on the element
                btn_pesquisar.click()
                sleep(3)
            
                # Scroll para cima (equivalente a girar a rodinha do mouse para trás)
                pyautogui.scroll(1000)   # quanto maior o número, maior o scroll
                sleep(2)
                path_screenshot = r'saida\screenshot_tela_processo.png' 
                bot.screenshot(path_screenshot)

                disponibilizacao = bot.find_element('/html/body/app-root/uikit-layout/mat-sidenav-container/mat-sidenav-content/div[2]/app-consulta/div/div/div[2]/app-resultado/mat-tab-group/div/mat-tab-body[1]/div/div/article/div/aside/div[2]',By.XPATH)

                if disponibilizacao:
                    
                    texto = disponibilizacao.text
                    # divide em duas partes pelo primeiro ":"
                    data_extraida = texto.split(":", 1)[1].strip()

                    logger.info(f' Data extraida: {data_extraida}')
                
                content = bot.find_element('/html/body/app-root/uikit-layout/mat-sidenav-container/mat-sidenav-content/div[2]/app-consulta/div/div/div[2]/app-resultado/mat-tab-group/div/mat-tab-body/div/div/article/div/section/div/div[2]',By.XPATH)

                if content:
                    logger.info(f'Texto extraido: {content.text}')
                    
                    # Pega o texto extraido da tela
                    descricao = content.text
                    
                    result = inserir_sucesso(conn,dados.id,data_pesquisa,descricao)
                
                    if result == True:
                        
                        #Enviar e-mail de sucesso
                        email.email_sucesso(descricao,dados.processo)

                        # Uncomment to mark this task as finished on BotMaestro
                        maestro.finish_task(
                            task_id=execution.task_id,
                            status=AutomationTaskFinishStatus.SUCCESS,
                            message="Task Finished OK.",
                            total_items=0,
                            processed_items=0,
                            failed_items=0
                        )
                    
                    else:
                        logger.error('Erro na atualização !')
                        result = retornar_fila(conn,dados.id,dados.qtd_tentativas)
                else:
                    # Pega o texto extraido da tela
                    descricao = "Nenhuma informação encontrada na data"
                    retornar_fila(conn,dados.id,dados.qtd_tentativas)
                    logger.info('Atualização realizada com sucesso !')                
                    
            except Error as e:
                logger.error(f"Erro ao executar procedure: {e}")
                main()
                
            
        else:
            logger.info('Não existem dados para processamento')
            # Uncomment to mark this task as finished on BotMaestro
            maestro.finish_task(
                task_id=execution.task_id,
                status=AutomationTaskFinishStatus.SUCCESS,
                message="Task Finished OK.",
                total_items=0,
                processed_items=0,
                failed_items=0
            )
            buscar = False    

        bot.stop_browser()
    
    # Finish and clean up the Web Browser
    # You MUST invoke the stop_browser to avoid
    # leaving instances of the webdriver open
    bot.stop_browser()

    # Uncomment to mark this task as finished on BotMaestro
    # maestro.finish_task(
    #     task_id=execution.task_id,
    #     status=AutomationTaskFinishStatus.SUCCESS,
    #     message="Task Finished OK.",
    #     total_items=0,
    #     processed_items=0,
    #     failed_items=0
    # )


def not_found(label):
    print(f"Element not found: {label}")


if __name__ == '__main__':
    main()
