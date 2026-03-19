# Robô de Consulta

Este é um programa de computador (robô) que faz o trabalho de entrar no Portal da Transparência, buscar todas as informações de pagamento de uma pessoa e organizar tudo em relatórios fáceis de ler.

##  O que o Robô faz por você?

* **Busca Completa:** Ele não esquece nenhuma parcela. O robô "folheia" todas as páginas do sistema do governo até encontrar tudo.
* **Relatórios Automáticos:** Ele cria três arquivos sozinho:
    1. Um arquivo de dados para sistemas (**JSON**).
    2. Uma tabela bonita e organizada para você ler (**HTML**).
    3. Um código de segurança para provar que a busca foi feita (**Base64**).
* **Aviso no Discord:** Se você usa o Discord, o robô te manda uma mensagem avisando que terminou o trabalho e quem foi a pessoa consultada.
* **Funciona "Escondido":** Você pode mandar o robô trabalhar sem precisar abrir janelas de navegador, direto pelo comando do computador.

## O que você precisa para começar?

Você precisará ter o **Python** instalado no seu computador e baixar dois complementos simples abrindo o seu terminal e digitando:

```bash
pip install requests python-dotenv
```

## Como configurar (Arquivo .env)
Para o robô funcionar, ele precisa da sua "chave" de acesso ao site do governo. Crie um arquivo de texto com o nome .env e coloque isso dentro:

*Snippet de código:*

CHAVE_API_DADOS=COLE_SUA_CHAVE_AQUI

DISCORD_WEBHOOK_URL=COLE_O_LINK_DO_DISCORD_AQUI

## Como usar o Robô
Existem duas formas de pedir para o robô trabalhar:

*Opção 1:* Digitando na hora
Apenas digite o comando abaixo e, quando o robô perguntar, digite o CPF ou NIS da pessoa:

```Bash
python main.py
```

*Opção 2:* Direto e Reto
Se você já sabe o número, pode colocar ele direto no comando para o robô nem precisar te perguntar nada:

```Bash
python main.py 13374917541
```

## Onde estão os resultados?
Assim que o robô termina, ele avisa na tela:

[INFO] relato.json gerado

[INFO] parcelas.html gerado

[INFO] print_base64.txt gerado
