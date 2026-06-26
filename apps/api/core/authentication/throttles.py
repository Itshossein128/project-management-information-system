from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle, UserRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'


class BurstAnonRateThrottle(AnonRateThrottle):
    scope = 'anon'


class BurstUserRateThrottle(UserRateThrottle):
    scope = 'user'


class RoleAwareUserRateThrottle(UserRateThrottle):
    """Pick throttle scope from user role (admin > hr > default user)."""

    scope = 'user'

    def _resolve_scope(self, user) -> str:
        if user.is_superuser or user.groups.filter(name='admin').exists():
            return 'admin'
        if user.groups.filter(name='hr').exists():
            return 'hr'
        return 'user'

    def allow_request(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return True
        self.scope = self._resolve_scope(request.user)
        self.rate = self.get_rate()
        if self.rate is None:
            return True
        self.num_requests, self.duration = self.parse_rate(self.rate)
        return SimpleRateThrottle.allow_request(self, request, view)
