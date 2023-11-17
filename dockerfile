# Use a imagem base Python
FROM python:3.9

# Define o diretório de trabalho no container
WORKDIR /app

# Copia os arquivos necessários para o container
COPY ./app/requirements.txt /app/requirements.txt
COPY ./app/main.py /app/main.py

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponha a porta do container
EXPOSE 5000

# Comando para iniciar o aplicativo quando o container for executado
CMD ["python", "main.py"]
