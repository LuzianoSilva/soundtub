# Dependências incorporadas

O SoundTub executa ferramentas independentes incluídas no pacote; ele não instala
programas no Windows e não lê cookies do navegador.

| Componente | Versão incorporada | Origem | Licença |
|---|---:|---|---|
| yt-dlp nightly | 2026.08.16.020253 | https://github.com/yt-dlp/yt-dlp | Unlicense e licenças dos componentes empacotados |
| FFmpeg | N-126175-g0056dd32fd-20260816 | https://ffmpeg.org/ | GPLv3 |
| QuickJS-NG | 0.16.1 | https://github.com/quickjs-ng/quickjs | MIT |
| BgUtils POT Provider (Rust) | 0.8.1 | https://github.com/jim60105/bgutil-ytdlp-pot-provider-rs | GPLv3 |

Os hashes SHA-256 estão em
`addon/globalPlugins/soundtub/dependencies/checksums.sha256`. Execute
`powershell -ExecutionPolicy Bypass -File tools/verify_dependencies.ps1` para
comprovar a integridade. Licenças e fontes correspondentes exigidos estão na pasta
`dependencies/legal`.
