from base import BasePlugin

class HelloPlugin(BasePlugin):
    def initialize(self):
        print("[HelloPlugin] initialized")
        
    def run(self, data):
        print("[HelloPlugin] run... Hello!")
        
    def finalize(self):
        print("[HelloPlugin] finalized")