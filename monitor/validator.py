import configparser

# Load config
config = configparser.ConfigParser()
config.read('config/config.ini')

RESPONSE_TIME_THRESHOLD = int(config['thresholds']['response_time_ms'])


def validate_results(probe_results):
    validated = []

    for result in probe_results:
        issues = []

        # Check if target is down
        if result['status'] == 'DOWN':
            issues.append(f"Target is DOWN — status code: {result['status_code']}")

        # Check response time
        if result['response_time_ms'] and result['response_time_ms'] >= RESPONSE_TIME_THRESHOLD:
            issues.append(
                f"Slow response — {result['response_time_ms']}ms "
                f"exceeds threshold of {RESPONSE_TIME_THRESHOLD}ms"
            )

        # Check keyword
        if result['keyword_found'] is False:
            issues.append("Expected keyword not found in response")

        # Check for errors
        if result['error']:
            issues.append(f"Probe error — {result['error']}")

        result['issues'] = issues
        result['healthy'] = len(issues) == 0
        validated.append(result)

    return validated