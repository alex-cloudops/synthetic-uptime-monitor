import json
from monitor.prober import probe_all_targets
from monitor.validator import validate_results
from monitor.alerter import process_alerts
from monitor.reporter import generate_report


def load_targets():
    with open('config/targets.json', 'r') as f:
        data = json.load(f)
    return data['targets']


if __name__ == "__main__":
    print("=" * 55)
    print("  SYNTHETIC UPTIME MONITOR")
    print("=" * 55)

    # Load targets
    targets = load_targets()
    print(f"\n🎯 Loaded {len(targets)} monitoring target(s)\n")

    # Step 1: Probe
    print("📡 Probing targets...")
    probe_results = probe_all_targets(targets)

    # Step 2: Validate
    print("\n🔍 Validating results...")
    validated = validate_results(probe_results)

    # Step 3: Alert
    print("\n🚨 Processing alerts...")
    alerts_fired = process_alerts(validated)

    # Step 4: Report
    print("\n📄 Generating report...")
    report = generate_report(validated)

    # Summary
    summary = report['summary']
    print("\n" + "=" * 55)
    print(f"  ✅ COMPLETE")
    print(f"  Targets Probed  : {summary['total_targets']}")
    print(f"  UP              : {summary['up']}")
    print(f"  DOWN            : {summary['down']}")
    print(f"  Alerts Fired    : {alerts_fired}")
    print(f"  Avg Response    : {summary['avg_response_time_ms']}ms")
    print(f"  Overall Health  : {summary['overall_health']}")
    print("=" * 55)
