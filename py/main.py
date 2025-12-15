import os
import time
import base64
import requests
import json
import re

# ================= 配置区域 =================

API_KEY = "sk-VGlEY77068BjCKj7izJjzQPOGzU2yEPIyeYPR1tKdYT3ARwd"
BASE_URL = "https://api.aabao.top"

# 模型配置
IMAGE_MODEL = "gemini-3-pro-image-preview"
VIDEO_MODEL = "sora-2-landscape-15s"

# 文件路径
INPUT_ORIGINAL = "buddha_original.jpg"
OUTPUT_RESTORED = "buddha_restored.jpg"
OUTPUT_VIDEO = "buddha_showcase.mp4"

import resume_task

# ================= 工具函数 =================

def encode_image_to_base64(image_path):
    """将本地图片转换为 Base64 字符串 (不带前缀)"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def download_video(video_url, output_path):
    """下载视频文件"""
    print(f"⬇️ 正在下载视频: {video_url[:50]}...")
    try:
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ 视频已保存至: {output_path}")
            return True
        else:
            print(f"❌ 下载失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 下载出错: {e}")
        return False

# ================= 步骤 1: 图片修复 (Gemini) =================

def restore_image(input_path, output_path):
    print(f"\n--- 步骤 1: 正在修复图片 (Model: {IMAGE_MODEL}) ---")
    
    if not os.path.exists(input_path):
        print(f"❌ 错误: 找不到原图 {input_path}")
        return False

    base64_img = encode_image_to_base64(input_path)
    
    # 提示词 (用户指定)
    prompt = (
        "i will give you a photo, and you should Restore the weathered stone statue of a Buddha in a robe. "
        "Its body is covered in brilliant, gleaming gold leaf, Radiant, polished gold, brilliant and gleaming. "
        "The robe is adorned with intricate, hand-painted patterns in vibrant colors of red, blue, green, orange. "
        "Also, please gently restore the faded murals and colorful paintings on the surrounding stone walls behind the statue, bringing back their original vibrant colors and details while keeping the rock texture. "
        "There may more than one statue in the photo. "
        "Do not change the background structure. "
        "Please generate/output the restored image."
    )

    url = f"{BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": IMAGE_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
                    }
                ]
            }
        ],
        "stream": False
    }

    try:
        print(f"🚀 发送修复请求...")
        print("⏳ 总请求可能需要较长时间 (3-10分钟)，请耐心等待...")
        # Pro 模型可能较慢，设置 600s 超时
        response = requests.post(url, headers=headers, json=payload, timeout=600)
        
        if response.status_code != 200:
            print(f"❌ 修复请求失败: {response.status_code} - {response.text}")
            return False

        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            print("✅ 模型已响应")
            
            # 提取图片
            # 1. Base64
            base64_match = re.search(r'data:image\/(\w+);base64,([a-zA-Z0-9+/=]+)', content)
            # 2. Markdown Link
            img_match = re.search(r'!\[.*?\]\((.*?)\)', content)
            # 3. Plain URL
            url_match = re.search(r'https?://[^\s<>"]+?(?:\.jpg|\.png|\.webp)', content)
            
            if base64_match:
                print("🎉 检测到 Base64 图片数据")
                img_data = base64.b64decode(base64_match.group(2))
                with open(output_path, "wb") as f:
                    f.write(img_data)
                print(f"✅ 修复图片已保存: {output_path}")
                return True
            elif img_match or url_match:
                image_url = img_match.group(1) if img_match else url_match.group(0)
                print(f"🎉 检测到图片 URL: {image_url}")
                img_res = requests.get(image_url)
                if img_res.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(img_res.content)
                    print(f"✅ 修复图片已保存: {output_path}")
                    return True
            else:
                print("⚠️ 未检测到图片输出")
                if len(content) > 200:
                    print(content[:200] + "...")
                else:
                    print(content)
                return False
        else:
            print("❌ 响应格式异常")
            return False

    except Exception as e:
        print(f"❌ 修复过程出错: {e}")
        return False

# ================= 步骤 2: 视频生成 (Sora) =================

def generate_video(image_path):
    print(f"\n--- 步骤 2: 正在生成视频 (Model: {VIDEO_MODEL}) ---")

    # Sora API 需要带前缀的 Base64
    base64_str = encode_image_to_base64(image_path)
    base64_with_prefix = f"data:image/jpeg;base64,{base64_str}"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 视频 Prompt (包含声音描述)
    prompt = (
        "Camera Movement: A montage of three distinct, separate shots with hard cuts. "
        "Shot 1: Low angle tilt-up from the base to the head, emphasizing the statue's towering height and grandeur. "
        "Shot 2: Extreme close-up of the face with a slow, smooth orbit. "
        "Shot 3: Extreme close-up of the robe patterns with a slow horizontal pan. "
        "Strictly adhering to the provided image details. "
        "Subject Stability: The Golden Buddha statue is massive, heavy, and completely motionless. "
        "Quality: 8k, IMAX quality, National Geographic style, razor-sharp focus, high fidelity. "
        "Soundscape: must be mute."
    )

    payload = {
        "model": VIDEO_MODEL,
        "prompt": prompt,
        "image": base64_with_prefix,
    }
    
    submit_url = f"{BASE_URL}/v1/videos"
    
    task_id = None
    try:
        print(f"🚀 提交视频任务...")
        response = requests.post(submit_url, headers=headers, json=payload, timeout=900)
        
        if response.status_code != 200:
            print(f"❌ 视频提交失败: {response.status_code} - {response.text}")
            return None, None
            
        task_id = response.json().get('id')
        print(f"✅ 任务提交成功! Task ID: {task_id}")
        
        # 轮询
        start_time = time.time()
        error_count = 0 # 错误计数器

        while True:
            if time.time() - start_time > 600: 
                print("❌ 等待视频生成超时")
                break
                
            check_url = f"{BASE_URL}/v1/videos/{task_id}"
            try:
                check_res = requests.get(check_url, headers=headers, timeout=30)
                
                if check_res.status_code == 200:
                    error_count = 0 # 成功连接，重置计数
                    data = check_res.json()
                    status = data.get('status')
                    progress = data.get('progress', 0)
                    print(f"⏳ 进度: {progress}% ({status})")
                    
                    if status == 'completed':
                        return data.get('video_url'), task_id
                    elif status == 'failed':
                        print("❌ 视频生成失败")
                        return None, task_id
                else:
                    print(f"⚠️ 状态码异常: {check_res.status_code}，稍后重试...")
                    
            except Exception as e:
                error_count += 1
                # 智能退避策略：错误越多，等待越久 (5s, 10s, 15s... max 30s)
                wait_time = min(5 * error_count, 30)
                print(f"⚠️ 网络波动 ({error_count}次): {str(e)[:50]}... 正在重试 (等待 {wait_time}s)")
                time.sleep(wait_time)
                continue
                
            time.sleep(5)
            
    except Exception as e:
        print(f"❌ 视频生成过程出错: {e}")
        return None, task_id
    
    return None, task_id

# ================= 主程序 =================

if __name__ == "__main__":
    print("=== 佛像修复与视频生成全流程 ===")
    
    # 1. 检查原图
    if not os.path.exists(INPUT_ORIGINAL):
        print(f"❌ 请准备原图: {INPUT_ORIGINAL}")
        print("请将原始风化佛像图片重命名为 'buddha_original.jpg' 并放在此目录下。")
        exit()
        
    # 2. 智能修复流程
    ready_for_video = False
    
    if os.path.exists(OUTPUT_RESTORED):
        print(f"\n⚠️ 发现已存在的修复图片: {OUTPUT_RESTORED}")
        choice = input("👉 是否直接使用这张图片生成视频？(y/n) [默认y]: ").strip().lower()
        if choice == '' or choice == 'y':
            ready_for_video = True
        else:
            print("🔄 正在重新修复图片...")
            if restore_image(INPUT_ORIGINAL, OUTPUT_RESTORED):
                ready_for_video = True
    else:
        if restore_image(INPUT_ORIGINAL, OUTPUT_RESTORED):
            ready_for_video = True

    # 3. 视频生成流程
    if ready_for_video:
        print(f"\n👀 建议现在打开 {OUTPUT_RESTORED} 检查修复效果。")
        try:
            input("👉 确认效果满意后，按 Enter 键开始生成视频 (或按 Ctrl+C 终止)...")
        except KeyboardInterrupt:
            print("\n🚫 用户取消操作。")
            exit()

        video_url, task_id = generate_video(OUTPUT_RESTORED)
        
        success = False
        if video_url:
            if download_video(video_url, OUTPUT_VIDEO):
                success = True
        
        if success:
            print("\n🎉🎉 全流程完成！视频已生成。")
        else:
            print("\n⚠️ 视频生成或下载失败。")
            if task_id:
                print(f"🔄 尝试使用 resume_task 恢复任务 (Task ID: {task_id})...")
                resume_task.check_and_download(task_id)
            else:
                print("❌ 无法恢复任务 (未获取到 Task ID)。")
    else:
        print("\n❌ 图片修复失败，终止流程。")
