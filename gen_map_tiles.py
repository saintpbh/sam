import json
import time
import os
from urllib import request, parse

def queue_prompt(prompt):
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req = request.Request("http://127.0.0.1:8188/prompt", data=data)
    with request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def get_history(prompt_id):
    while True:
        try:
            with request.urlopen(f"http://127.0.0.1:8188/history/{prompt_id}") as response:
                history = json.loads(response.read().decode('utf-8'))
                if prompt_id in history:
                    return history[prompt_id]
        except:
            pass
        time.sleep(1)

def save_image(image_info, target_path):
    filename = image_info['filename']
    subfolder = image_info['subfolder']
    img_url = f"http://127.0.0.1:8188/view?filename={parse.quote(filename)}&subfolder={parse.quote(subfolder)}&type=output"
    with request.urlopen(img_url) as img_response:
        with open(target_path, "wb") as f:
            f.write(img_response.read())

tile_prompt_template = """
{
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "cfg": 8, "denoise": 1, "latent_image": ["5", 0], "model": ["4", 0],
            "negative": ["7", 0], "positive": ["6", 0], "sampler_name": "euler",
            "scheduler": "normal", "seed": 42, "steps": 20
        }
    },
    "4": { "class_type": "CheckpointLoaderSimple", "inputs": { "ckpt_name": "sd_v1-5.safetensors" } },
    "5": { "class_type": "EmptyLatentImage", "inputs": { "batch_size": 1, "height": 512, "width": 512 } },
    "6": { "class_type": "CLIPTextEncode", "inputs": { "clip": ["4", 1], "text": "" } },
    "7": { "class_type": "CLIPTextEncode", "inputs": { "clip": ["4", 1], "text": "text, watermark, blurry, low quality" } },
    "8": { "class_type": "VAEDecode", "inputs": { "samples": ["3", 0], "vae": ["4", 2] } },
    "9": { "class_type": "SaveImage", "inputs": { "filename_prefix": "Tile", "images": ["8", 0] } }
}
"""

rows = 5
cols = 8
save_dir = "/Users/proktv/.gemini/antigravity/scratch/chunhadoji/public/tiles"

for r in range(rows):
    for c in range(cols):
        tile_name = f"tile_{r}_{c}.png"
        target_path = os.path.join(save_dir, tile_name)
        
        if os.path.exists(target_path):
            continue
            
        # Regional prompt logic
        region_desc = "Central plains, ancient walled city, bustling life"
        if r == 0: region_desc = "Northern steppe, dry desert mountains, Great Wall remains"
        elif r >= 3: region_desc = "Southern lush jungle, massive rivers, misty mountains"
        
        if c <= 1: region_desc += ", western high rugged peaks"
        elif c >= 6: region_desc += ", eastern coastline and wavy hills"
        
        prompt_text = f"An ancient Chinese map detail, Three Kingdoms era, {region_desc}, ink wash painting style, traditional brush strokes, weathered paper texture, masterpiece, high details"
        
        workflow = json.loads(tile_prompt_template)
        workflow["6"]["inputs"]["text"] = prompt_text
        workflow["3"]["inputs"]["seed"] = 1000 + (r * cols + c)
        
        print(f"Generating TILE [{r},{c}]: {tile_name}...")
        res = queue_prompt(workflow)
        pid = res['prompt_id']
        history = get_history(pid)
        
        img_info = history['outputs']['9']['images'][0]
        save_image(img_info, target_path)
        print(f"Saved {tile_name}")

print("All 40 tiles generated successfully!")
