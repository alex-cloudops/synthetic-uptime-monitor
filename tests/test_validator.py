import pytest
from monitor.validator import validate_results


def make_result(status='UP', response_time_ms=200, keyword_found=None, error=None):
    """Helper — build a probe result with controlled values."""
    return {
        'name': 'Test Target',
        'url': 'https://example.com',
        'timestamp': '2026-03-11T00:00:00+00:00',
        'status': status,
        'status_code': 200 if status == 'UP' else 503,
        'response_time_ms': response_time_ms,
        'keyword_found': keyword_found,
        'error': error
    }


class TestDownTargets:
    def test_down_target_is_unhealthy(self):
        results = validate_results([make_result(status='DOWN')])
        assert results[0]['healthy'] is False

    def test_down_target_has_issue_recorded(self):
        results = validate_results([make_result(status='DOWN')])
        assert len(results[0]['issues']) > 0

    def test_up_target_with_no_issues_is_healthy(self):
        results = validate_results([make_result(status='UP', response_time_ms=200)])
        assert results[0]['healthy'] is True

    def test_up_target_with_no_issues_has_empty_issues_list(self):
        results = validate_results([make_result(status='UP', response_time_ms=200)])
        assert results[0]['issues'] == []


class TestResponseTimeThreshold:
    def test_slow_response_is_unhealthy(self):
        results = validate_results([make_result(response_time_ms=2001)])
        assert results[0]['healthy'] is False

    def test_slow_response_has_issue_recorded(self):
        results = validate_results([make_result(response_time_ms=2001)])
        assert len(results[0]['issues']) > 0

    def test_response_at_threshold_is_unhealthy(self):
        # 2000ms is the threshold — exactly at it should trigger
        results = validate_results([make_result(response_time_ms=2000)])
        assert results[0]['healthy'] is False

    def test_response_just_below_threshold_is_healthy(self):
        results = validate_results([make_result(response_time_ms=1999)])
        assert results[0]['healthy'] is True

    def test_none_response_time_does_not_cause_error(self):
        results = validate_results([make_result(status='DOWN', response_time_ms=None)])
        assert 'healthy' in results[0]


class TestKeywordValidation:
    def test_keyword_not_found_is_unhealthy(self):
        results = validate_results([make_result(keyword_found=False)])
        assert results[0]['healthy'] is False

    def test_keyword_not_found_has_issue_recorded(self):
        results = validate_results([make_result(keyword_found=False)])
        assert len(results[0]['issues']) > 0

    def test_keyword_found_does_not_add_issue(self):
        results = validate_results([make_result(keyword_found=True)])
        assert results[0]['healthy'] is True

    def test_none_keyword_does_not_add_issue(self):
        # keyword=None means no keyword check configured — should not flag
        results = validate_results([make_result(keyword_found=None)])
        assert results[0]['healthy'] is True


class TestErrorHandling:
    def test_probe_error_is_unhealthy(self):
        results = validate_results([make_result(error='Connection refused')])
        assert results[0]['healthy'] is False

    def test_probe_error_has_issue_recorded(self):
        results = validate_results([make_result(error='Timeout after 10s')])
        assert len(results[0]['issues']) > 0

    def test_no_error_does_not_add_issue(self):
        results = validate_results([make_result(error=None)])
        assert results[0]['healthy'] is True


class TestMultipleTargets:
    def test_each_result_gets_validated_independently(self):
        results = validate_results([
            make_result(status='UP', response_time_ms=200),
            make_result(status='DOWN'),
            make_result(status='UP', response_time_ms=200),
        ])
        assert results[0]['healthy'] is True
        assert results[1]['healthy'] is False
        assert results[2]['healthy'] is True

    def test_returns_same_count_as_input(self):
        input_results = [make_result() for _ in range(5)]
        output_results = validate_results(input_results)
        assert len(output_results) == 5