from google.cloud import vision
import os
import io
from utils.logger import get_logger

logger = get_logger(__name__)

class OCRClient:
        
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './credentials/GoogleVisionCredential.json'
        self.client = vision.ImageAnnotatorClient()
        logger.info("OCRClient initialized")
    
    def get_annotations(self, image_path: str):
        # image = cv2.imread(image_path)
        # if image is None:
        #     raise ValueError(f"Error loading image: {image_path}")

        # # Convert image to bytes for Google Vision API
        # _, image_encoded = cv2.imencode('.jpg', image)
        # content = image_encoded.tobytes()
        try:
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()
            response = self.client.text_detection(image=vision.Image(content=content))
            annotations = response.text_annotations
            return annotations
        except Exception:
            logger.error(f"Error in OCRClient.get_annotations")
            return None
    
if __name__=='__main__':
    ocr_client = OCRClient()
    res = ocr_client.get_annotations('annotations.png')
    print(res)