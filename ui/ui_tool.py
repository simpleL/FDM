import platform
from ui_tool_osx import UIToolOSX

class UITool:
    def __init__(self):
        self.__system = platform.system()
        if self.__system == 'Darwin':
            self.__tool_private = UIToolOSX()
        else:
            self.__tool_private = None

    def notify(self, title, text):
        if not self.__tool_private:
            print "UITool not prepared for %s"%(self.__system)
            return

        self.__tool_private.notify(title, text)