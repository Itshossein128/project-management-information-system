"""A6-P4 nested sensitive redaction."""

from permissions.redaction import redact_sensitive_payload


def test_nested_wage_redacted_without_permission():
    payload = {
        'summary': {'wage': 100, 'title': 'ok'},
        'rows': [{'wage': 50, 'name': 'a'}, {'rates': [1, 2]}],
    }
    out = redact_sensitive_payload(payload, set())
    assert out['summary']['wage'] is None
    assert out['summary']['wage_redacted'] is True
    assert out['summary']['title'] == 'ok'
    assert out['rows'][0]['wage'] is None
    assert out['rows'][0]['name'] == 'a'


def test_wage_kept_with_view_wage():
    payload = {'nested': {'wage': 9}}
    out = redact_sensitive_payload(payload, {'view_wage'})
    assert out['nested']['wage'] == 9


def test_person_contacts_independent_of_stakeholder_permission():
    payload = {'email': 'a@b.c', 'mobile': '1'}
    out = redact_sensitive_payload(
        payload,
        {'view_sensitive_contacts'},
        redact_wages=False,
        redact_person_contacts=True,
    )
    assert out['email'] is None
    assert out['mobile'] is None
