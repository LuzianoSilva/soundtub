import re
from pathlib import Path
from urllib.parse import urlsplit

_PROGRESS_RE = re.compile(r"ST_PROGRESS:\s*([0-9]+(?:[.,][0-9]+)?)%")
_PLAYLIST_ITEM_RE = re.compile(r"ST_ITEM:\s*(\d+):(?:(\d+)|NA)")
_PLAYLIST_DONE_RE = re.compile(r"ST_DONE:\s*(\d+):(?:(\d+)|NA)")


def validate_url(value):
    value = value.strip()
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    if parsed.username or parsed.password:
        return None
    return value


def parse_progress(line):
    match = _PROGRESS_RE.search(line)
    if not match:
        return None
    try:
        return max(0, min(100, int(float(match.group(1).replace(",", ".")))))
    except ValueError:
        return None


def parse_playlist_item(line):
    match = _PLAYLIST_ITEM_RE.search(line)
    if not match:
        return None
    index = int(match.group(1))
    total = int(match.group(2)) if match.group(2) else None
    return index, total


def parse_playlist_done(line):
    match = _PLAYLIST_DONE_RE.search(line)
    if not match:
        return None
    index = int(match.group(1))
    total = int(match.group(2)) if match.group(2) else None
    return index, total


def has_permanent_content_error(output):
    text = output.lower()
    return any(marker in text for marker in (
        "video unavailable",
        "private video",
        "this video has been removed",
        "video has been removed",
        "members-only content",
    ))


def ensure_destination(folder):
    path = Path(folder).expanduser()
    if not path.is_dir():
        raise ValueError(_("A pasta de destino não existe."))
    return str(path.resolve())


def friendly_error(output):
    text = output.lower()
    if "po token" in text and ("failed" in text or "not provided" in text):
        return _("O YouTube não aceitou a verificação anônima. Aguarde um momento e tente novamente.")
    if "too many requests" in text or "http error 429" in text:
        return _("O YouTube limitou temporariamente os acessos e pediu confirmação de login. Aguarde alguns minutos e tente novamente. Alguns conteúdos podem exigir uma conta conectada.")
    if "http error 403" in text or "403: forbidden" in text:
        return _("O YouTube recusou o arquivo solicitado. Tente novamente; se o problema continuar, o conteúdo pode exigir autenticação.")
    if "unsupported url" in text:
        return _("Este endereço não é compatível com o SoundTub.")
    if "video unavailable" in text or "private video" in text:
        return _("O vídeo não está disponível ou é privado.")
    if "sign in" in text or "login required" in text:
        return _("O YouTube bloqueou temporariamente o acesso anônimo. Aguarde alguns minutos e tente novamente.")
    if "unable to download" in text or "network" in text or "timed out" in text:
        return _("Não foi possível acessar o serviço. Verifique sua conexão e tente novamente.")
    if "ffmpeg" in text or "ffprobe" in text:
        return _("As ferramentas internas de conversão estão ausentes ou danificadas. Reinstale o SoundTub.")
    return _("Não foi possível concluir o download. Consulte o log do NVDA para obter detalhes.")
