import requests
import time
import json
import configparser
from datetime import datetime, timezone

# Load config
config = configparser.ConfigParser()
config.read('config/config.ini')

TIMEOUT = int(config['monitor']['timeout_seconds'])
RETRY_ATTEMPTS = int(config['monitor']['retry_attempts'])


def probe_target(target):
    name = target['name']
    url = target['url']
    method = target['method']
    expected_status = target['expected_status']
    keyword = target.get('keyword')

    result = {
        'name': name,
        'url': url,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': None,
        'status_code': None,
        'response_time_ms': None,
        'keyword_found': None,
        'error': None
    }

    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            start = time.time()
            response = requests.request(
                method,
                url,
                timeout=TIMEOUT,
                allow_redirects=True
            )
            elapsed = round((time.time() - start) * 1000, 2)

            result['status_code'] = response.status_code
            result['response_time_ms'] = elapsed

            # Keyword check
            if keyword:
                result['keyword_found'] = keyword in response.text
            else:
                result['keyword_found'] = None

            # Status validation
            if response.status_code == expected_status:
                result['status'] = 'UP'
            else:
                result['status'] = 'DOWN'

            break

        except requests.exceptions.Timeout:
            result['error'] = f'Timeout after {TIMEOUT}s'
            result['status'] = 'DOWN'
        except requests.exceptions.ConnectionError as e:
            result['error'] = f'Connection error: {str(e)}'
            result['status'] = 'DOWN'
        except Exception as e:
            result['error'] = f'Unexpected error: {str(e)}'
            result['status'] = 'DOWN'

        if attempt < RETRY_ATTEMPTS:
            time.sleep(2)

    return result


def probe_all_targets(targets):
    results = []
    for target in targets:
        if target.get('enabled', True):
            print(f"  Probing: {target['name']}...")
            result = probe_target(target)
            results.append(result)
    return results