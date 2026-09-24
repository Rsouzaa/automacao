"""Normalize Talos JSON reports for the dashboard API."""
import json
from pathlib import Path


ROOT_PATH = Path(__file__).resolve().parent.parent
DEFAULT_REPORT_PATH = ROOT_PATH / 'output' / 'reports' / 'talos_report.json'


def _duration(value):
    return round(float(value or 0), 2)


def _status(value):
    value = str(value or 'unknown').lower()
    return value if value in {'passed', 'failed', 'skipped'} else 'unknown'


def normalize_report(report):
    """Convert a Talos report to a predictable JSON-friendly dashboard model."""
    features = []
    failures = []
    for feature in report.get('features', []):
        scenarios = []
        for scenario in feature.get('elements', []):
            steps = []
            for step in scenario.get('steps', []):
                result = step.get('result', {})
                step_status = _status(result.get('status'))
                step_data = {
                    'keyword': step.get('keyword', ''),
                    'name': step.get('name', ''),
                    'status': step_status,
                    'duration': _duration(result.get('duration')),
                    'expected': result.get('expected_result', ''),
                    'actual': result.get('obtained_result', ''),
                    'screenshots': step.get('screenshots', []),
                }
                steps.append(step_data)
                if step_status == 'failed':
                    failures.append({
                        'feature': feature.get('name', ''),
                        'scenario': scenario.get('name', ''),
                        'step': step_data,
                    })

            scenario_status = _status(scenario.get('status'))
            scenario_data = {
                'name': scenario.get('name', ''),
                'status': scenario_status,
                'duration': _duration(scenario.get('duration')),
                'location': scenario.get('location', ''),
                'steps': steps,
            }
            scenarios.append(scenario_data)
            if scenario_status == 'failed' and not any(
                    item['scenario'] == scenario_data['name'] for item in failures
            ):
                failures.append({
                    'feature': feature.get('name', ''),
                    'scenario': scenario_data['name'],
                    'step': None,
                })

        features.append({
            'name': feature.get('name', ''),
            'status': _status(feature.get('status')),
            'duration': _duration(feature.get('duration')),
            'location': feature.get('location', ''),
            'tags': feature.get('tags', []),
            'scenarios': scenarios,
        })

    global_data = report.get('global_data', {})
    results = global_data.get('results', {})
    summary = {
        'features': int(results.get('total_features', len(features)) or 0),
        'scenarios': int(results.get('total_scenarios', sum(len(item['scenarios']) for item in features)) or 0),
        'steps': int(results.get('total_steps', sum(len(scenario['steps']) for feature in features for scenario in feature['scenarios'])) or 0),
        'passed': int(results.get('passed_scenarios', 0) or 0),
        'failed': int(results.get('failed_scenarios', 0) or 0),
        'skipped': int(results.get('steps_skipped', 0) or 0),
        'failed_steps': int(results.get('steps_failed', 0) or 0),
    }
    all_scenarios = [scenario for feature in features for scenario in feature['scenarios']]
    slowest_scenario = max(all_scenarios, key=lambda scenario: scenario['duration'], default=None)
    analytics = {
        'pass_rate': round((summary['passed'] / summary['scenarios']) * 100, 1) if summary['scenarios'] else 0,
        'average_scenario_duration': round(
            sum(scenario['duration'] for scenario in all_scenarios) / len(all_scenarios), 2
        ) if all_scenarios else 0,
        'step_statuses': {
            'passed': int(results.get('steps_passed', 0) or 0),
            'failed': summary['failed_steps'],
            'skipped': summary['skipped'],
        },
        'slowest_scenario': slowest_scenario,
    }
    return {
        'meta': {
            'date': global_data.get('date', ''),
            'application': global_data.get('application', 'AutomacaoBDD'),
            'environment': global_data.get('environment', ''),
            'version': global_data.get('version', ''),
            'duration': _duration((results.get('end_time') or 0) - (results.get('start_time') or 0)),
        },
        'summary': summary,
        'analytics': analytics,
        'features': features,
        'failures': failures,
    }


def load_report(report_path=DEFAULT_REPORT_PATH):
    """Load and normalize a Talos report, returning an empty state when absent."""
    report_path = Path(report_path)
    if not report_path.is_file():
        return {
            'meta': {'date': '', 'application': 'AutomacaoBDD', 'environment': '', 'version': '', 'duration': 0},
            'summary': {'features': 0, 'scenarios': 0, 'steps': 0, 'passed': 0, 'failed': 0, 'skipped': 0},
            'analytics': {
                'pass_rate': 0, 'average_scenario_duration': 0,
                'step_statuses': {'passed': 0, 'failed': 0, 'skipped': 0}, 'slowest_scenario': None,
            },
            'features': [],
            'failures': [],
            'message': f'Report not found: {report_path}',
        }
    with report_path.open(encoding='utf-8') as report_file:
        return normalize_report(json.load(report_file))