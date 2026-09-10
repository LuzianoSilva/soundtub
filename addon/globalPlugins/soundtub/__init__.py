import addonHandler
import globalPluginHandler
import gui as nvdaGui
import wx
from scriptHandler import script

from .gui import SoundTubDialog

addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    _dialog = None

    @script(
        description=_("Abrir o SoundTub"),
        category=_("SoundTub"),
        gesture="kb:NVDA+alt+y",
    )
    def script_openSoundTub(self, gesture):
        wx.CallAfter(self._showDialog)

    def _showDialog(self):
        if self._dialog:
            self._dialog.Raise()
            self._dialog.SetFocus()
            return
        nvdaGui.mainFrame.prePopup()
        self._dialog = SoundTubDialog(nvdaGui.mainFrame, self._onDialogClosed)
        self._dialog.Show()

    def _onDialogClosed(self):
        self._dialog = None
        nvdaGui.mainFrame.postPopup()

    def terminate(self):
        if self._dialog:
            self._dialog.closeForNvdaExit()
            self._dialog = None
        super().terminate()
