import os
import base64
import requests
import time

# ================= 配置 =================
API_KEY = "sk-6DVZcEhWXSkyUTbjj5hvrh3MHaa8ekk2dBNCI5GzmWg5LnUs"
BASE_URL = "https://api.aabao.top"
MODEL = "gemini-3-pro-image-preview"  # 用户指定的模型

def encode_image_to_base64(image_path):
    """将图片转为 Base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def restore_buddha_image(input_path, output_path):
    print(f"正在处理图片: {input_path} ...")
    
    if not os.path.exists(input_path):
        print(f"❌ 错误: 找不到文件 {input_path}")
        return

    base64_image = encode_image_to_base64(input_path)
    
    url = f"{BASE_URL}/v1beta/models/gemini-3-pro-image-preview:generateContent"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 提示词：用户指定
    prompt = (
        "i will give you a photo, and you should Restore the weathered stone statue of a Buddha in a robe. "
        "Its body is covered in brilliant, gleaming gold leaf, Radiant, polished gold, brilliant and gleaming. "
        "The robe is adorned with intricate, hand-painted patterns in vibrant colors of red, blue, green, orange. "
        "There may more than one statue in the photo. "
        "Do not change the background. "
        "Please generate/output the restored image."
    )

    # 使用 OpenAI 兼容接口
    url = f"{BASE_URL}/v1/chat/completions"

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "stream": False
    }

    try:
        print(f"🚀 正在发送请求到 {url} (Model: {MODEL})...")
        # Pro 模型可能需要更长时间，设置 600秒超时
        response = requests.post(url, headers=headers, json=payload, timeout=600)
        
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            print(response.text)
            return

        result = response.json()
        # print("API 响应:", json.dumps(result, indent=2, ensure_ascii=False))
        
        # 解析响应内容
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            
            # 防止打印过长的 Base64
            if len(content) > 1000:
                print("\n💬 模型回复内容 (前200字符):")
                print(content[:200] + "... [内容过长，疑似包含 Base64 图片数据]")
            else:
                print("\n💬 模型回复内容:")
                print(content)
            
            # 尝试提取图片
            import re
            
            # 1. 尝试匹配 Base64 图片 (data:image/jpeg;base64,...)
            base64_match = re.search(r'data:image\/(\w+);base64,([a-zA-Z0-9+/=]+)', content)
            
            # 2. 匹配 Markdown 图片链接
            img_match = re.search(r'!\[.*?\]\((.*?)\)', content)
            # 3. 匹配纯 URL (以 http 开头，图片格式结尾)
            url_match = re.search(r'https?://[^\s<>"]+?(?:\.jpg|\.png|\.webp)', content)
            
            if base64_match:
                print("\n🎉 发现 Base64 图片数据")
                # img_format = base64_match.group(1) # e.g., jpeg
                img_data_str = base64_match.group(2)
                try:
                    img_bytes = base64.b64decode(img_data_str)
                    with open(output_path, "wb") as f:
                        f.write(img_bytes)
                    print(f"✅ 图片已解码并保存至: {output_path}")
                except Exception as e:
                    print(f"❌ Base64 解码失败: {e}")
            
            elif img_match or url_match:
                image_url = img_match.group(1) if img_match else url_match.group(0)
                print(f"\n🎉 发现图片 URL: {image_url}")
                print("⬇️ 正在下载修复后的图片...")
                
                try:
                    img_res = requests.get(image_url)
                    if img_res.status_code == 200:
                        with open(output_path, "wb") as f:
                            f.write(img_res.content)
                        print(f"✅ 图片已保存至: {output_path}")
                    else:
                        print("❌ 图片下载失败")
                except Exception as e:
                    print(f"❌ 下载异常: {e}")
            else:
                print("\n⚠️ 未在回复中检测到图片链接或 Base64 数据。")
                print("可能原因：该模型仅返回了文本描述，或者图片链接格式不标准。")
        else:
            print("❌ 响应格式异常")

    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    input_file = "buddha_original.jpg"
    output_file = "buddha_restored.jpg"
    
    restore_buddha_image(input_file, output_file)
