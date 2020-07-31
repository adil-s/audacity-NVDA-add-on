"""
audacity App Module.

An add-on for NVDA
license:   release under gpl
author: adilhusain shaikh
copyright 2020
"""

import re
import api
import appModuleHandler
import controlTypes
import NVDAObjects.IAccessible
import ui
import windowUtils
import winUser
from NVDAObjects.IAccessible import IAccessible
from scriptHandler import script


class AppModule(appModuleHandler.AppModule):
    def chooseNVDAObjectOverlayClasses(self, obj, clsList):
        if obj.windowControlID == 1003 and obj.role == controlTypes.ROLE_TABLEROW:
            clsList.insert(0, EnhanceTrackWindow)
        if obj.windowControlID == -31982 and obj.role == controlTypes.ROLE_DROPDOWNBUTTON:
            clsList.insert(0, PlayMeter)
        if obj.windowControlID == 0\
           and obj.windowClassName == 'msctls_statusbar32'\
           and obj.role == controlTypes.ROLE_STATICTEXT\
           and obj.IAccessibleChildID == 2:
            clsList.insert(0, TrackStatus)
        if obj.windowControlID == 1003 and obj.role == controlTypes.ROLE_TABLEROW:
            clsList.insert(0, trackState)
        if obj.role == controlTypes.ROLE_STATICTEXT and obj.windowControlID == 2801:
            clsList.insert(0, AudioPosition)
        if obj.role == controlTypes.ROLE_STATICTEXT \
           and obj.windowControlID == 2705:
            clsList.insert(0, SelectionTime)


class EnhanceTrackWindow(IAccessible):
    def message(self, text):
        import speech
        import braille
        braille.handler.message(text)
        speech.speakMessage(text)

    def getStartSelection(self):
        try:
            mainHwnd = windowUtils.findDescendantWindow(api.getForegroundObject().windowHandle, True, 2)
            selStartObj = NVDAObjects.IAccessible.getNVDAObjectFromEvent(
                windowUtils.findDescendantWindow(mainHwnd, True, 2705), winUser.OBJID_CLIENT, 0)
            selStartText = self.formatTime(selStartObj.name)
            self.message(selStartText)
        except LookupError:
            return False

    def getEndSelection(self):
        try:
            mainHwnd = windowUtils.findDescendantWindow(api.getForegroundObject().windowHandle, True, 2)
            selEndObj = NVDAObjects.IAccessible.getNVDAObjectFromEvent(
                windowUtils.findDescendantWindow(mainHwnd, True, 2708), winUser.OBJID_CLIENT, 0)
            selEndText = self.formatTime(selEndObj.name)
            self.message(selEndText)
        except LookupError:
            return False

    def getAudioPosition(self):
        fgObj = api.getForegroundObject()
        tbObj = fgObj.children[-1]
        timeObj = tbObj.children[-1]
        audioPos = timeObj.children[1]
        audioPosText = self.formatTime(audioPos.name)
        if audioPosText != "":
            self.message(audioPosText)

    def formatTime(self, text):
        time = re.findall(r"[\d\.]*", text)
        time = [t for t in time if t != '']
        formattedTime = []
        for t in time:
            try:
                i = int(t)
                if i > 0:
                    formattedTime.append(str(i))
            except ValueError:
                i = float(t)
                formattedTime.append(str(i))
        return ':'.join(formattedTime)

    @script(gesture="kb:[")
    def script_startSelection(self, gesture):
        gesture.send()
        self.message("selection start")
        self.getStartSelection()

    @script(gesture="kb:]")
    def script_endSelection(self, gesture):
        gesture.send()
        self.message("selection end")
        self.getEndSelection()

    @script(gesture="kb:nvda+shift+a")
    def script_sayAudioPosition(self, gesture):
        self.getAudioPosition()

    def script_playStop(self, gesture):
        gesture.send()
        self.getAudioPosition()

    @script(gesture="kb:p")
    def script_playPause(self, gesture):
        gesture.send()
        self.getAudioPosition()

    @script(gesture="kb:nvda+shift+s")
    def script_readSelection(self, gesture):
        try:
            self.message("selection from ")
            self.getStartSelection()
            self.message(" to ")
            self.getEndSelection()
        except LookupError:
            self.message("no selection")


class PlayMeter(IAccessible):
    def event_nameChange(self):
        ui.message(" working")


class trackState(IAccessible):
    def event_valueChange(self):
        ui.message(self.value)


class TrackStatus(IAccessible):
    status = ''

    def event_nameChange(self):
        if self.name != TrackStatus.status:
            ui.message(self.name)
        TrackStatus.status = self.name


class AudioPosition(IAccessible):
    pos = 0

    def event_nameChange(self):
        if self.name != AudioPosition.pos:
            ui.message(self.name)
        AudioPosition.pos = self.name


class SelectionTime(IAccessible):
    def event_nameChange(self):
        ui.message(self.name)
