# coding: utf-8
import requests
import base64
import io
from PIL import Image
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()


class StableDiffsuionAPI:
    def __init__(self):
        self.url = "http://127.0.0.1:7860"
        self.sd_model_checkpoint = "pixlAnimeCartoonComic_v10"  # 模型
        self.steps = 20     # 步数
        self.width = 512    # 默认宽度
        self.height = 512   # 默认高度
        self.seed = -1      # 中子数，随机性
        self.samples = 1    # 返回的图像数量
        self.batch_size = 1     # 每批生成的数量
        self.sampler_name = "Euler a"       # 采样方式: DPM++ 2M Karras
        self.cfg_scale = 7      # 提示词相关性
        self.denoising_strength = 0.5   # 去噪强度
        self.restore_faces = True   # 脸部修复
        self.save_images = True     # 保存图片至本地


    # 测试API连通性
    def get_api_status(self):
        url = f'{self.url}/docs'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                logger.info('API 连接成功')
                return True
            else:
                logger.error(f'API 连接失败，状态码：{response.status_code}')
                return False

        except Exception as e:
            logger.error(f'API 连接失败：{e}')
            return False


    # 模型、Lora列表
    def get_models_list(self):
        model_url = f'{self.url}/sdapi/v1/sd-models'
        lora_url = f'{self.url}/sdapi/v1/loras'

        response_model = requests.get(model_url).json()
        response_lora = requests.get(lora_url).json()

        model_list = [i['model_name'] for i in response_model]
        lora_list = [i['path'] for i in response_lora]

        logger.info(f'模型列表: {model_list}')
        logger.info(f'Lora列表: {lora_list}')


    # 重载模型
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
                    logger.info('模型重载成功')

        except Exception as e:
            logger.error(f'模型重载失败')


    # 图像转Base64
    def img_to_base64(self, img_path):
        logger.info("正在将图像转换成Base64...")
        with open(img_path, 'rb') as img_file:
            base64_string = base64.b64encode(img_file.read()).decode('utf-8')
        return base64_string


    # Base64转图像
    def base64_to_img(self, base64_string, img_path):
        logger.info("正在将Base64转换成图像...")
        image_byte = base64.b64decode(base64_string)
        img = Image.open(io.BytesIO(image_byte))
        img.save(img_path)


    # 读取Stable Diffusion 生成的图片信息
    def get_sd_img_info(self, img_path):
        img_base64 = self.img_to_base64(img_path)
        url = f'{self.url}/sdapi/v1/png-info'
        payload = {
            "image": img_base64
        }
        img_info = requests.post(url, json=payload).json()
        return img_info
    

    # 读取普通图片信息
    def get_img_info(self, img_path):
        logger.info('正在获取图片信息...')
        img = Image.open(img_path)
        width, height = img.size
        logger.info(f'图片宽度：{width}，图片高度：{height}')
        return width, height


    # 文生图
    def txt2img(self, prompt):
        url = f'{self.url}/sdapi/v1/txt2img'
        payload = {
            "prompt": f'{prompt}, simple anime style, 2D, celshading, thick lineart, heavy black ink lines, posterized, flat color, celshading, toonshading, Cartoon Rendering, Flat Shading, Graphic Novel Style, minimal shading, flat shading, hard color shading',   # 正向提示词
            "negative_prompt": "text, watermark, negativeXL_D",    # 反向提示词
            "override_settings":{
                "sd_model_checkpoint": self.sd_model_checkpoint,
            },
            "steps": self.steps,
            "width": self.width,
            "height": self.height,
            "seed": self.seed,     
            "samples": self.samples,
            "batch_size": self.batch_size,    
            "sampler_name": self.sampler_name,
            "cfg_scale": self.cfg_scale,
            "restore_faces": self.restore_faces,  
            "save_images": self.save_images,
        }

        requests.post(url, json=payload)
        logger.info(f'图像生成成功')


    # 图片风格转换
    def img_redraw(self, img_path):
        logger.info('正在进行风格转换...')

        img_info = self.get_img_info(img_path)
        width, height = img_info
        
        while width >= 1000 or height >= 1000:  # 防止原图尺寸过大，导致显存不足报错
            width /= 2
            height /= 2

        img_base64 = self.img_to_base64(img_path)

        url = f'{self.url}/sdapi/v1/img2img'
        payload = {
            "init_images": [str(img_base64)],
            "prompt": "simple anime style, 2D, celshading, thick lineart, heavy black ink lines, posterized, flat color, celshading, toonshading, Cartoon Rendering, Flat Shading, Graphic Novel Style, minimal shading, flat shading, hard color shading",
            "negative_prompt": "text, watermark, negativeXL_D",
            "override_settings":{
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
            logger.info(f'图像生成成功')
        else:
            logger.error(f'图像生成失败：{response.text}')


if __name__ == '__main__':
    start = StableDiffsuionAPI()

    if start.get_api_status() is True:
        start.reload_model()
        start.get_models_list()

        while True:
            imgs_path = "E:\\tmp"
            for i in os.listdir(imgs_path):
                img_path = imgs_path + '\\' + i
                start.img_redraw(img_path)
