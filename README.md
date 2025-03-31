# queue-load-test

Instruções:

1 - Clone o repositório https://github.com/ctakamiya/queue-load-test
$ git clone https://github.com/ctakamiya/queue-load-test.git

2 - Entre no diretório:
$ cd queue-load-test

3 - Execute o comando:
$ docker compose up

4 - Acesse o utilitário locust.io na URL: http://localhost:8089

5 - Configure os parâmetros de teste. É importante no "Custom Parameters" informar o Databricks PAT e a URL do endpoint.
Obs. O tempo de execução de um chatbot é uma "transação" mais demorada. Portanto, coloque requisitos de desempenhos adequados para este tipo de workload.

