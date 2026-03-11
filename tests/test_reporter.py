import pytest
import json
from unittest.mock import patch, mock_open
from monitor.reporter import generate_report


def make_validated_result(status='UP', response_time_ms=200, healthy=True):
    """Helper — build a validated probe result."""
    return {
        'name': 'Test Target',
        'url': 'https://example.com',
        'timestamp': '2026-03-11T00:00:00+00:00',
        'status': status,
        'status_code': 200 if status == 'UP' else 503,
        'response_time_ms': response_time_ms,
        'keyword_found': None,
        'error': None,
        'issues': [] if healthy else ['Target is DOWN'],
        'healthy': healthy
    }


class TestSummaryCounts:
    @patch('monitor.reporter.open', mock_open())
    @patch('monitor.reporter.Path.mkdir')
    def test_total_targets_count_is_correct(self, mock_mkdir):
        results = [make_validated_result() for _ in range(5)]
        report = generate_report(results)
        assert report['summary']['total_targets'] == 5

    @patch('monitor.reporter.open', mock_open())
    @patch('monitor.reporter.Path.mkdir')
    def test_up_count_is_correct(self, mock_mkdir):
        results = [
            make_validated_result(status='UP'),
            make_validated_result(status='UP'),
            make_validated_result(status='DOWN', healthy=False),
        ]
        report = generate_report(results)
        assert report['summary']['up'] == 2

    @patch('monitor.reporter.open', mock_open())
    @patch('monitor.reporter.Path.mkdir')
    def test_down_count_is_correct(self, mock_mkdir):
        results = [
            make_validated_result(status='UP'),
            make_validated_result(status='DOWN', healthy=False),
            make_validated_result(status='DOWN', healthy=False),
        ]
        report = generate_report(results)
        assert report['summary']['down'] == 2

    @patch('monitor.reporter.open', mock_open())
    @patch('monitor.reporter.Path.mkdir')
    def test_all_up_gives_zero_down(self, mock_mkdir):
        results = [make_validated_result(status='UP') for _ in range(3)]
        report = generate_report(results)
        assert report['summary']['down'] == 0


class TestAverageResponseTime:
    @patch('monitor.reporter.open', mock_open())
    @patch('monitor.reporter.Path.mkdir')
    def test_avg_response_time_is_correct(self, mock_mkdir):
        results = [
            make_validated_result(response_time_ms=100),
            make_validated_result(response_time_ms=200),
            make_validated_result(response_time_ms=300),
        ]
        report = generate_report(results)
        assert report['summary']['avg_response_time_ms'] == 200.0

    @patch('monitor.reporter.open', mock_open())
    @patch('monitor.reporter.Path.mkdir')
    def test_none_response_times_are_excluded_from_avg(self, mock_mkdir):
        results = [
            make_validated_result(response_time_ms=200),
            make_validated_result(status='DOWN', response_time_ms=None, healthy=False),
        ]
        report = generate_report(results)
        assert report['summary']['avg_response_time_ms'] == 200.0

    @patch('monitor.reporter.open', mock_open())
    @patch('monitor.reporter.Path.mkdir')
    def test_all_none_response_times_returns_none(self, mock_mkdir):
        results = [
            make_validated_result(status='DOWN', response_time_ms=None, healthy=False),
        ]
        report = generate_report(results)
        assert report['summary']['avg_response_time_ms'] is None


class TestOverallHealthStatus:
    @patch('monitor.reporter.open', mock_open())
    @patch('monitor.reporter.Path.mkdir')
    def test_healthy_when_no_targets_down(self, mock_mkdir):
        results = [make_validated_result(status='UP') for _ in range(3)]
        report = generate_report(results)
        assert report['summary']['overall_health'] == 'HEALTHY'

    @patch('monitor.reporter.open', mock_open())
    @patch('monitor.reporter.Path.mkdir')
    def test_degraded_when_any_target_down(self, mock_mkdir):
        results = [
            make_validated_result(status='UP'),
            make_validated_result(status='DOWN', healthy=False),
        ]
        report = generate_report(results)
        assert report['summary']['overall_health'] == 'DEGRADED'

    @patch('monitor.reporter.open', mock_open())
    @patch('monitor.reporter.Path.mkdir')
    def test_degraded_when_all_targets_down(self, mock_mkdir):
        results = [make_validated_result(status='DOWN', healthy=False) for _ in range(3)]
        report = generate_report(results)
        assert report['summary']['overall_health'] == 'DEGRADED'


class TestReportStructure:
    @patch('monitor.reporter.open', mock_open())
    @patch('monitor.reporter.Path.mkdir')
    def test_report_contains_required_fields(self, mock_mkdir):
        results = [make_validated_result()]
        report = generate_report(results)
        assert 'generated_at' in report
        assert 'summary' in report
        assert 'results' in report

    @patch('monitor.reporter.open', mock_open())
    @patch('monitor.reporter.Path.mkdir')
    def test_results_list_matches_input(self, mock_mkdir):
        results = [make_validated_result() for _ in range(4)]
        report = generate_report(results)
        assert len(report['results']) == 4