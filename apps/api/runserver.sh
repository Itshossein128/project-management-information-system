#!/usr/bin/env bash
exec "$(dirname "$0")/django.sh" runserver "$@"
