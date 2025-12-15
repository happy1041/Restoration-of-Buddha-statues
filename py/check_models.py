import requests

API_KEY = "sk-6DVZcEhWXSkyUTbjj5hvrh3MHaa8ekk2dBNCI5GzmWg5LnUs"
BASE_URL = "https://api.aabao.top"

def list_models():
    url = f"{BASE_URL}/v1/models"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("可用模型列表:")
            for model in data.get('data', []):
                mid = model.get('id')
                if 'sora' in mid.lower():
                    print(f" - {mid}")
        else:
            print(f"获取模型列表失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    list_models()
