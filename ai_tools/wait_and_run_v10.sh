#!/bin/bash
echo "Waiting for Juggernaut XL v10 download to complete..."
while pgrep -f "Juggernaut-X-v10.safetensors" > /dev/null; do
    current_size=$(ls -lh /Users/proktv/ai-tools/ComfyUI/models/checkpoints/Juggernaut-X-v10.safetensors | awk '{print $5}')
    echo "Downloading... Current size: $current_size"
    sleep 10
done

echo "Download likely complete or failed. Checking file size..."
final_size=$(ls -l /Users/proktv/ai-tools/ComfyUI/models/checkpoints/Juggernaut-X-v10.safetensors | awk '{print $5}')
# Approx 6.6GB is 7105348672 bytes. Check if > 6000000000
if [ "$final_size" -gt 6000000000 ]; then
    echo "Download verified (>6GB). Starting V10 Generation..."
    # Refresh ComfyUI model list (it auto-refreshes usually, but just in case)
    # Start generation
    python3 -u /Users/proktv/.gemini/antigravity/scratch/chunhadoji/ai_tools/generate_juggernaut_v10.py > /Users/proktv/.gemini/antigravity/scratch/chunhadoji/ai_tools/generation_v10.log 2>&1
else
    echo "Download failed or incomplete (Size: $final_size bytes). Aborting."
fi
