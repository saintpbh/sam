import json
import urllib.request
import urllib.parse
import time
import os
import random

SERVER_ADDRESS = "127.0.0.1:8188"
CLIENT_ID = "chunhadoji_pony_agent"

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": CLIENT_ID}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{SERVER_ADDRESS}/prompt", data=data)
    with urllib.request.urlopen(req) as f:
        return json.loads(f.read().decode('utf-8'))

def get_history(prompt_id):
    with urllib.request.urlopen(f"http://{SERVER_ADDRESS}/history/{prompt_id}") as f:
        return json.loads(f.read().decode('utf-8'))

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"http://{SERVER_ADDRESS}/view?{url_values}") as f:
        return f.read()

def generate_pony_portrait(character_info, output_path):
    character_name = character_info['name']
    details = character_info.get('desc', 'ornate Han dynasty armor and silk robes, detailed face, majestic pose')
    
    # Pony Specific Prompting - TARGETED ASIAN/KOEI STYLE
    # Increased style weight, added explicit racial/aesthetic tags
    positive_prompt = f"score_9, score_8_up, score_7_up, (masterpiece:1.2), (high quality), official art, (romance of the three kingdoms style:1.4), (art by Koei Tecmo:1.3), (realistic asian face:1.2), (chinese man:1.1), (historical chinese armor:1.2), {character_name}, {details}, looking at viewer, standalone character, white background, centered, dynamic 2D illustration, intricate details, best quality"
    
    negative_prompt = "score_6, score_5, score_4, (low quality:1.4), (worst quality:1.4), (monochrome:1.1), (3d render:1.2), (western face:1.4), (caucasian:1.4), (anime face:1.2), bad anatomy, text, watermark, signature, blurry, multiple people, messy background, simple background"

    seed = random.randint(0, 2**32 - 1)

    # Workflow using Pony V6 + Ultimate SD Upscale (FAST MODE - 1.5x)
    workflow = {
        "4": {
            "inputs": {
                "ckpt_name": "pony_v6_xl.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "6": {
            "inputs": {
                "text": positive_prompt,
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": negative_prompt,
                "clip": ["4", 1] 
            },
            "class_type": "CLIPTextEncode"
        },
        "5": {
            "inputs": {
                "width": 832,
                "height": 1024,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "3": {
            "inputs": {
                "seed": seed,
                "steps": 20, 
                "cfg": 6.5, # Slightly lowered CFG for better prompt adherence without burning
                "sampler_name": "dpmpp_2m_sde",
                "scheduler": "karras",
                "denoise": 1,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "8": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            },
            "class_type": "VAEDecode"
        },
        "11": {
            "inputs": {
                "model_name": "RealESRGAN_x4plus_anime_6B.pth"
            },
            "class_type": "UpscaleModelLoader"
        },
        "12": {
            "inputs": {
                "upscale_by": 1.5, 
                "seed": seed,
                "steps": 12,
                "cfg": 6.5,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": 0.35,
                "mode_type": "Chess",
                "tile_width": 1024,
                "tile_height": 1024,
                "mask_blur": 8,
                "tile_padding": 32,
                "seam_fix_mode": "None",
                "seam_fix_denoise": 1,
                "seam_fix_width": 64,
                "seam_fix_mask_blur": 8,
                "seam_fix_padding": 16,
                "force_uniform_tiles": True,
                "tiled_decode": False,
                "image": ["8", 0],
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "vae": ["4", 2],
                "upscale_model": ["11", 0]
            },
            "class_type": "UltimateSDUpscale"
        },
        "9": {
            "inputs": {
                "filename_prefix": "RTK_Pony_FixedStyle",
                "images": ["12", 0]
            },
            "class_type": "SaveImage"
        },
        "13": {
            "inputs": {
                "images": ["12", 0]
            },
            "class_type": "PreviewImage"
        }
    }

    print(f"Generating [FIXED STYLE] for {character_name}...")
    try:
        prompt_res = queue_prompt(workflow)
        if 'error' in prompt_res:
             print(f"Server Error: {prompt_res['error']}")
             return False
        prompt_id = prompt_res['prompt_id']
    except Exception as e:
        print(f"Queue Exception: {e}")
        return False
    
    start_time = time.time()
    while True:
        try:
            history = get_history(prompt_id)
            if prompt_id in history: break
        except: pass
        if time.time() - start_time > 600:
            print("Timeout")
            return False
        time.sleep(2)
    
    outputs = history[prompt_id]['outputs']
    for node_id in outputs:
        node_output = outputs[node_id]
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                with open(output_path, "wb") as f:
                    f.write(image_data)
                print(f"Success -> {output_path}")
                return True
    return False

if __name__ == "__main__":
    char_file = '/Users/proktv/.gemini/antigravity/scratch/chunhadoji/ai_tools/character_list.json'
    with open(char_file, 'r') as f:
        characters = json.load(f)

    output_dir = '/Users/proktv/.gemini/antigravity/scratch/chunhadoji/public/portraits/'
    os.makedirs(output_dir, exist_ok=True)
    
    priority_list = ["Zhuge Liang", "Guan Yu", "Liu Bei", "Cao Cao"]
    
    print("\n=== RESTARTING PRIORITY GENERATION (FIXED STYLE) ===")
    for char_data in characters:
        if isinstance(char_data, list):
            name = char_data[0]
            filename = char_data[1]
            desc = f"{name} from Romance of the Three Kingdoms, historical warrior"
        else:
            name = char_data['name']
            filename = char_data['filename']
            # ENHANCED DESCRIPTION FOR BETTER STYLE MATCH
            original_desc = char_data.get('desc', f"{name} from Three Kingdoms")
            desc = f"{original_desc}, detailed historical chinese face, dignified expression"

        if name in priority_list:
            target = os.path.join(output_dir, filename)
            if generate_pony_portrait({'name': name, 'desc': desc}, target):
                time.sleep(1)

    print("\n=== RESTARTING FULL BATCH (FIXED STYLE) ===")
    for char_data in characters:
        if isinstance(char_data, list):
            name = char_data[0]
            filename = char_data[1]
            desc = f"{name} from Romance of the Three Kingdoms, historical warrior"
        else:
            name = char_data['name']
            filename = char_data['filename']
            original_desc = char_data.get('desc', f"{name} from Three Kingdoms")
            desc = f"{original_desc}, detailed historical chinese face"
        
        if name not in priority_list:
            target = os.path.join(output_dir, filename)
            if generate_pony_portrait({'name': name, 'desc': desc}, target):
                time.sleep(1)
