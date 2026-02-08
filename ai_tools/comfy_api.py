import json
import urllib.request
import urllib.parse
import time
import os
import random

# ComfyUI API URL
SERVER_ADDRESS = "127.0.0.1:8188"
CLIENT_ID = "chunhadoji_agent"

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

def generate_portrait(character_name, output_path):
    # Dynamic actions/poses
    actions = [
        "drawing a longbow on horseback",
        "brandishing a massive spear in a war zone",
        "commanding an army with a heroic shout",
        "calmly fanning a feather fan in a pavilion",
        "slashing a sword with dynamic particle effects",
        "galloping heroically with a billowing cape",
        "standing with a resolute and visionary gaze",
        "engaging in an intense duel pose",
        "sitting on a wooden throne with supreme authority",
        "amidst falling cherry blossoms or burning embers"
    ]
    
    # ULTIMATE 2D ILLUSTRATION STYLE
    style_keywords = (
        "Masterpiece, top-quality digital 2D illustration, official Koei Romance of the Three Kingdoms 14 character art style, "
        "flat cel-shaded animation style, thick and clean lineart, vibrant but elegant colors, "
        "painterly details on armor and silk robes, sharp 2D vector-like look, "
        "dramatic anime lighting, clean background for transparency"
    )

    action = random.choice(actions)
    seed = random.randint(0, 2**32 - 1)

    # WORKFLOW: Checkpoint -> (Optional LoRA) -> KSampler -> VAE Decode -> Upscale with Model -> Save
    workflow = {
        "3": {
            "inputs": {
                "seed": seed,
                "steps": 25,
                "cfg": 7.0,
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
        "4": {
            "inputs": {
                "ckpt_name": "Juggernaut-XL-v9.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": 832,
                "height": 1024,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": f"{style_keywords}. Character: {character_name}. Action: {action}.",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": "photorealistic, 3d, realistic, photography, skin texture, real-life, octane render, unreal engine, depth of field, blurry, distorted, messy, watermark, text, out of frame",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            },
            "class_type": "VAEDecode"
        },
        # ADDED: Upscale with High-End Model
        "10": {
            "inputs": {
                "upscale_model": ["11", 0],
                "image": ["8", 0]
            },
            "class_type": "ImageUpscaleWithModel"
        },
        "11": {
            "inputs": {
                "model_name": "RealESRGAN_x4plus_anime_6B.pth"
            },
            "class_type": "UpscaleModelLoader"
        },
        "9": {
            "inputs": {
                "filename_prefix": "RTK_Ultimate",
                "images": ["10", 0]
            },
            "class_type": "SaveImage"
        }
    }

    print(f"Generating [ULTIMATE 2D + UPSCALE] for {character_name}...")
    try:
        prompt_res = queue_prompt(workflow)
        prompt_id = prompt_res['prompt_id']
    except Exception as e:
        print(f"Queue failed: {e}")
        return False
    
    start_time = time.time()
    while True:
        try:
            history = get_history(prompt_id)
            if prompt_id in history: break
        except: pass
        if time.time() - start_time > 600: return False # 10 min timeout for upscale
        time.sleep(4)
    
    outputs = history[prompt_id]['outputs']
    for node_id in outputs:
        node_output = outputs[node_id]
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                with open(output_path, "wb") as f:
                    f.write(image_data)
                print(f"Success! High-Res saved to {output_path}")
                return True
    return False

if __name__ == "__main__":
    list_path = '/Users/proktv/.gemini/antigravity/scratch/chunhadoji/ai_tools/character_list.json'
    with open(list_path, 'r') as f:
        characters = json.load(f)
    output_dir = '/Users/proktv/.gemini/antigravity/scratch/chunhadoji/public/portraits/'
    
    for name, filename in characters:
        target_path = os.path.join(output_dir, filename)
        print(f"\n--- [UPSCALE BATCH] {name} ---")
        try:
            generate_portrait(name, target_path)
            time.sleep(2)
        except Exception as e:
            print(f"Critical error for {name}: {e}")
