from pathlib import Path

import ui
import wx

from . import config as soundtub_config
from .downloader import DownloadWorker
from .utils import ensure_destination, validate_url


class SoundTubDialog(wx.Dialog):
    ANNOUNCE_AT = (10, 25, 50, 75, 100)

    def __init__(self, parent, on_closed):
        super().__init__(parent, title=_("SoundTub"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self._on_closed = on_closed
        self._worker = None
        self._announced = set()
        self._buildUi()
        self.Bind(wx.EVT_CLOSE, self._onClose)
        self.SetMinSize((540, 340))
        self.Fit()
        self.CentreOnParent()
        self.url.SetFocus()

    def _buildUi(self):
        panel = wx.Panel(self)
        root = wx.BoxSizer(wx.VERTICAL)

        root.Add(wx.StaticText(panel, label=_("&URL do vídeo ou música:")), 0, wx.ALL, 8)
        self.url = wx.TextCtrl(panel, name=_("URL do vídeo ou música"))
        root.Add(self.url, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        root.Add(wx.StaticText(panel, label=_("&Formato:")), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        self.format = wx.Choice(panel, choices=[_("MP3 — somente áudio"), _("MP4 — vídeo")], name=_("Formato"))
        self.format.SetSelection(1 if soundtub_config.get_default_format() == "MP4" else 0)
        root.Add(self.format, 0, wx.EXPAND | wx.ALL, 8)

        self.playlist = wx.CheckBox(panel, label=_("Baixar &playlist completa"))
        self.playlist.SetValue(False)
        root.Add(self.playlist, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        root.Add(wx.StaticText(panel, label=_("Pasta de &destino:")), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        folder_row = wx.BoxSizer(wx.HORIZONTAL)
        self.folder = wx.TextCtrl(panel, value=soundtub_config.get_download_folder(), style=wx.TE_READONLY, name=_("Pasta de destino atual"))
        folder_row.Add(self.folder, 1, wx.RIGHT, 8)
        choose = wx.Button(panel, label=_("&Escolher pasta…"))
        choose.Bind(wx.EVT_BUTTON, self._chooseFolder)
        folder_row.Add(choose, 0)
        root.Add(folder_row, 0, wx.EXPAND | wx.ALL, 8)

        self.status = wx.StaticText(panel, label=_("Pronto."), name=_("Estado do download"))
        root.Add(self.status, 0, wx.EXPAND | wx.ALL, 8)
        self.progress = wx.Gauge(panel, range=100, name=_("Progresso do download"))
        root.Add(self.progress, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        buttons = wx.StdDialogButtonSizer()
        self.download = wx.Button(panel, label=_("&Baixar"))
        self.download.Bind(wx.EVT_BUTTON, self._startDownload)
        buttons.AddButton(self.download)
        self.cancel = wx.Button(panel, label=_("&Cancelar download"))
        self.cancel.Disable()
        self.cancel.Bind(wx.EVT_BUTTON, self._cancelDownload)
        buttons.AddButton(self.cancel)
        close = wx.Button(panel, wx.ID_CLOSE, label=_("&Fechar"))
        close.Bind(wx.EVT_BUTTON, lambda event: self.Close())
        buttons.AddButton(close)
        buttons.Realize()
        root.Add(buttons, 0, wx.ALIGN_RIGHT | wx.ALL, 8)
        panel.SetSizer(root)

        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(outer)

    def _chooseFolder(self, event):
        with wx.DirDialog(self, _("Escolha a pasta de destino"), defaultPath=self.folder.Value) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.folder.Value = dialog.Path
                soundtub_config.set_download_folder(dialog.Path)

    def _startDownload(self, event):
        url = validate_url(self.url.Value)
        if not url:
            self._showError(_("Digite um endereço HTTP ou HTTPS válido."))
            self.url.SetFocus()
            return
        try:
            destination = ensure_destination(self.folder.Value)
        except ValueError as error:
            self._showError(str(error))
            return
        media_format = "MP3" if self.format.Selection == 0 else "MP4"
        tools_dir = Path(__file__).resolve().parent / "dependencies" / "win64"
        self._announced.clear()
        self.progress.Value = 0
        self.status.Label = _("Preparando download.")
        ui.message(_("Preparando download."))
        self._setDownloading(True)
        self._worker = DownloadWorker(
            tools_dir, url, media_format, destination, self.playlist.Value,
            lambda value: wx.CallAfter(self._onProgress, value),
            lambda success, message: wx.CallAfter(self._onDone, success, message),
            lambda message: wx.CallAfter(self._onStatus, message),
            lambda index, total: wx.CallAfter(self._onPlaylistItem, index, total),
        )
        self._worker.start()

    def _onStatus(self, message):
        self.status.Label = message
        ui.message(message)

    def _onPlaylistItem(self, index, total):
        self._announced.clear()
        self.progress.Value = 0
        if total:
            message = _("Baixando item %(index)d de %(total)d.") % {
                "index": index, "total": total,
            }
        else:
            message = _("Baixando item %d da playlist.") % index
        self._onStatus(message)

    def _onProgress(self, value):
        self.progress.Value = value
        self.status.Label = _("Download: %d por cento.") % value
        for threshold in self.ANNOUNCE_AT:
            if value >= threshold and threshold not in self._announced:
                self._announced.add(threshold)
                ui.message(_("%d por cento.") % threshold)

    def _onDone(self, success, message):
        self._worker = None
        self._setDownloading(False)
        self.status.Label = message
        ui.message(message)
        if success:
            self.progress.Value = 100
            wx.MessageBox(message, "SoundTub", wx.OK | wx.ICON_INFORMATION, self)
        elif message != _("Download cancelado."):
            wx.MessageBox(message, _("Erro no SoundTub"), wx.OK | wx.ICON_ERROR, self)

    def _cancelDownload(self, event):
        if self._worker:
            self.status.Label = _("Cancelando download…")
            ui.message(_("Cancelando download."))
            self._worker.cancel()

    def _setDownloading(self, active):
        self.download.Enable(not active)
        self.cancel.Enable(active)
        self.url.Enable(not active)
        self.format.Enable(not active)
        self.playlist.Enable(not active)

    def _showError(self, message):
        self.status.Label = message
        ui.message(message)
        wx.MessageBox(message, _("SoundTub"), wx.OK | wx.ICON_ERROR, self)

    def _onClose(self, event):
        if self._worker:
            answer = wx.MessageBox(
                _("Há um download em andamento. Deseja cancelá-lo e fechar?"),
                _("SoundTub"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION, self,
            )
            if answer != wx.YES:
                event.Veto()
                return
            self._worker.cancel()
        self.Destroy()
        self._on_closed()

    def closeForNvdaExit(self):
        if self._worker:
            self._worker.cancel()
        self.Destroy()
