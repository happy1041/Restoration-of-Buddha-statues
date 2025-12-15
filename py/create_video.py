import os
import time
import base64
import requests
import json

# ================= 配置区域 =================

# 视频生成 API (Sora2 API)
NEWAPI_KEY = "sk-6DVZcEhWXSkyUTbjj5hvrh3MHaa8ekk2dBNCI5GzmWg5LnUs"           # <--- 【必填】请在这里填入你的 API Key
NEWAPI_BASE_URL = "https://api.aabao.top" # <--- 已修改为您提供的地址

# 模型名称
# 根据文档选择横屏 15秒模型
VIDEO_MODEL = "sora-2-landscape" 

# ================= 工具函数 =================

def encode_image_to_base64(image_path):
    """将本地图片转换为带前缀的 Base64 字符串"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        # Sora2 API 文档推荐格式: data:image/jpeg;base64,...
        return f"data:image/jpeg;base64,{encoded_string}"

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
        else:
            print(f"❌ 下载失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 下载出错: {e}")

# ================= 核心逻辑 =================

def generate_restored_video(image_path):
    print(f"\n--- 正在提交视频生成任务 (Model: {VIDEO_MODEL}) ---")

    # 检查文件大小
    file_size = os.path.getsize(image_path)
    print(f"📄 图片大小: {file_size / 1024 / 1024:.2f} MB")
    if file_size > 2 * 1024 * 1024:
        print("⚠️ 图片较大 (>2MB)，上传可能需要较长时间，请耐心等待...")
    
    base64_image = encode_image_to_base64(image_path)
    
    headers = {
        "Authorization": f"Bearer {NEWAPI_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prompt 策略：
    # 1. 描述目标状态：展示已修复的完美状态
    # 2. 描述运镜：简单的平移/推拉，强调细节展示
    # 3. 描述声音：自然环境音，营造清幽景区的氛围
    prompt = (
        "High-quality documentary footage with ambient sound. "
        "A slow, smooth, and steady camera pan showcasing a magnificent, fully restored Golden Buddha statue. "
        "The statue is static and majestic, covered in brilliant gold leaf with intricate colorful patterns on the robe. "
        "Soft sunlight illuminates the details. "
        "No visual effects, no morphing, no transformation. "
        "Just a pure, high-resolution showcase of the artwork. 8k resolution, photorealistic, cinematic lighting. "
        "Soundscape: No sounds but very very gentle birds chirping"
    )

    # 构造请求 Payload
    # 根据 Sora2 API 文档调整
    payload = {
        "model": VIDEO_MODEL,
        "prompt": prompt,
        "image": base64_image,  # 文档指定参数名为 image
        # "style_id": "retro",  # 可选: 如果想要老纪录片感觉可以加上这个
    }
    
    # 1. 提交任务
    # 文档 Endpoint: POST /v1/videos
    submit_url = f"{NEWAPI_BASE_URL}/v1/videos"
    
    try:
        print(f"🚀 正在发送请求到 {submit_url} ...")
        # 设置 300秒 超时，防止网络卡死；上传 Base64 图片可能较慢
        response = requests.post(submit_url, headers=headers, json=payload, timeout=300)
        
        if response.status_code != 200:
            print(f"❌ 提交失败: {response.status_code}")
            print(response.text)
            return None
            
        task_data = response.json()
        task_id = task_data.get('id')
        print(f"✅ 任务提交成功! Task ID: {task_id}")
        
        # 2. 轮询状态
        start_time = time.time()
        while True:
            if time.time() - start_time > 600: # 10分钟超时
                print("❌ 等待超时")
                break
                
            # 文档 Endpoint: GET /v1/videos/{video_id}
            check_url = f"{NEWAPI_BASE_URL}/v1/videos/{task_id}"
            
            try:
                check_response = requests.get(check_url, headers=headers, timeout=30)
            except Exception as e:
                print(f"⚠️ 网络波动，正在重试... ({str(e)[:50]}...)")
                time.sleep(5)
                continue
            
            if check_response.status_code == 200:
                check_data = check_response.json()
                status = check_data.get('status')
                progress = check_data.get('progress', 0)
                
                print(f"⏳ 任务状态: {status} (进度: {progress}%)")
                
                if status == 'completed':
                    video_url = check_data.get('video_url')
                    print(f"🎉 视频生成完成! URL: {video_url}")
                    return video_url
                elif status == 'failed':
                    print("❌ 视频生成失败")
                    return None
            else:
                print(f"⚠️ 查询状态失败: {check_response.status_code}")
                
            time.sleep(5) # 每5秒检查一次
            
    except Exception as e:
        print(f"❌ 发生异常: {e}")
        return None

# ================= 主程序 =================

if __name__ == "__main__":
    # 请确保这里的文件名是您刚刚用 Image API 生成的那张“修复好的照片”
    input_img = "buddha_restored.jpg" 
    output_video = "buddha_showcase.mp4"
    
    if not os.path.exists(input_img):
        print(f"❌ 找不到输入图片: {input_img}")
        print(f"请将您在官网上生成的修复后图片重命名为 '{input_img}' 并放在此脚本同一目录下。")
    else:
        if "sk-..." in NEWAPI_KEY:
             print("⚠️ 请先在代码中填入你的 NEWAPI_KEY")
        else:
            video_url = generate_restored_video(input_img)
            
            if video_url:
                download_video(video_url, output_video)
                print("\n🎉 视频生成完成！")
