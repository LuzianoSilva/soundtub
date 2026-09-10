# SoundTub

Add-on acessível para baixar áudio MP3 e vídeo MP4 pelo NVDA com `NVDA+Alt+Y`.

## Diferencial

O SoundTub foi projetado para uma experiência centrada no NVDA, sem depender da
acessibilidade de páginas ou aplicativos externos. A interface é totalmente operável
por teclado e o leitor de telas anuncia a análise do endereço, o início e o progresso
do download, a posição na playlist, conclusões parciais e erros. Em playlists, os
arquivos já concluídos são preservados e somente os itens ausentes são tentados
novamente. O funcionamento é anônimo e não lê cookies nem contas do navegador.

## Arquitetura

- `gui.py`: janela wxPython, feedback acessível e coordenação da thread.
- `downloader.py`: processo isolado, progresso, cancelamento e tradução de erros.
- `config.py`: persistência da pasta e base para configurações futuras.
- `utils.py`: validação de URL, caminhos e mensagens amigáveis.
- `dependencies/win64`: ferramentas internas; nada é instalado no Windows do usuário.

## Desenvolvimento

Execute os testes com `python -m unittest discover -s tests`. O pacote final é criado por
`tools/build_addon.ps1`, depois que as dependências verificadas forem preparadas.

O download deve ser usado apenas para conteúdo que o usuário tenha direito de baixar.

## Dependências e licenças

O pacote usa versões fixas de yt-dlp, FFmpeg e QuickJS-NG e inclui hashes, licenças e os
fontes correspondentes exigidos pelas ferramentas GPL. Consulte
`addon/globalPlugins/soundtub/dependencies/THIRD-PARTY-NOTICES.txt`. O FFmpeg GPL
foi escolhido porque a conversão MP3 requer libmp3lame. A compilação compartilhada
evita duplicar as bibliotecas usadas por FFmpeg e FFprobe, preservando a instalação
em um único arquivo.

O SoundTub também inclui um provedor local de PO Token em Rust. Ele permite que o
yt-dlp responda às verificações anônimas do YouTube sem ler cookies, abrir navegador
ou acessar uma conta do usuário.
