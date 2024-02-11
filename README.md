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
   Em seguida, digite o nome do arquivo que deseja enviar ao servidor e tecle *Enter*.
5. Observe na pasta do diretório que foram salvos dois novos arquivos: 
   *  **"nfileRecvFromClient"** refere-se ao arquivo que o servidor recebeu do cliente, onde *n* é o numero pela ordem da requisição desde que o servidor foi executado;
   * **"fileRecvFromServer"** refere-se ao arquivo que o cliente recebeu em resposta do servidor.
   Ambos os arquivos estão no formato referente ao arquivo enviado inicialmente pelo cliente.
6. Se desejar enviar mais arquivos, basta voltar ao passo 3 e executar o cliente novamente. Não é necessário executar o servidor novamente, pois ele fica esperando por mais requisições do cliente.

**OBS.: O arquivo que deseja enviar deve estar salvo na mesma pasta do projeto. Os arquivos de teste disponibilizados na atividade são: `image.pdf` e `TesteTXT.txt`. Além disso, são mantidas cópias dos arquivos recebidos pelo server, entretanto, os aquivos recebidos pelo client são sobrescritos, a menos que a extensão seja diferente do último enviado.**
