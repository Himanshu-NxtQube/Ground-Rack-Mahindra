from utils.error_codes import ErrorCodes
import shutil
import os

class ErrorBucket:
    def __init__(self):
        self.base_bucket_path = 'buckets/'

        for code in ErrorCodes:
            os.makedirs(os.path.join(self.base_bucket_path, str(code.value)), exist_ok=True)

    def add(self, type: ErrorCodes, image_path):
        bucket_path = os.path.join(self.base_bucket_path, str(type.value))
        shutil.copy(image_path, bucket_path)
    
    def add_partnumber(self, type: ErrorCodes, part_number):
        bucket_path = os.path.join(self.base_bucket_path, str(type.value))

        with open(os.path.join(bucket_path, 'part_numbers.txt'), 'a') as f:
            f.write(part_number + '\n')
