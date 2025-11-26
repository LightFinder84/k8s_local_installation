
class Analysis():
    
    def run(self, data):
        print(f"Running ananlysis with data: {data}")
        if data['metric'] == 'cpu' and float(data['value']) > 50:
            return {
                "hostname": data['hostname'],
                "command": 1,
                "parameter": 10
            }
        elif data['metric'] == 'cpu' and float(data['value']) <= 50:
            return {
                "hostname": data['hostname'],
                "command": 1,
                "parameter": 5
            }
        else:
            return None