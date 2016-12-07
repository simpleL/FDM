import Foundation
import objc
import AppKit
import sys

class UIToolOSX:
    def __init__(self):
        self.__NSUserNotification = objc.lookUpClass('NSUserNotification')
        self.__NSUserNotificationCenter = objc.lookUpClass('NSUserNotificationCenter')

    def notify(self, title, text):
        notification = self.__NSUserNotification.alloc().init()
        notification.setTitle_(title)
        notification.setInformativeText_(text)
        notification.setSoundName_("NSUserNotificationDefaultSoundName")
        self.__NSUserNotificationCenter.defaultUserNotificationCenter().scheduleNotification_(notification)

