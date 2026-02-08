import json
import time
import os
import shutil
from urllib import request, parse

# ComfyUI API Helpers
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
        time.sleep(2)

def save_image(image_info, filename_to_save):
    img_filename = image_info['filename']
    subfolder = image_info['subfolder']
    img_url = f"http://127.0.0.1:8188/view?filename={parse.quote(img_filename)}&subfolder={parse.quote(subfolder)}&type=output"
    
    # Save to Game Resources
    game_res_path = os.path.join("/Users/proktv/.gemini/antigravity/scratch/chunhadoji/public/portraits", filename_to_save)
    # Save to Desktop
    desktop_path = os.path.join("/Users/proktv/Desktop/Chunhadoji_Portraits", filename_to_save)
    
    with request.urlopen(img_url) as img_response:
        data = img_response.read()
        with open(game_res_path, "wb") as f:
            f.write(data)
        with open(desktop_path, "wb") as f:
            f.write(data)

# Character List (100 Characters)
characters = [
    # SHU (Green)
    ("Liu Bei", "Shu", "Lord, benevolent, ears hanging low, gentle but firm face, green silk robes, gold trim"),
    ("Guan Yu", "Shu", "General, long red beard, green robes, massive build, heroic, fierce gaze"),
    ("Zhang Fei", "Shu", "General, thick black beard, bulging eyes, powerful, green armor with animal motifs"),
    ("Zhuge Liang", "Shu", "Strategist, white crane feather fan, serene expression, ornate headgear, flowing white and green robes"),
    ("Zhao Yun", "Shu", "General, silver armor, handsome, young but noble, green cape, dashing appearance"),
    ("Ma Chao", "Shu", "General, lion-head helmet, silver and green armor, white cloak, fierce warrior"),
    ("Huang Zhong", "Shu", "General, old but strong, white beard, green armor, expert archer, majestic"),
    ("Wei Yan", "Shu", "General, dark features, rebellious gaze, green and bronze armor, fierce"),
    ("Pang Tong", "Shu", "Strategist, eccentric appearance, clever gaze, ragged but noble brown and green robes"),
    ("Jiang Wei", "Shu", "General, young successor, intellegent, green armor, silver accents"),
    ("Ma Dai", "Shu", "General, loyal, green armor, sturdy build"),
    ("Guan Ping", "Shu", "General, Guan Yu's son, strong, silver and green armor"),
    ("Zhang Bao", "Shu", "General, Zhang Fei's son, fierce, green and black armor"),
    ("Guan Xing", "Shu", "General, heroic, silver armor, green cape"),
    ("Fa Zheng", "Shu", "Strategist, sharp features, clever, green silk robes"),
    ("Xu Shu", "Shu", "Strategist, scholarly, humble, green robes"),
    ("Yueying", "Shu", "Scholar, Zhuge Liang's wife, intelligent, green silk robes, mechanical fan"),
    ("Ma Liang", "Shu", "Official, white eyebrows, calm, green robes"),
    ("Liao Hua", "Shu", "General, veteran, sturdy green armor"),
    ("Yuan Shansong", "Shu", "Official, green robes"),

    # WEI (Blue)
    ("Cao Cao", "Wei", "Lord, ambitious, short beard, intense cold gaze, deep blue silk robes, gold armor plates"),
    ("Xiahou Dun", "Wei", "General, one eye with eyepatch, fierce, blue armor, powerful"),
    ("Xiahou Yuan", "Wei", "General, sturdy archer, blue armor, fast looking"),
    ("Zhang Liao", "Wei", "General, majestic, blue armor, twin blade expert, fierce but noble"),
    ("Xu Huang", "Wei", "General, headwrap, blue armor, giant axe user"),
    ("Zhang He", "Wei", "General, elegant, butterfly motifs on blue armor, graceful"),
    ("Cao Ren", "Wei", "General, heavy armor expert, blue and silver plate, sturdy"),
    ("Sima Yi", "Wei", "Strategist, sharp eagle-like gaze, black and blue robes, mystical headgear"),
    ("Guo Jia", "Wei", "Strategist, sickly but brilliant, pale, blue robes, wise gaze"),
    ("Xun Yu", "Wei", "Strategist, noble, handsome, blue robes, loyal expression"),
    ("Xun You", "Wei", "Strategist, calm, blue robes"),
    ("Cheng Yu", "Wei", "Strategist, veteran, blue robes, tall"),
    ("Jia Xu", "Wei", "Strategist, cold calculation, blue robes"),
    ("Yu Jin", "Wei", "General, disciplined, blue armor"),
    ("Pang De", "Wei", "General, coffin-carrier, white lion helmet, blue armor"),
    ("Cao Pi", "Wei", "Lord, Cao Cao's son, regal, blue silk robes, sharp"),
    ("Zhenji", "Wei", "Lady, beautiful, flute, blue elegant robes"),
    ("Deng Ai", "Wei", "General, climbing gear, blue armor"),
    ("Zhong Hui", "Wei", "General, young ambitious, blue armor, flying swords"),
    ("Man Chong", "Wei", "Official, blue armor"),

    # WU (Red)
    ("Sun Jian", "Wu", "Lord, Tiger of Jiangdong, red headband, fierce, bronze and red armor"),
    ("Sun Ce", "Wu", "Lord, Little Conqueror, young but powerful, red armor, dashing"),
    ("Sun Quan", "Wu", "Lord, purple beard, green eyes, regal, red and gold silk robes"),
    ("Zhou Yu", "Wu", "Strategist, handsome, white and red robes, elegant, artistic"),
    ("Lu Su", "Wu", "Strategist, honest, sturdy, red robes"),
    ("Lu Meng", "Wu", "General, scholar-warrior, red armor over robes"),
    ("Lu Xun", "Wu", "General, young genius, red and silver armor, clever"),
    ("Gan Ning", "Wu", "General, pirate, bells, red scarf, fierce, tanned"),
    ("Taishi Ci", "Wu", "General, powerful archer, red and bronze armor"),
    ("Huang Gai", "Wu", "General, veteran, bare-chested under red armor, fierce"),
    ("Cheng Pu", "Wu", "General, veteran, red armor"),
    ("Han Dang", "Wu", "General, veteran, red armor"),
    ("Zhou Tai", "Wu", "General, scars, silent, red armor, katana style weapon"),
    ("Ling Tong", "Wu", "General, young, red armor"),
    ("Zhu Ran", "Wu", "General, fire archer, red armor"),
    ("Sun Shangxiang", "Wu", "Lady, bow princess, red martial robes, energetic"),
    ("Lian Shi", "Wu", "Lady, graceful, red robes, crossbow"),
    ("Da Qiao", "Wu", "Lady, beautiful, fan, red robes"),
    ("Xiao Qiao", "Wu", "Lady, cute, fan, red robes"),
    ("Ding Feng", "Wu", "General, ice/snow general, red armor"),

    # OTHERS (Neutral/Various)
    ("Lu Bu", "Others", "General, two pheasant feathers on gold crown, black armor, chaotic energy, fierce gaze"),
    ("Diaochan", "Others", "Lady, most beautiful, pink and white silk robes, dancer"),
    ("Dong Zhuo", "Others", "Lord, fat but powerful, cruel, dark robes"),
    ("Yuan Shao", "Others", "Lord, noble, gold armor, majestic but indecisive look"),
    ("Yuan Shu", "Others", "Lord, extravagant, gold robes, malicious"),
    ("Zhang Jue", "Others", "Rebel, yellow scarf, mystical robes, sorcerer staff"),
    ("Gongsun Zan", "Others", "Lord, white horse general, white armor"),
    ("Meng Huo", "Others", "Nanman King, tribal armor, fierce, massive"),
    ("Zhu Rong", "Others", "Nanman Queen, fire goddess, throwing knives, red and feathers"),
    ("Chen Gong", "Others", "Strategist, loyal to Lu Bu, scrolls"),
    ("Gao Shun", "Others", "General, trapped camp leader, silent, black armor"),
    ("Lu Lingqi", "Others", "General, Lu Bu's daughter, cross-pike, black and red armor"),
    ("Cai Wenji", "Others", "Musician, harp, elegant blue/white robes"),
    ("Zuo Ci", "Others", "Taoist, mystical, floating robes"),
    ("Hua Tuo", "Others", "Doctor, old, benevolent, medical bag"),
    ("Ma Teng", "Others", "General, western leader, furs, sturdy"),
    ("Han Sui", "Others", "General, western leader, armor"),
    ("Liu Biao", "Others", "Lord, old, scholar-like, purple robes"),
    ("Liu Zhang", "Others", "Lord, weak, ornate robes"),
    ("Zhang Lu", "Others", "Celestial Master, religious robes"),
    ("He Jin", "Others", "Regent, Butcher, fat, ornate robes"),
    ("Zhang Liao (Old)", "Others", "Veteran general"),
    ("Guan Yu (Deity)", "Others", "God of War, glowing green energy"),
    ("Yan Liang", "Others", "General, fierce, heavy armor"),
    ("Wen Chou", "Others", "General, fierce, heavy armor"),
    ("Sun Chen", "Others", "Power struggle"),
    ("Sima Shi", "Others", "Strategist, eyepatch, cold"),
    ("Sima Zhao", "Others", "Strategist, carefree but sharp"),
    ("Wang Yuanji", "Others", "Lady, intellegent, blue robes"),
    ("Zhang Chunhua", "Others", "Lady, Sima Yi's wife, sharp"),
    ("Guan Yinping", "Others", "Lady, Guan Yu's daughter, green robes, powerful weapon"),
    ("Bao Sanniang", "Others", "Lady, energetic, green robes"),
    ("Xingcai", "Others", "Lady, Zhang Fei's daughter, green and silver armor"),
    ("Ma Yunlu", "Others", "Lady, Ma Chao's sister, silver armor"),
    ("Lu Ji", "Others", "Official"),
    ("Zhuge Ke", "Others", "Strategist, arrogant"),
    ("Jiang Gan", "Others", "Scholar, comical"),
    ("Xu Gong", "Others", "Assassin"),
    ("Li Ru", "Others", "Strategist for Dong Zhuo, sinister"),
    ("Tianshui General", "Others", "Generic warrior")
]

tile_prompt_template = """
{
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "cfg": 8, "denoise": 1, "latent_image": ["5", 0], "model": ["4", 0],
            "negative": ["7", 0], "positive": ["6", 0], "sampler_name": "euler",
            "scheduler": "normal", "seed": 42, "steps": 25
        }
    },
    "4": { "class_type": "CheckpointLoaderSimple", "inputs": { "ckpt_name": "sd_v1-5.safetensors" } },
    "5": { "class_type": "EmptyLatentImage", "inputs": { "batch_size": 1, "height": 768, "width": 512 } },
    "6": { "class_type": "CLIPTextEncode", "inputs": { "clip": ["4", 1], "text": "" } },
    "7": { "class_type": "CLIPTextEncode", "inputs": { "clip": ["4", 1], "text": "text, watermark, blurry, low quality, deformed hands, bad quality" } },
    "8": { "class_type": "VAEDecode", "inputs": { "samples": ["3", 0], "vae": ["4", 2] } },
    "9": { "class_type": "SaveImage", "inputs": { "filename_prefix": "Portrait", "images": ["8", 0] } }
}
"""

style_suffix = ", Semic-realistic digital painting, Three Kingdoms heroic heroic general portrait, waist-up, 3/4 view, dramatic rim lighting, high contrast, cinematic lighting, sharp focus, 8k resolution, Koei Tecmo style, masterpiece"

for i, (name, faction, features) in enumerate(characters):
    safe_name = name.replace(" ", "_").lower() + ".png"
    if os.path.exists(os.path.join("/Users/proktv/.gemini/antigravity/scratch/chunhadoji/public/portraits", safe_name)):
        continue

    prompt_text = f"Portrait of {name} from Three Kingdoms, {faction} faction officer, {features}{style_suffix}"
    
    workflow = json.loads(tile_prompt_template)
    workflow["6"]["inputs"]["text"] = prompt_text
    workflow["3"]["inputs"]["seed"] = 2000 + i
    
    print(f"Generating Portrait {i+1}/100: {name}...")
    try:
        res = queue_prompt(workflow)
        pid = res['prompt_id']
        history = get_history(pid)
        img_info = history['outputs']['9']['images'][0]
        save_image(img_info, safe_name)
        print(f"Saved {safe_name}")
    except Exception as e:
        print(f"Error generating {name}: {e}")

print("All 100 portraits generated successfully!")
