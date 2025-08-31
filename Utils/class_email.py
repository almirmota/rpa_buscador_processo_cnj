from botcity.plugins.email import BotEmailPlugin

# Instanciar o plug -in
email = BotEmailPlugin()

# Configure IMAP com o servidor Gmail
email.configure_imap("imap.gmail.com", 993)

# Configure SMTP com o servidor Gmail
email.configure_smtp("imap.gmail.com", 587)

# Faça login com uma conta de email válida
email.login("almirmota.ma@gmail.com", "kwnx qyvq lwwh ninp")

class Email:
    def __init__(self):
        self.subject = ''
        self.body = ''
        self.to = ''

    def email_sucesso(self,descricao, processo):
        # Defining the attributes that will compose the message
        self.to = ["almirmota@yahoo.com.br","vitormonteiromota@gmail.com"]
        self.subject = "Informações sobre processo - Teste do robô"
        html1 = f'''<h1>Atenção!</h1>
                    <h4>Segue texto com as informações sobre o processo {processo} </h4>
                    <p>{descricao}</p>'''
        
        
        self.body = html1
        path_arquivo = r'saida\screenshot_tela_processo.png'
        self.files = [path_arquivo]

        # Sending the email message
        email.send_message(self.subject, self.body, self.to, attachments=self.files, use_html=True)

        # Close the conection with the IMAP and SMTP servers
        email.disconnect()
        
    
