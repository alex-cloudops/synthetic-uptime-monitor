# synthetic-uptime-monitor

A production-grade synthetic monitoring agent that continuously probes URLs, APIs, and endpoints for availability, response time, and health status — firing alerts via AWS SNS when targets go down or respond too slowly.

Built to mirror real-world NOC and CloudOps uptime monitoring workflows.

---

## Overview

Modern infrastructure teams need to know about outages before users do. `synthetic-uptime-monitor` provides a configurable, deployable Python agent that probes any HTTP/HTTPS endpoint, validates response codes and content, measures response times, and fires immediate alerts through AWS SNS when issues are detected.

This project demonstrates core CloudOps and SRE competencies:
- Synthetic endpoint probing with retry logic
- Response time measurement and threshold alerting
- Config-driven target management via JSON
- AWS SNS alert delivery
- Structured JSON reporting

---

## Architecture
```
config/targets.json
        │
        ▼
  prober.py          # HTTP/HTTPS endpoint probing with retry
        │
        ▼
  validator.py       # Response validation and issue detection
        │
        ▼
  alerter.py         # AWS SNS alert delivery
        │
        ▼
  reporter.py        # JSON report generation
        │
        ▼
logs/report.json     # Full structured results report
```

---

## Features

- **Multi-target probing** — Monitor unlimited endpoints from a single `targets.json`
- **Response time measurement** — Millisecond-precision timing with configurable thresholds
- **Status code validation** — Verify expected HTTP response codes
- **Keyword validation** — Confirm expected content is present in responses
- **AWS SNS alerting** — Immediate notifications on failures
- **Retry logic** — Configurable retry attempts before marking a target DOWN
- **JSON reporting** — Structured results report per run
- **Config-driven** — Zero hardcoded values

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.x |
| HTTP Probing | requests |
| AWS SDK | boto3 / botocore |
| Alerting | AWS SNS |
| Target Config | JSON |
| Configuration | configparser |

---

## Project Structure
```
synthetic-uptime-monitor/
├── monitor/
│   ├── __init__.py
│   ├── prober.py          # HTTP endpoint probing
│   ├── validator.py       # Response validation
│   ├── alerter.py         # SNS alert delivery
│   └── reporter.py        # JSON report generation
├── config/
│   ├── config.ini         # Agent configuration
│   └── targets.json       # Monitoring targets
├── logs/
│   └── uptime.log
├── tests/
│   └── __init__.py
├── requirements.txt
└── main.py
```

---

## Getting Started

### Prerequisites
- Python 3.8+
- AWS account (Free Tier compatible)
- AWS CLI installed and configured

### Installation
```bash
git clone https://github.com/Alex-CloudOps/synthetic-uptime-monitor.git
cd synthetic-uptime-monitor
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Configuration

Edit `config/config.ini`:
```ini
[monitor]
interval_seconds = 60
timeout_seconds = 10
retry_attempts = 3

[thresholds]
response_time_ms = 2000
consecutive_failures = 2

[aws]
region = us-east-2
sns_topic_arn = arn:aws:sns:us-east-2:YOUR_ACCOUNT_ID:cloud-telemetry-alerts
```

### Adding Monitoring Targets

Edit `config/targets.json`:
```json
{
    "targets": [
        {
            "name": "My API",
            "url": "https://api.example.com/health",
            "method": "GET",
            "expected_status": 200,
            "keyword": "healthy",
            "enabled": true
        }
    ]
}
```

### Run the Monitor
```bash
python main.py
```

---

## Sample Output
```
=======================================================
  SYNTHETIC UPTIME MONITOR
=======================================================
🎯 Loaded 5 monitoring target(s)

📡 Probing targets...
  Probing: Google...
  Probing: GitHub...
  Probing: AWS Console...
  Probing: HTTPBin Health Check...
  Probing: HTTPBin Simulated Failure...

🚨 Processing alerts...
    🚨 Alert sent for HTTPBin Simulated Failure

=======================================================
  ✅ COMPLETE
  Targets Probed  : 5
  UP              : 4
  DOWN            : 1
  Alerts Fired    : 1
  Avg Response    : 353.9ms
  Overall Health  : DEGRADED
=======================================================
```

---

## Roadmap

- [ ] Continuous polling loop with configurable interval
- [ ] Response time trending and history
- [ ] Dashboard integration via exported JSON
- [ ] Docker containerization
- [ ] Power BI uptime dashboard integration
- [ ] Unit tests with pytest

---

## Author

**Alex Evans** | CloudOps & NOC Engineer
[GitHub](https://github.com/Alex-CloudOps) | alex.evans.cloudops@gmail.com

---

*Built to demonstrate production-grade synthetic monitoring and NOC engineering practices.*