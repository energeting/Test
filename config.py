
BMC_CONFIG = {
    'base_url': 'http://localhost:8000',  
    'username': 'root',
    'password': '0penBmc',
    'verify_ssl': False
}

TEST_CONFIG = {
    'power_operation_delay': 2,  
    'request_timeout': 10,
    'max_retries': 3
}

TEMPERATURE_LIMITS = {
    'cpu_min': 10,
    'cpu_max': 90,
    'system_min': 15,
    'system_max': 85
}
