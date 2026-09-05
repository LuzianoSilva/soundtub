import logging
import os
import subprocess
import threading
from pathlib import Path

from .utils import (
    friendly_error,
    has_permanent_content_error,
    parse_playlist_done,
    parse_playlist_item,
    parse_progress,
)

log = logging.getLogger("nvda.soundtub")


class DownloadCancelled(Exception):
    pass


class DownloadWorker:
    def __init__(self, tools_dir, url, media_format, destination, playlist, on_progress, on_done, on_status=None, on_item=None):
        self.tools_dir = Path(tools_dir)
        self.url = url
        self.media_format = media_format
        self.destination = destination
        self.playlist = playlist
        self.on_progress = on_progress
        self.on_done = on_done
        self.on_status = on_status or (lambda message: None)
        self.on_item = on_item or (lambda index, total: None)
        self._process = None
        self._cancelled = threading.Event()
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._run, name="SoundTubDownload", daemon=True)
        self._thread.start()

    def cancel(self):
        self._cancelled.set()
        process = self._process
        if process and process.poll() is None:
            try:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
                        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL, timeout=5, check=False, shell=False,
                    )
                else:
                    process.terminate()
            except OSError:
                log.exception("Falha ao encerrar o processo do SoundTub")

    def build_command(self, player_client="web_embedded", playlist_items=None):
        ytdlp = self.tools_dir / "yt-dlp.exe"
        ffmpeg = self.tools_dir
        command = [
            str(ytdlp), "--newline", "--no-warnings",
            "--force-ipv4", "--no-continue", "--retries", "5", "--fragment-retries", "5",
            "--progress-template", "download:ST_PROGRESS:%(progress._percent_str)s",
            "--ffmpeg-location", str(ffmpeg),
            "--windows-filenames", "--trim-filenames", "180",
        ]
        if self.playlist:
            command.extend([
                "--yes-playlist",
                "--print", "before_dl:ST_ITEM:%(playlist_index)s:%(playlist_count)s",
                "--print", "after_move:ST_DONE:%(playlist_index)s:%(playlist_count)s",
                "-o", str(Path(self.destination) / "%(playlist_title).150B" / "%(playlist_index)03d - %(title).150B.%(ext)s"),
            ])
            if playlist_items:
                command.extend(["--playlist-items", ",".join(str(item) for item in playlist_items)])
        else:
            command.extend([
                "--no-playlist",
                "-o", str(Path(self.destination) / "%(title).180B.%(ext)s"),
            ])
        quickjs = self.tools_dir / "qjs.exe"
        if quickjs.is_file():
            command.extend(["--js-runtimes", "quickjs:%s" % quickjs])
        plugins = self.tools_dir / "plugins"
        command.extend(["--plugin-dirs", str(plugins)])
        if player_client == "mweb":
            provider = self.tools_dir / "bgutil-pot.exe"
            command.extend([
                "--extractor-args", "youtubepot-bgutilcli:cli_path=%s" % provider,
                "--extractor-args", "youtube:player_client=mweb",
            ])
        else:
            command.extend(["--extractor-args", "youtube:player_client=web_embedded"])
        if self.media_format == "MP3":
            command.extend([
                "-f", "bestaudio/best", "-x", "--audio-format", "mp3",
                "--audio-quality", "192K", "--embed-metadata",
            ])
        else:
            command.extend([
                "-f", "bv*+ba/b", "-S", "res:1080,vcodec:h264,acodec:aac",
                "--merge-output-format", "mp4", "--recode-video", "mp4",
                "--embed-metadata",
            ])
        command.extend(["--", self.url])
        return command

    def _run(self):
        output = []
        completed_items = set()
        playlist_total = None
        partial_failure = False
        try:
            required = (
                "yt-dlp.exe", "ffmpeg.exe", "ffprobe.exe", "qjs.exe",
                "bgutil-pot.exe", "plugins/bgutil-ytdlp-pot-provider-rs.zip",
            )
            missing = [name for name in required if not (self.tools_dir / name).is_file()]
            if missing:
                raise RuntimeError(_("Ferramentas internas ausentes: %s") % ", ".join(missing))
            creationflags = 0
            if os.name == "nt":
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            self.on_status(_("Analisando o endereço."))
            download_announced = False
            retry_items = None
            for player_client in ("web_embedded", "mweb"):
                attempt_output = []
                if player_client == "mweb":
                    self.on_status(_("Obtendo autorização anônima."))
                log.info("Tentando download com o cliente anônimo %s", player_client)
                self._process = subprocess.Popen(
                    self.build_command(player_client, retry_items),
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace",
                    creationflags=creationflags, shell=False,
                )
                for line in self._process.stdout:
                    clean = line.strip()
                    attempt_output.append(clean)
                    log.debug("yt-dlp: %s", clean)
                    playlist_item = parse_playlist_item(clean)
                    if playlist_item is not None:
                        item_index, item_total = playlist_item
                        if item_total:
                            playlist_total = item_total
                        self.on_item(item_index, item_total)
                    playlist_done = parse_playlist_done(clean)
                    if playlist_done is not None:
                        item_index, item_total = playlist_done
                        completed_items.add(item_index)
                        if item_total:
                            playlist_total = item_total
                    progress = parse_progress(clean)
                    if progress is not None:
                        if not download_announced:
                            download_announced = True
                            self.on_status(_("Iniciando download."))
                        self.on_progress(progress)
                    if self._cancelled.is_set():
                        break
                return_code = self._process.wait()
                output.extend(attempt_output)
                if self._cancelled.is_set():
                    raise DownloadCancelled()
                if return_code == 0:
                    break
                if self.playlist and completed_items:
                    if has_permanent_content_error("\n".join(attempt_output)):
                        log.info(
                            "A playlist contém conteúdo indisponível; "
                            "não será feita uma tentativa de autorização."
                        )
                        partial_failure = True
                        break
                    if player_client == "web_embedded" and playlist_total:
                        retry_items = [
                            index for index in range(1, playlist_total + 1)
                            if index not in completed_items
                        ]
                        if retry_items:
                            log.warning(
                                "A primeira tentativa da playlist foi parcial; "
                                "tentando somente os itens ausentes: %s",
                                retry_items,
                            )
                            continue
                    partial_failure = True
                    break
                log.warning(
                    "Cliente %s falhou; tentando a alternativa anônima. Saída: %s",
                    player_client, " | ".join(attempt_output[-5:]),
                )
            else:
                raise RuntimeError("\n".join(output[-40:]))
        except DownloadCancelled:
            self.on_done(False, _("Download cancelado."))
        except Exception as error:
            log.exception("Erro no download do SoundTub")
            self.on_done(False, friendly_error(str(error)))
        else:
            if self.playlist and playlist_total and len(completed_items) < playlist_total:
                missing = playlist_total - len(completed_items)
                message = _(
                    "Playlist concluída parcialmente: %(completed)d de %(total)d itens baixados. "
                    "%(missing)d item ou itens estavam indisponíveis ou foram recusados. "
                    "Os arquivos concluídos não foram repetidos."
                ) % {
                    "completed": len(completed_items),
                    "total": playlist_total,
                    "missing": missing,
                }
                self.on_done(False, message)
            elif partial_failure:
                self.on_done(False, _(
                    "A playlist foi concluída parcialmente. Os arquivos concluídos não foram repetidos."
                ))
            else:
                self.on_done(True, _("Download concluído com sucesso."))
        finally:
            self._process = None
