import json
import urllib.request
import urllib.parse
import time
import os
import random

SERVER_ADDRESS = "127.0.0.1:8188"
CLIENT_ID = "chunhadoji_juggernaut_agent"

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

def generate_portrait(character_info, output_path):
    character_name = character_info['name']
    details = character_info.get('desc', 'detailed historical chinese warrior')
    
    # JUGGERNAUT SPECIFIC PROMPTS (Cinematic, Realistic Painting)
    # Using 'digital illustration' but focusing on historical painting style
    positive_prompt = f"epic digital illustration of {character_name}, {details}, romance of the three kingdoms style, (historical chinese painting style:1.2), (koei tecmo art style:1.2), intricate armor, majestic pose, cinematic lighting, highly detailed face, realistic texture, 8k resolution, masterpiece, best quality"
    
    negative_prompt = "(anime:1.5), (manga:1.5), (cartoon:1.5), (sketch:1.2), (3d render:1.3), (photorealistic:1.2), low quality, worst quality, blurry, text, watermark, signature, ugly, bad anatomy, deformed, disfigured, extra limbs, fused fingers, multiple people, simple background"

    seed = random.randint(0, 2**32 - 1)

    # Workflow using Juggernaut XL v9 + Ultimate SD Upscale (FAST MODE - 1.5x)
    workflow = {
        "4": {
            "inputs": {
                "ckpt_name": "Juggernaut-XL-v9.safetensors"
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
                "steps": 25, 
                "cfg": 6.0, # Juggernaut works well with lower CFG
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
                "cfg": 6.0,
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
                "filename_prefix": "RTK_Juggernaut",
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

    print(f"Generating [JUGGERNAUT REALISTIC] for {character_name}...")
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
    
    print("\n=== STARTING PRIORITY GENERATION (JUGGERNAUT) ===")
    for char_data in characters:
        if isinstance(char_data, list):
            name = char_data[0]
            filename = char_data[1]
        else:
            name = char_data['name']
            filename = char_data['filename']
            # Stronger description for Juggernaut
            original_desc = char_data.get('desc', f"{name} from Three Kingdoms")
            desc = f"{original_desc}, detailed historical chinese face, dignified expression, intricate armor"

        if name in priority_list:
            target = os.path.join(output_dir, filename)
            if generate_portrait({'name': name, 'desc': desc}, target):
                time.sleep(1)

    print("\n=== STARTING FULL BATCH (JUGGERNAUT) ===")
    for char_data in characters:
        if isinstance(char_data, list):
            name = char_data[0]
            filename = char_data[1]
        else:
            name = char_data['name']
            filename = char_data['filename']
            original_desc = char_data.get('desc', f"{name} from Three Kingdoms")
            desc = f"{original_desc}, detailed historical chinese face"
        
        if name not in priority_list:
            target = os.path.join(output_dir, filename)
            if generate_portrait({'name': name, 'desc': desc}, target):
                time.sleep(1)
