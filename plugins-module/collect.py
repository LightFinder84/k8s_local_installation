import subprocess

class DataCollector:
        
    def get_cpu_usage(self):
        command = "top -bn1 | grep \"^%Cpu\" | awk '{print $2}'"
        value = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()
        if value == 'us,': value = '100.0'
        return value

    def get_memory_usage(self):
        command =  "free -m | awk '/^Mem:/ { printf(\"%.2f\", $3/$2 * 100) }'"
        value = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()
        return value
    
    def get_disk_read(self):
        command = "iostat -d -k 1 2 | awk 'NR>7 {read+=$3} END {print read}'"
        value = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()
        return value
    
    def get_disk_write(self):
        command = " iostat -d -k 1 2 | awk 'NR>7 {write+=$4} END {print write}'"
        value = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()
        return value
    
    def get_net_in(self):
        command = "ifstat -i enp0s8 1 1 | awk 'NR>2 {print $1}'"
        value = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()
        return value
    
    def get_net_out(self):
        command = "ifstat -i enp0s8 1 1 | awk 'NR>2 {print $2}'"
        value = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()
        return value
    
    def execute(self, metrics):
        print(f"Collecting data...")
        data = {}
        for metric in metrics:
            if metric == "cpu":
                data["cpu"] = self.get_cpu_usage()
            elif metric == "mem":
                data["mem"] = self.get_memory_usage()
            elif metric == "disk_read":
                data["disk_read"] = self.get_disk_read()
            elif metric == "disk_write":
                data["disk_write"] = self.get_disk_write()
            elif metric == "net_in":
                data["net_in"] = self.get_net_in()
            elif metric == "net_out":
                data["net_out"] = self.get_net_out()
        return data