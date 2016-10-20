# -*- coding: utf-8 -*-

import os, sys
from screenshoter import Screenshoter
from scripter import Scripter
from uploader import Uploader


class Screen():
    def __init__(self, selfdir):
        self.sefdir = selfdir
        
    def main(self):
        Screenshoter(self.sefdir).start()
        Scripter(selfdir).start()
        Uploader(selfdir).start()

if __name__ == '__main__':
    selfdir = os.path.abspath(os.path.dirname(__file__)) 
    Screen(selfdir).main()
    