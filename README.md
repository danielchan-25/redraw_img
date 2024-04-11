# redraw_img

> This is a program that redraws pictures. The program will read all files in `img_dir_path` in `config.ini` and then perform style conversion

## Installation

1. Clone Repository

   ```shell
   git clone https://github.com/danielchan-25/redraw_img.git
   ```

2. Install dependencies

   ```shell
   pip install -r requirements.txt
   ```

## Usage

```shell
python main.py
```

## Setting

See  `config.ini`

| Argument              | Type  | Description                      | Example               |
| --------------------- | ----- | -------------------------------- | --------------------- |
| `url`                 | str   | STable Diffusion API Url address | http://127.0.0.1:7860 |
| `img_dir_path`        | str   | Image Dir Path                   | E:\\temp              |
| `sd_model_checkpoint` | str   | Model Name                       | v1-5-pruned-emaonly   |
| `steps`               | int   | Step count                       | 20                    |
| `width`               | int   | Image width                      | 512                   |
| `height`              | int   | Image height                     | 512                   |
| `seed`                | int   | seed                             | -1                    |
| `samples`             | int   | samples                          | 1                     |
| `batch_size`          | int   | batch size                       | 1                     |
| `sampler_name`        | str   | sampler name                     | Euler a               |
| `cfg_scale`           | int   | Prompt word relevance            | 7                     |
| `denoising_strength`  | float | denoising strength               | 0.7                   |
| `restore_faces`       | bool  | restore faces                    | True                  |
| `save_images`         | bool  | save images to local             | True                  |

