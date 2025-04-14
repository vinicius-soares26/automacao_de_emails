import smtplib
from email.message import EmailMessage
import os
import json

def enviar_emails(senha, remetente, destinatarios, assunto, corpo_base, anexos, cargos_permitidos=None):
    erros_envio = []  # Lista para acumular falhas

    for destinatario in destinatarios:
        # Se cargos_permitidos for especificado, verifica se o destinatário tem cargo permitido
        if cargos_permitidos and destinatario.get("cargo") not in cargos_permitidos: # Mesma coisa que -- if cargos_permitidos is not None and destinatario.get("cargo") not in cargos_permitidos:
            continue

        nome_destinatario = destinatario["nome"]
        email_destinatario = destinatario["email"]

        # Cria o objeto e-mail e atribui assunto, remetente e email do destinatario
        email = EmailMessage()
        email["Subject"] = assunto
        email["From"] = remetente
        email["To"] = email_destinatario

        # Corpo do e-mail (personalizado pelo nome do destinatário)
        corpo = corpo_base.format(nome=nome_destinatario)
        email.set_content(corpo)

        # Carregando os anexos
        for caminho_anexo in anexos:
            with open(caminho_anexo, "rb") as f:
                # Carregando o arquivo (em binario) e o nome do arquivo
                arquivo = f.read()
                nome_arquivo = os.path.basename(caminho_anexo)
                # Adicionando o anexo
                email.add_attachment(arquivo, filename=nome_arquivo, maintype="application", subtype="octet-stream")

        try:
            # Criando conexao para enviar email
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                # Logando no remetente com a senha
                smtp.login(remetente, senha)
                # Enviando o e-mail
                smtp.send_message(email)
                # print(f"📨 E-mail enviado para {nome_destinatario} <{email_destinatario}>")
        # Acumula as falhas na lista de erros
        except Exception as erro:
            erros_envio.append((nome_destinatario, email_destinatario, str(erro))) 

    # E caso tenha havido falhas, envia e-mail.
    if erros_envio:
        aviso = EmailMessage()
        aviso["Subject"] = "❌ Relatório de falhas no envio de e-mails ❌"
        aviso["From"] = remetente
        aviso["To"] = "vinicius4burame@gmail.com"

        corpo_erro = "As seguintes falhas ocorreram durante o envio de e-mails para os indivíduos:\n\n"
        for nome, email, erro in erros_envio:
            corpo_erro += f"- {nome} <{email}>: {erro}\n"

        aviso.set_content(corpo_erro)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(remetente, senha)
            smtp.send_message(aviso)

json_base = os.getenv('DIC_BASE')
dic_base = json.loads(json_base)

json_email = os.getenv('DIC_EMAIL')
dic_email = json.loads(json_email)

enviar_emails(**dic_base, **dic_email)
enviar_emails(**dic_base, **dic_email, cargos_permitidos=['Diretor (a)'])
