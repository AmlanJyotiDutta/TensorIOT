import random 
import string
import logging
from random import choice
import boto3
from dotenv import load_dotenv
import json
        
class ParkingSlot: 
    def __init__(self, size = 2000 , parking_spot_size = (8, 12)):
        slot_num = size // (parking_spot_size[0] * parking_spot_size[1])
        self.slots = [None for _ in range(slot_num)]
    
    def _is_slot_empty(self, slot_num) -> bool :
        if slot_num >= len(self.slots): 
            raise ValueError(f'Slot number must be >=1 && < {len(self.slots)}')
        return self.slots[slot_num] is None 
    def find_empty_slot(self):
        for idx,slot in enumerate(self.slots):
            if slot is None:
                return idx
        return -1    
    def insert_slot(self, slot_num, car ): 
        try: 
            is_empty = self._is_slot_empty(slot_num)
            if is_empty : 
                self.slots[slot_num] = car 
                return slot_num 
            else: 
                return -1 
                
        except ValueError as ex:
            #logging.error("Failed to insert slot ", ex)
            return -1 
    
    def export_state(self,filename,write_to_s3 = False):
        parked_car_dict ={}
        for idx,car in enumerate(self.slots):
            parked_car_dict[car.license]=idx
        
            
        with open(filename,"w+") as fp:
            fp.write(json.dumps(parked_car_dict, indent = 4))
        
        if write_to_s3: 
            s3=boto3.client('s3')
            s3.upload_file(filename, 'amlan-tensor-iot-test-bucket', filename)
        
            
class Car: 
    def __init__(self, license = None):
        if license is None: 
            self.license = self._generate_license()
        else: 
            if len(license) > 7 : 
                raise ValueError(f"license number {license} must be equal to 7",)
            self.license = self.license
    def _generate_license(self): 
        res = ''.join(random.choices(string.ascii_uppercase +string.digits, k = 7))
        return res

    def __str__(self): 
        return f'[License [{self.license}]]'

    def park(self, slot: int, parking_slot):
        if parking_slot is None: 
            raise ValueError("Car cannot be parked without a parking slot ")
        park_status = parking_slot.insert_slot(slot, self)
        return park_status
        
def main():
    parking_slot = ParkingSlot()
    cars = [Car() for _ in range(21)]
    slot_nums = [i for i in range (22)]
    for car in cars: 
        random_slot = choice(slot_nums)
        park_status = car.park(random_slot, parking_slot)
        
        if  park_status !=-1 :
            print(f"Car {car} inserted successfully at slot {random_slot}")
        else: 
            print(f'random_slot {random_slot} car{car} failed . trying to insert in successive slots ')
            empty_slot = parking_slot.find_empty_slot() 
            if empty_slot != -1:
                assert(car.park(empty_slot,parking_slot)!=-1)
                print(f'Car {car} inserted successfully at {empty_slot}')
            else:
                print(f' Car {car} insertion failed , No empty slot available')
    parking_slot.export_state('state.json', write_to_s3 = True)
    
if __name__ == '__main__': 
    load_dotenv()
    main()
