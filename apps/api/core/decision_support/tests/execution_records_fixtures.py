"""Literal independent inputs: existing 1..10 axes, finite/raw draft policies."""
import copy
METHODS = ('saw', 'topsis', 'ahp', 'ism', 'dematel')
def payload(**changes):
    return copy.deepcopy({'title': 'Recorded analysis', 'criteria': ['Cost', 'Quality'],
        'alternatives': ['Alpha', 'Beta'], 'selected_methods': list(METHODS),
        'weights': [2, 3], 'types': ['cost', 'benefit'], 'performance_matrix': [[4, 6], [2, 3]],
        'ahp_matrix': [[1, 2], [.5, 1]], 'ism_matrix': [[0, 1], [0, 0]],
        'dematel_matrix': [[0, None]], **changes})
TIME = '2026-10-13T00:00:00Z'
IDS = ['00000000-0000-0000-0000-'+str(i).zfill(12) for i in range(1, 26)]
