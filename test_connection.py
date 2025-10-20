
import requests
from test.config import BMC_CONFIG

def test_connection():
    print("🔍 Тестирование подключения к Redfish API...")
    
    url = f"{BMC_CONFIG['base_url']}/redfish/v1/"
    
    try:
        response = requests.get(url, verify=BMC_CONFIG['verify_ssl'])
        print(f"✅ Подключение успешно! Status: {response.status_code}")
        print(f"📡 URL: {url}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Сервис: {data.get('Name', 'Unknown')}")
            print(f"🔧 Версия: {data.get('RedfishVersion', 'Unknown')}")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Не удалось подключиться к {url}")
        print("💡 Убедитесь что mock-сервер запущен: python3 redfish_mock_server.py")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    test_connection()
