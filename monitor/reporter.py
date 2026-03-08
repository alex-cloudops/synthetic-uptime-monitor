import json
import configparser
from datetime import datetime, timezone
from pathlib import Path

# Load config
config = configparser.ConfigParser()
config.read('config/config.ini')

REPORT_OUTPUT = config['reporting']['report_output']


def generate_report(validated_results):
    total = len(validated_results)
    up_count = sum(1 for r in validated_results if r['status'] == 'UP')
    down_count = sum(1 for r in validated_results if r['status'] == 'DOWN')
    unhealthy_count = sum(1 for r in validated_results if not r['healthy'])

    avg_response_time = None
    response_times = [
        r['response_time_ms'] for r in validated_results
        if r['response_time_ms'] is not None
    ]
    if response_times:
        avg_response_time = round(sum(response_times) / len(response_times), 2)

    report = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'summary': {
            'total_targets': total,
            'up': up_count,
            'down': down_count,
            'unhealthy': unhealthy_count,
            'avg_response_time_ms': avg_response_time,
            'overall_health': 'HEALTHY' if down_count == 0 else 'DEGRADED'
        },
        'results': validated_results
    }

    # Write report
    output_path = Path(REPORT_OUTPUT)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(report, f, indent=4)

    print(f"\n📄 Report written to: {REPORT_OUTPUT}")
    return report