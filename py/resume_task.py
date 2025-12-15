import requests
import time

# 配置
NEWAPI_KEY = "sk-6DVZcEhWXSkyUTbjj5hvrh3MHaa8ekk2dBNCI5GzmWg5LnUs"
NEWAPI_BASE_URL = "https://api.aabao.top"
TASK_ID = "video_003930f9e64743e885b4bcc0058d768a"  # 您刚才失败的任务 ID

def check_and_download(task_id=None):
    target_task_id = task_id if task_id else TASK_ID
    headers = {
        "Authorization": f"Bearer {NEWAPI_KEY}",
        "Content-Type": "application/json"
    }
    
    url = f"{NEWAPI_BASE_URL}/v1/videos/{target_task_id}"
    print(f"正在查询任务: {target_task_id}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            progress = data.get('progress', 0)
            print(f"当前状态: {status} (进度: {progress}%)")
            
            if status == 'completed':
                video_url = data.get('video_url')
                print(f"🎉 视频已生成! 下载链接: {video_url}")
                
                # 下载
                print("正在下载...")
                v_res = requests.get(video_url, stream=True)
                with open("buddha_showcase.mp4", "wb") as f:
                    for chunk in v_res.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("✅ 下载完成: buddha_showcase.mp4")
                return True
            else:
                print("任务尚未完成，请稍后再试。")
                return False
        else:
            print(f"查询失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"发生错误: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        check_and_download(sys.argv[1])
    else:
        check_and_download()
