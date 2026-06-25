from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'


class BurstAnonRateThrottle(AnonRateThrottle):
    scope = 'anon'


class BurstUserRateThrottle(UserRateThrottle):
    scope = 'user'
