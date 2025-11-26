
class Analysis():
    
    def run(self, data):
        if data['metric'] == 'cpu' and data['value'] > 50:
            return {
                "hostname": data['hostname'],
                "command": 1,
                "parameter": 10
            }
        elif data['metric'] == 'cpu' and data['value'] <= 50:
            return {
                "hostname": data['hostname'],
                "command": 1,
                "parameter": 5
            }
        else:
            return None