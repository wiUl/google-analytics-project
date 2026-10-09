# Monitoramento do Power Automate Desktop

O `main.py` aguarda o resultado do fluxo por meio do arquivo:

`output/flow_status.json`

O Python apaga esse arquivo antes de chamar o PAD. Portanto, o próprio fluxo PAD precisa gravar um resultado novo a cada execução.

## 1. Ao final do fluxo (sucesso)

Adicione uma ação **Gravar texto em arquivo** depois que o upload para o SharePoint terminar com sucesso.

- Caminho: caminho absoluto da pasta do projeto + `output\flow_status.json`
- Texto a gravar (texto simples, não variável):

```json
{"status": "success"}
```

Configure a ação para substituir o conteúdo existente, se solicitado.

## 2. Quando uma ação do fluxo falhar

Configure o tratamento de erros do PAD para capturar falhas no fluxo (por exemplo, usando a opção **Em caso de erro** / **On block error** nas ações ou no bloco que contém o processo de upload). No caminho de tratamento do erro, adicione **Gravar texto em arquivo**, usando o mesmo caminho e substituindo o conteúdo por:

```json
{"status": "error", "message": "Descreva aqui a etapa que falhou"}
```

Se a sua versão do PAD permitir inserir a mensagem de erro numa variável, grave-a no campo `message` para que o log Python registre o detalhe. O conteúdo precisa ser JSON válido.

**Importante:** se o fluxo não gravar um status de sucesso ou erro, o Python não tem como saber se o fluxo realmente terminou; ele aguardará até 30 minutos e então registrará timeout. Abrir a URL `ms-powerautomate:` com `os.startfile` só inicia a solicitação e não devolve o resultado final do fluxo.

## 3. Onde consultar os logs

O Python grava logs em:

`logs/automacao.log`

O log registra início e fim de cada script, mensagens de erro, falhas na leitura/gravação do Excel, o pedido de execução do PAD e o resultado recebido pelo arquivo de status.

O fluxo PAD deve ter acesso de gravação à pasta `output` no mesmo computador e no mesmo caminho local que o Python utiliza.
