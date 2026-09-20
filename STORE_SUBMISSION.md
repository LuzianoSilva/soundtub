# Preparação para a Loja de Complementos do NVDA

## Estado atual

A versão 4.0.0 foi publicada na Loja de Complementos do NVDA. Para a atualização
4.1.0, o manifesto mantém a última versão do NVDA declarada como testada; somente
altere esse campo após um teste na versão correspondente.

## Dados para o cadastro

- Identificador: `soundtub`
- Nome público: SoundTub
- Editor: Luziano Silva - desenvolvedor de software — luzianosilva.dv@gmail.com
- Canal inicial: stable
- Licença: GNU GPL v3 ou posterior (`GPL-3.0-or-later`)
- URL da licença: `https://www.gnu.org/licenses/gpl-3.0.html`
- Repositório de código: `https://github.com/LuzianoSilva/soundtub`
- Download imutável da atualização: `https://github.com/LuzianoSilva/soundtub/releases/download/v4.1.0/SoundTub-4.1.0.nvda-addon`

## Checklist antes de publicar

1. Testar instalação, abertura com NVDA+Alt+Y, MP3, MP4, cancelamento e reinício do NVDA.
2. Testar com a versão estável mais recente do NVDA e só então atualizar `lastTestedNVDAVersion`.
3. Executar `python -m unittest discover -s tests`.
4. Executar `powershell -ExecutionPolicy Bypass -File tools/build_addon.ps1`.
5. Confirmar o SHA-256 e instalar o arquivo produzido em `dist`.
6. Publicar o código-fonte e criar a tag `v4.1.0` no GitHub.
7. Anexar o `.nvda-addon` à release; a URL precisa ser HTTPS, direta, imutável e terminar em `.nvda-addon`.
8. Enviar o formulário de registro: https://github.com/nvaccess/addon-datastore/issues/new?template=registerAddon.yml

O primeiro cadastro de um editor pode passar por análise manual. Não altere o arquivo
de uma release já cadastrada; publique uma versão e uma URL novas.
