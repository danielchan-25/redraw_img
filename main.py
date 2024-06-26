# coding: utf-8
import requests
import base64
import io
from PIL import Image
import logging
import os
import configparser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()


class StableDiffsuionAPI:
    def __init__(self):
        # Read configuration file
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.img_dir_path = config.get('global', 'img_dir_path')
        self.url = config.get('global', 'url')
        self.sd_model_checkpoint = config.get('global', 'sd_model_checkpoint')
        self.prompt = config.get('global', 'prompt')
        self.negative_prompt = config.get('global', 'negative_prompt')
        self.steps = config.getint('global', 'steps')
        self.seed = config.getint('global', 'seed')
        self.samples = config.getint('global', 'samples')
        self.batch_size = config.getint('global', 'batch_size')
        self.sampler_name = config.get('global', 'sampler_name')
        self.cfg_scale = config.getint('global', 'cfg_scale')
        self.denoising_strength = config.getfloat('global', 'denoising_strength')
        self.restore_faces = config.getboolean('global', 'restore_faces')
        self.save_images = config.getboolean('global', 'save_images')

    # Test API connectivity
    def get_api_status(self):
        url = f'{self.url}/docs'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                logger.info('API connection successful')
                return True
            else:
                logger.error(f'API connection failed,status code:{response.status_code}')
                return False

        except Exception as e:
            logger.error(f'API connection failed:{e}')
            return False

    # Read model list,Lora list
    def get_models_list(self):
        model_url = f'{self.url}/sdapi/v1/sd-models'
        lora_url = f'{self.url}/sdapi/v1/loras'

        response_model = requests.get(model_url).json()
        response_lora = requests.get(lora_url).json()

        model_list = [i['model_name'] for i in response_model]
        lora_list = [i['path'] for i in response_lora]

        logger.info(f'Model List: {model_list}')
        logger.info(f'Lora List: {lora_list}')

    # Overloaded model
    def reload_model(self):
        model_url = f'{self.url}/sdapi/v1/refresh-checkpoints'
        lora_url = f'{self.url}/sdapi/v1/refresh-loras'

        url_list = [model_url, lora_url]

        payload = {
            "accept": "application/json",
        }
        try:
            for i in url_list:
                response = requests.post(url=i, json=payload)
                if response.status_code == 200:
                    logger.info('Model reloaded successfully')

        except Exception as e:
            logger.error(f'Model reload failed: {e}')

    # Image to Base64
    def img_to_base64(self, img_path):
        logger.info("Converting image to Base64...")
        with open(img_path, 'rb') as img_file:
            base64_string = base64.b64encode(img_file.read()).decode('utf-8')
        return base64_string

    # Base64 to Image
    def base64_to_img(self, base64_string, img_path):
        logger.info("Converting Base64 to image...")
        image_byte = base64.b64decode(base64_string)
        img = Image.open(io.BytesIO(image_byte))
        img.save(img_path)

    # Load image information generated by Stable Diffusion
    def get_sd_img_info(self, img_path):
        img_base64 = self.img_to_base64(img_path)
        url = f'{self.url}/sdapi/v1/png-info'
        payload = {
            "image": img_base64
        }
        img_info = requests.post(url, json=payload).json()
        return img_info

    # Load image information
    def get_img_info(self, img_path):
        logger.info('Loading image information...')
        img = Image.open(img_path)
        width, height = img.size
        logger.info(f'Image width:{width}, Image height:{height}')
        return width, height

    # Image style conversion
    def img_redraw(self, img_path):
        logger.info(f'Style transfer in progress... {img_path}')

        img_info = self.get_img_info(img_path)
        width, height = img_info

        while width >= 1000 or height >= 1000:  # Prevent image size from being too large, resulting in insufficient video memory and errors.
            width /= 2
            height /= 2

        img_base64 = self.img_to_base64(img_path)

        url = f'{self.url}/sdapi/v1/img2img'
        payload = {
            "init_images": [img_base64],
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "override_settings": {
                "sd_model_checkpoint": self.sd_model_checkpoint,
            },
            "steps": self.steps,
            "width": width,
            "height": height,
            "seed": self.seed,
            "sampler_name": self.sampler_name,
            "cfg_scale": self.cfg_scale,
            "denoising_strength": 0.5,
            "restore_faces": False,
            "save_images": self.save_images,
        }
        response = requests.post(url=url, json=payload)
        if response.status_code == 200:
            logger.info(f'Image generated successfully')
        else:
            logger.error(f'Image generation failed: {response.text}')


if __name__ == '__main__':
    start = StableDiffsuionAPI()

    if start.get_api_status() is True:
        start.reload_model()
        start.get_models_list()

        while True:
            for i in os.listdir(start.img_dir_path):
                if i.endswith('.jpg') or i.endswith('png'):
                    img_path = os.path.join(start.img_dir_path, i)
                    start.img_redraw(img_path)
