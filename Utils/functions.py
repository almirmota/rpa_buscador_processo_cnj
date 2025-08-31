import os
import mysql.connector
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from types import SimpleNamespace



def connect_db():
    load_dotenv()  # carrega as variáveis do .env

    # Pegar variáveis do .env
    db_config = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "database": os.getenv("DB_NAME")
    }

    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print("Conexão estabelecida com sucesso!")
            return conn
    except Error as e:
        print(f"Erro ao conectar: {e}")
        return False

def buscar_movimentacoes_por_oab(oab,conn):
    
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        
        cursor.callproc('sp_buscar_e_atualizar_movimentacao', [oab])
        
        # Pega o primeiro resultado retornado pela procedure
        for result in cursor.stored_results():
            linhas = result.fetchall()
            if linhas:  # se encontrou algum registro
                
                # Confirma a atualização no banco
                conn.commit()
                
                # Converte o primeiro registro em objeto
                return SimpleNamespace(**linhas[0])

        return None  # se não encontrou nenhum registro
        
    except Error as e:
        print(f"Erro ao executar SELECT: {e}")
        return []
    finally:
        if conn.is_connected():
            # conn.close()
            print("A conxão está ativa.")


def inserir_sucesso(conn, id_movimentacao, data_movimento, descricao):
    """
    Atualiza os campos data_movimento e descricao na tabela monimentacoes
    para o registro informado.
    """
    if not conn:
        return False

    cursor = None
    try:
        cursor = conn.cursor()

        sql = """
            UPDATE legislacao.movimentacoes
            SET data_movimento = %s,
                descricao = %s,
                status = %s,
                desc_status = %s
            WHERE id = %s
        """
        status = 0
        desc_status = 'PROCESSADO COM SUCESS'
        valores = (data_movimento, descricao,status,desc_status, id_movimentacao)
        cursor.execute(sql, valores)

        # ✅ Persistir a alteração
        conn.commit()

        return True

    except Error as e:
        print(f"Erro ao atualizar movimentação: {e}")
        return False

    # finally:
    #     if cursor:
    #         cursor.close()
    #     if conn.is_connected():
    #         conn.close()

def retornar_fila(conn, id_movimentacao, qtd_tentativas):
    """
    Atualiza os campos data_movimento e descricao na tabela monimentacoes
    para o registro informado.
    """
    if not conn:
        return False

    cursor = None
    try:
        cursor = conn.cursor()

        sql = """
            UPDATE legislacao.movimentacoes
            SET status = %s,
                desc_status = %s
            WHERE id = %s
        """
        if qtd_tentativas >=3:
            status = 1
            desc_status = 'RETORNADO PARA FILA'
        else:
            status = 3
            desc_status = 'ERRO DE PROCESSAMENTO'
            
        qtd_tentativas += 1
        valores = (status,desc_status, id_movimentacao)
        cursor.execute(sql, valores)

        # ✅ Persistir a alteração
        conn.commit()

        return True

    except Error as e:
        print(f"Erro ao atualizar movimentação: {e}")
        return False

    # finally:
    #     if cursor:
    #         cursor.close()
    #     if conn.is_connected():
    #         conn.close()

def formatar_processo(num: str) -> str:
    """
    Formata uma string de 20 dígitos no padrão CNJ:
    NNNNNNN-DD.AAAA.J.TR.OOOO
    """
    return f"{num[:7]}-{num[7:9]}.{num[9:13]}.{num[13]}.{num[14:16]}.{num[16:]}"