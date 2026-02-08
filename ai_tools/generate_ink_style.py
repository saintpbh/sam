
import json
import urllib.request
import urllib.parse
import time
import os
import random

SERVER_ADDRESS = "127.0.0.1:8188"
CLIENT_ID = "chunhadoji_ink_agent"

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

def generate_ink_painting(character_info, output_path):
    character_name = character_info['name']
    details = character_info.get('desc', 'detailed historical chinese warrior')
    
    # INK PAINTING PROMPTS
    # Positive: Focus on traditional brush strokes but keeping the character design grounded in historical accuracy (Koei feel)
    positive_prompt = f"(monochrome:1.3), (traditional chinese ink painting:1.3), (sumi-e style:1.3), (rough brush strokes:1.2), (art by Koei Tecmo:1.2), (Romance of the Three Kingdoms character design:1.2), {character_name}, {details}, (black and white), stark contrast, majestic pose, historical atmosphere, masterpiece, best quality"
    
    # Negative: Avoid color, modern photorealism, and anime
    negative_prompt = "color, colorful, (anime:1.5), (cartoon:1.5), (3d render:1.3), (photorealistic:1.2), low quality, worst quality, blurry, text, watermark, signature, ugly, bad anatomy, simple background, smooth gradient"

    seed = random.randint(0, 2**32 - 1)

    # Simplified Workflow: Just SDXL Base Gen (No Upscale for speed/style)
    # Resolution: 832x1024 -> Perfect for portraits
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
                "cfg": 5.0, # Lower CFG for more "artistic" freedom with ink style
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
        "9": {
            "inputs": {
                "filename_prefix": "RTK_Ink_Style",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        },
        "13": {
            "inputs": {
                "images": ["8", 0]
            },
            "class_type": "PreviewImage"
        }
    }

    print(f"Generating [INK STYLE] for {character_name}...")
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
        if time.time() - start_time > 120: # Should be fast now
            print("Timeout")
            return False
        time.sleep(1)
    
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
    
    print("\n=== STARTING PRIORITY GENERATION (INK STYLE) ===")
    for char_data in characters:
        if isinstance(char_data, list):
            name = char_data[0]
            filename = char_data[1]
            original_desc = char_data[2] if len(char_data) > 2 else f"{name} from Three Kingdoms"
        else:
            name = char_data['name']
            filename = char_data['filename']
            original_desc = char_data.get('desc', f"{name} from Three Kingdoms")
        
        if name in priority_list:
            target = os.path.join(output_dir, filename)
            desc = f"{original_desc}, detailed historical chinese face, dignified expression, intricate armor"
            if generate_ink_painting({'name': name, 'desc': desc}, target):
                time.sleep(0.5)

    print("\n=== STARTING FULL BATCH (INK STYLE) ===")
    for char_data in characters:
        if isinstance(char_data, list):
            name = char_data[0]
            filename = char_data[1]
            original_desc = char_data[2] if len(char_data) > 2 else f"{name} from Three Kingdoms"
        else:
            name = char_data['name']
            filename = char_data['filename']
            original_desc = char_data.get('desc', f"{name} from Three Kingdoms")
        
        if name not in priority_list:
            target = os.path.join(output_dir, filename)
            desc = f"{original_desc}, detailed historical chinese face"
            if generate_ink_painting({'name': name, 'desc': desc}, target):
                time.sleep(0.5)
