"""
Конфигурация для тестов Redfish API
"""

# Настройки подключения к mock серверу
BMC_CONFIG = {
    'base_url': 'http://localhost:8000',  # Mock сервер
    'username': 'root',
    'password': '0penBmc',
    'verify_ssl': False
}

# Настройки тестирования
TEST_CONFIG = {
    'power_operation_delay': 2,  # Уменьшаем задержку для mock
    'request_timeout': 10,
    'max_retries': 3
}

# Допустимые диапазоны температур
TEMPERATURE_LIMITS = {
    'cpu_min': 10,
    'cpu_max': 90,
    'system_min': 15,
    'system_max': 85
}
