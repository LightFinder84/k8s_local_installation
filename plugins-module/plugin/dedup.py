from base import BasePlugin

class DeDupPlugin(BasePlugin):
    def initialize(self):
        self.prev_data = None
        print("[DeDupPlugin] initialized")
        
    def run(self, data):
        print("[DeDupPlugin] running!")
        if data != self.prev_data:
            data['send'] = True
            self.prev_data = data
        else:
            data['send'] = False
        
        return data
        
    def finalize(self):
        self.prev_data = None
        print("[DeDupPlugin] finalized")