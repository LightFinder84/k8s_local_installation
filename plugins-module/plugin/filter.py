from base import BasePlugin

class FilterNet(BasePlugin):
    def initialize(self):
        self.prev_data = None
        print("[FilterNet Plugin] initialized")
        
    def run(self, data):
        print("[FilterNet Plugin] running!")
        if 'net_in' in data:
            del data['net_in']
        if 'net_out' in data:
            del data['net_out']
        
        return data
        
    def finalize(self):
        self.prev_data = None
        print("[FilterNet Plugin] finalized")