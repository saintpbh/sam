
import json
import urllib.request
import urllib.parse
import time
import os
import random

SERVER_ADDRESS = "127.0.0.1:8188"
CLIENT_ID = "chunhadoji_juggernaut_v10_agent"

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
    
    # JUGGERNAUT XL v10 & RTK 14 STYLE PROMPTS (Targeted Analysis)
    # The user wants specific "Modern Koei Style": Semi-realistic digital painting, dramatic lighting, detailed armor, dynamic poses.
    # v10 is even better at lighting and skin texture, so we emphasize that.
    positive_prompt = f"(art by Koei Tecmo:1.4), (Romance of the Three Kingdoms 14 style:1.4), (digital oil painting:1.3), {character_name}, {details}, (imposing historical chinese general:1.2), (intricate armor details:1.3), (realistic face texture:1.2), masculine features, serious expression, dramatic cinematic lighting, volumetrics, sharp focus, 8k resolution, masterpiece, best quality, dynamic pose"
    
    # STRONG Negative Prompt to kill Anime/Cartoon style
    negative_prompt = "(anime:1.6), (manga:1.6), (cartoon:1.6), (sketch:1.4), (cel shading:1.4), (lineart:1.4), (2D flat color:1.4), (3d render:1.2), (photorealistic:1.1), low quality, worst quality, blurry, text, watermark, signature, ugly, bad anatomy, deformed, disfigured, extra limbs, fused fingers, multiple people, simple background, grayscale"

    seed = random.randint(0, 2**32 - 1)

    # Workflow using Juggernaut XL v10 + Ultimate SD Upscale (Corrected Node Connections)
    workflow = {
        "4": {
            "inputs": {
                "ckpt_name": "Juggernaut-X-v10.safetensors"
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
                "cfg": 5.5, # v10 usually prefers lower CFG (3.0-6.0) for realism
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
                "cfg": 5.5, # Match base CFG
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
                "filename_prefix": "RTK_Juggernaut_v10",
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

    print(f"Generating [JUGGERNAUT v10] for {character_name}...")
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

    # Output directory
    output_dir = '/Users/proktv/.gemini/antigravity/scratch/chunhadoji/public/portraits/'
    os.makedirs(output_dir, exist_ok=True)
    
    # Priority List
    priority_list = ["Zhuge Liang", "Guan Yu", "Liu Bei", "Cao Cao"]
    
    print("\n=== STARTING PRIORITY GENERATION (JUGGERNAUT v10) ===")
    for char_data in characters:
        if isinstance(char_data, list):
            name = char_data[0]
            filename = char_data[1]
        else:
            name = char_data['name']
            filename = char_data['filename']
        if isinstance(char_data, list):
            # If list, format is [Name, Filename, Desc]
            original_desc = char_data[2] if len(char_data) > 2 else f"{name} from Three Kingdoms"
        else:
            original_desc = char_data.get('desc', f"{name} from Three Kingdoms")

        if name in priority_list:
            target = os.path.join(output_dir, filename)
            desc = f"{original_desc}, detailed historical chinese face, dignified expression, intricate armor"
            
            if generate_portrait({'name': name, 'desc': desc}, target):
                time.sleep(1)

    print("\n=== STARTING FULL BATCH (JUGGERNAUT v10) ===")
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
