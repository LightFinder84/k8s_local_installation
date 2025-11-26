
class Analysis():
    
    def run(self, data):
        if 'cpu' in data and data['cpu'] > 50:
            return {
                "hostname": data['hostname'],
                "command": 1,
                "parameter": 10
            }
        elif 'cpu' in data and data['cpu'] <= 50:
            return {
                "hostname": data['hostname'],
                "command": 1,
                "parameter": 5
            }
        else:
            return None