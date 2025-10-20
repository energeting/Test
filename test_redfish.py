
import pytest
import requests
import json
import time
import logging
from typing import Dict, Any


from test.config import BMC_CONFIG, TEST_CONFIG

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedfishClient:
    """Клиент для работы с Redfish API"""
    
    def __init__(self, base_url: str = None, username: str = None, password: str = None, verify_ssl: bool = None):
        self.base_url = (base_url or BMC_CONFIG['base_url']).rstrip('/')
        self.username = username or BMC_CONFIG['username']
        self.password = password or BMC_CONFIG['password']
        self.verify_ssl = verify_ssl if verify_ssl is not None else BMC_CONFIG['verify_ssl']
        self.session = requests.Session()
        self.auth_token = None
        self.session_id = None
        
    def authenticate(self) -> Dict[str, Any]:
        """Аутентификация в Redfish API"""
        auth_url = f"{self.base_url}/redfish/v1/SessionService/Sessions"
        auth_data = {
            "UserName": self.username,
            "Password": self.password
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"Попытка аутентификации на {auth_url}")
            response = self.session.post(
                auth_url,
                json=auth_data,
                headers=headers,
                verify=self.verify_ssl,
                timeout=TEST_CONFIG['request_timeout']
            )
            
            logger.info(f"Ответ сервера: {response.status_code}")
            
            if response.status_code == 201:
                self.auth_token = response.headers.get('X-Auth-Token')
                self.session_id = response.json().get('Id')
                if self.auth_token:
                    self.session.headers.update({'X-Auth-Token': self.auth_token})
                logger.info("Аутентификация успешна")
                return response.json()
            else:
                logger.error(f"Ошибка аутентификации: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка подключения: {e}")
            return None
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        url = f"{self.base_url}/redfish/v1/Systems/system"
        
        try:
            response = self.session.get(
                url, 
                verify=self.verify_ssl,
                timeout=TEST_CONFIG['request_timeout']
            )
            logger.info(f"GET {url} - Status: {response.status_code}")
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка получения информации о системе: {e}")
            return None
    
    def power_control(self, reset_type: str) -> bool:
        """Управление питанием системы"""
        url = f"{self.base_url}/redfish/v1/Systems/system/Actions/ComputerSystem.Reset"
        
        data = {
            "ResetType": reset_type
        }
        
        try:
            logger.info(f"Power control: {reset_type}")
            response = self.session.post(
                url,
                json=data,
                verify=self.verify_ssl,
                timeout=TEST_CONFIG['request_timeout']
            )
            logger.info(f"Power control response: {response.status_code}")
            return response.status_code in [200, 202]
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка управления питанием: {e}")
            return False
    
    def get_thermal_data(self) -> Dict[str, Any]:
        """Получение данных о температуре"""
        url = f"{self.base_url}/redfish/v1/Chassis/chassis/Thermal"
        
        try:
            response = self.session.get(
                url, 
                verify=self.verify_ssl,
                timeout=TEST_CONFIG['request_timeout']
            )
            logger.info(f"GET {url} - Status: {response.status_code}")
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка получения данных о температуре: {e}")
            return None

@pytest.fixture(scope="session")
def redfish_client():
    """Фикстура для создания клиента Redfish"""
    client = RedfishClient()
    yield client

@pytest.fixture(scope="function")
def authenticated_session(redfish_client):
    """Фикстура для аутентифицированной сессии"""
    auth_result = redfish_client.authenticate()
    if not auth_result:
        pytest.skip("Не удалось выполнить аутентификацию")
    yield redfish_client

class TestRedfishAuthentication:
    """Тесты аутентификации в Redfish API"""
    
    def test_authentication_success(self, redfish_client):
        """Тест успешной аутентификации"""
        logger.info("=" * 50)
        logger.info("Запуск теста успешной аутентификации...")
        
        auth_result = redfish_client.authenticate()

        assert auth_result is not None, "Аутентификация не удалась"
        assert 'Id' in auth_result, "ID сессии не получен"
        
        logger.info("✓ Аутентификация прошла успешно")
        logger.info(f"Session ID: {auth_result.get('Id')}")
    
    def test_authentication_failure(self):
        """Тест неудачной аутентификации с неверными данными"""
        logger.info("=" * 50)
        logger.info("Запуск теста неудачной аутентификации...")
        
        client = RedfishClient(username="wrong_user", password="wrong_password")
        auth_result = client.authenticate()

        assert auth_result is None, "Аутентификация с неверными данными не должна проходить"
        
        logger.info("✓ Тест неудачной аутентификации пройден")

class TestSystemInfo:
    """Тесты получения информации о системе"""
    
    def test_get_system_info(self, authenticated_session):
        """Тест получения информации о системе"""
        logger.info("=" * 50)
        logger.info("Запуск теста получения информации о системе...")
        
        system_info = authenticated_session.get_system_info()

        assert system_info is not None, "Не удалось получить информацию о системе"
        assert 'Status' in system_info, "Отсутствует поле Status в ответе"
        assert 'PowerState' in system_info, "Отсутствует поле PowerState в ответе"
        
        logger.info(f"✓ Информация о системе получена: PowerState={system_info.get('PowerState')}")
        logger.info(f"✓ Статус системы: {system_info.get('Status')}")
    
    def test_system_info_structure(self, authenticated_session):
        """Тест структуры информации о системе"""
        logger.info("=" * 50)
        logger.info("Запуск теста структуры информации о системе...")
        
        system_info = authenticated_session.get_system_info()
        
        if system_info:
            required_fields = ['Id', 'Name', 'PowerState', 'Status']
            for field in required_fields:
                assert field in system_info, f"Отсутствует обязательное поле: {field}"
            
            logger.info("✓ Структура информации о системе корректна")

class TestPowerManagement:
    """Тесты управления питанием"""
    
    def test_power_on(self, authenticated_session):
        """Тест включения сервера"""
        logger.info("=" * 50)
        logger.info("Запуск теста включения сервера...")
        
        result = authenticated_session.power_control("On")

        assert result is True, "Не удалось выполнить операцию включения"

        time.sleep(TEST_CONFIG['power_operation_delay'])
        system_info = authenticated_session.get_system_info()
        
        if system_info:
            logger.info(f"✓ Операция включения выполнена. Текущий PowerState: {system_info.get('PowerState')}")
        else:
            logger.warning("⚠ Не удалось проверить состояние после включения")
    
    def test_power_off(self, authenticated_session):
        """Тест выключения сервера"""
        logger.info("=" * 50)
        logger.info("Запуск теста выключения сервера...")

        result = authenticated_session.power_control("ForceOff")

        assert result is True, "Не удалось выполнить операцию выключения"

        time.sleep(TEST_CONFIG['power_operation_delay'])
        system_info = authenticated_session.get_system_info()
        
        if system_info:
            logger.info(f"✓ Операция выключения выполнена. Текущий PowerState: {system_info.get('PowerState')}")
        else:
            logger.warning("⚠ Не удалось проверить состояние после выключения")

class TestTemperatureMonitoring:
    """Тесты мониторинга температуры"""
    
    def test_temperature_sensors_exist(self, authenticated_session):
        """Тест наличия датчиков температуры"""
        logger.info("=" * 50)
        logger.info("Запуск теста датчиков температуры...")
        
        thermal_data = authenticated_session.get_thermal_data()
        
        if thermal_data:
            assert 'Temperatures' in thermal_data, "Отсутствуют данные о температуре"
            assert len(thermal_data['Temperatures']) > 0, "Нет доступных датчиков температуры"
            
            logger.info(f"✓ Найдено датчиков температуры: {len(thermal_data['Temperatures'])}")
        
            for sensor in thermal_data['Temperatures']:
                name = sensor.get('Name', 'Unknown')
                reading = sensor.get('ReadingCelsius', 'N/A')
                logger.info(f"  Датчик: {name}, Температура: {reading}°C")
        else:
            pytest.skip("Данные о температуре недоступны")
    
    def test_cpu_temperature_normal_range(self, authenticated_session):
        """Тест температуры CPU в нормальном диапазоне"""
        logger.info("=" * 50)
        logger.info("Запуск теста температуры CPU...")
        
        thermal_data = authenticated_session.get_thermal_data()
        
        if thermal_data and 'Temperatures' in thermal_data:
            cpu_sensors = [s for s in thermal_data['Temperatures'] 
                          if 'CPU' in s.get('Name', '') or 'Processor' in s.get('Name', '')]
            
            if cpu_sensors:
                for sensor in cpu_sensors:
                    temp = sensor.get('ReadingCelsius')
                    if temp is not None:
                        assert 10 <= temp <= 90, f"Температура CPU {temp}°C вне допустимого диапазона"
                        logger.info(f"✓ Температура CPU в норме: {temp}°C")
            else:
                logger.warning("⚠ Датчики CPU не найдены, проверяем все датчики")
                for sensor in thermal_data['Temperatures']:
                    temp = sensor.get('ReadingCelsius')
                    if temp is not None:
                        assert 10 <= temp <= 90, f"Температура {sensor.get('Name')} {temp}°C вне диапазона"
                        logger.info(f"✓ Температура {sensor.get('Name')} в норме: {temp}°C")
        else:
            pytest.skip("Данные о температуре недоступны")

class TestSensorConsistency:
    """Тесты согласованности данных датчиков"""
    
    def test_sensor_data_consistency(self, authenticated_session):
        """Тест согласованности данных датчиков"""
        logger.info("=" * 50)
        logger.info("Запуск теста согласованности данных датчиков...")
        
        thermal_data = authenticated_session.get_thermal_data()
        
        if thermal_data and 'Temperatures' in thermal_data:
            for sensor in thermal_data['Temperatures']:
                assert 'Name' in sensor, "Датчик без имени"
                assert 'ReadingCelsius' in sensor, f"Датчик {sensor.get('Name')} без показаний температуры"

                reading = sensor.get('ReadingCelsius')
                if reading is not None:
                    assert isinstance(reading, (int, float)), f"Некорректный тип данных температуры: {type(reading)}"
            
            logger.info("✓ Данные датчиков согласованы")
        else:
            pytest.skip("Данные датчиков недоступны")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
