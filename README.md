# SSPA Private Server — pacote para hospedagem gratuita de teste

Este pacote adapta o `sspa_server.zip` recebido para aceitar a porta definida pela plataforma e detectar `RENDER_EXTERNAL_URL`. Os arquivos `.bin` e `.ver` foram preservados; nenhum asset ausente foi inventado.

## Publicar no Render (sem domínio próprio)

1. Extraia este ZIP.
2. Envie o conteúdo da pasta para um repositório GitHub novo (público ou privado).
3. No Render, escolha **New + → Blueprint** e conecte o repositório; ou crie um **Web Service** com:
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `python server.py`
   - Plano: Free
4. Aguarde o deploy. O Render fornecerá um endereço `https://NOME.onrender.com`.
5. Teste `https://NOME.onrender.com/health`, `/api` e um asset, por exemplo `/assets/MusicData`.
6. Confira os logs durante o teste do jogo.

## Importante

- Este pacote ainda é experimental. Hospedar online não garante compatibilidade com o cliente 1.4.11.
- O servidor anuncia apenas os assets presentes no diretório, mas a lista `ASSET_MAP` contém referências a arquivos ausentes. O cliente pode solicitar alguns deles; os logs mostrarão `BIN NÃO ENCONTRADO`.
- Os `.bin` foram preservados byte a byte. Não sabemos ainda se o formato deles é exatamente o esperado pela versão do APK que você está usando.
- O serviço gratuito pode entrar em suspensão após inatividade, demorar para acordar e ter limites de uso.
- Não use este servidor para dados pessoais ou credenciais reais. A API é experimental, sem autenticação robusta e sem persistência de conta.
- Para o APK usar o servidor, sua URL de API/CDN precisa estar configurada para o endereço público HTTPS. Este pacote de servidor não modifica o APK.
