from .parser import Parser

class ScriptParser(Parser):
    
    def __init__(self, cookie):
        super().__init__(cookie)
        self.url = ''
        self.selector = None