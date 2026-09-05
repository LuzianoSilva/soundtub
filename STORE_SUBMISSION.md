# Preparação para a Loja de Complementos do NVDA

## Estado atual

O código e o pacote 3.3.3 estão preparados, mas a publicação só deve ocorrer depois
de testar manualmente esta versão no NVDA estável mais recente. O manifesto declara
apenas a versão do NVDA efetivamente usada nos testes locais.

## Dados para o cadastro

- Identificador: `soundtub`
- Nome público: SoundTub
- Editor: Luziano Silva - desenvolvedor de software — luzianosilva.dv@gmail.com
- Canal inicial: stable
- Licença: GNU GPL v3 ou posterior (`GPL-3.0-or-later`)
- URL da licença: `https://www.gnu.org/licenses/gpl-3.0.html`
- Repositório de código: `https://github.com/SEU_USUARIO/soundtub`
- Download imutável: `https://github.com/SEU_USUARIO/soundtub/releases/download/v3.3.3/SoundTub-3.3.3.nvda-addon`

Substitua `SEU_USUARIO` pelo nome real da conta antes do cadastro.

## Checklist antes de publicar

1. Testar instalação, abertura com NVDA+Alt+C, MP3, MP4, cancelamento e reinício do NVDA.
2. Testar com a versão estável mais recente do NVDA e só então atualizar `lastTestedNVDAVersion`.
3. Executar `python -m unittest discover -s tests`.
4. Executar `powershell -ExecutionPolicy Bypass -File tools/build_addon.ps1`.
5. Confirmar o SHA-256 e instalar o arquivo produzido em `dist`.
6. Criar um repositório público no GitHub e publicar o código com a tag `v3.3.3`.
7. Anexar o `.nvda-addon` à release; a URL precisa ser HTTPS, direta, imutável e terminar em `.nvda-addon`.
8. Enviar o formulário de registro: https://github.com/nvaccess/addon-datastore/issues/new?template=registerAddon.yml

O primeiro cadastro de um editor pode passar por análise manual. Não altere o arquivo
de uma release já cadastrada; publique uma versão e uma URL novas.
