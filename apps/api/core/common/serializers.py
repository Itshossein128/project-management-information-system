from rest_framework import serializers

from common.jalali import gregorian_to_jalali, parse_jalali_or_gregorian


class JalaliDateField(serializers.Field):
    """Read/write Jalali date strings; stores Gregorian ``date`` in the ORM."""

    default_error_messages = {
        'invalid': 'Invalid date format. Use Jalali YYYY/MM/DD or ISO YYYY-MM-DD.',
    }

    def to_representation(self, value):
        if value is None:
            return None
        return gregorian_to_jalali(value)

    def to_internal_value(self, data):
        if data in (None, ''):
            return None
        try:
            return parse_jalali_or_gregorian(str(data))
        except (ValueError, TypeError):
            self.fail('invalid')
