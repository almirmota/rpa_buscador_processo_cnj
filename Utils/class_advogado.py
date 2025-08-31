

class Advogado:
    def __init__(self, nome, oab, especialidade):
        self.nome = nome
        self.oab = oab
        self.especialidade = especialidade

    def apresentar(self):
        return f"Sou o advogado {self.nome}, OAB {self.oab}, especializado em {self.especialidade}."

    def peticionar(self, processo):
        return f"O advogado {self.nome} protocolou uma petição no processo {processo}."

    def processos(self, codigo):
        return f"O advogado {self.nome} de OAB {self.oab } possui o seguinte processo{codigo}."