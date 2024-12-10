import time
import random
from datetime import datetime


class DataGenerator:
    """Real-time data generator for aquaculture monitoring system"""
    
    def __init__(self):
        self.base_temperature = 26
        self.base_salinity = 30
        self.base_acidity = 7
    
    def generate_data(self, verbose: bool = True):
        """Generate random data with realistic variations"""
        timestamp = int(datetime.now().timestamp() * 1000)
        
        temperature = random.randint(15, 35)
        salinity = random.randint(50, 350)
        acidity = random.randint(4, 9)
        
        data = {
            "timestamp": timestamp,
            "temperature": temperature,
            "salinity": salinity,
            "acidity": acidity
        }

        if verbose:
            print("success...")
            print(data)

        return data
    

if __name__ == "__main__":

    generator = DataGenerator()
    while True:
        generator.generate_data()
        time.sleep(1)