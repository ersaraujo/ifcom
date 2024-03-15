# Projeto de Infraestrutura de Comunicações
## Equipe
* Elisson Rodrigo da Silva Araujo (ersa)

## Instruções de execução da primeira entrega
1. Baixe a pasta e extraia os arquivos.
2. Considerando que já tenha Python3 instalado, abra duas abas do terminal no diretório em que baixou a pasta.
3. Em uma das abas execute o comando: 
   ```
   python3 server.py
   ```
   O servidor será inicializado e irá aguardar alguma requisição.
4. Na outra aba do terminal execute o comando: 
   ```
   python3 client.py
   ```
   O primeiro comando a ser enviado é o de conexão ```connect as <user>```. Será exibido no terminal as instruções dos demais comandos.
5. Para os comandos ```reservar```, ```cancelar``` e ```check``` o formato da sala de ser E10x (0 < x < 5), do dia deve ser todo minusculo "segunda, terça, quarta, quinta e sexta" e a hora dever ser um inteiro (8 a 16)
