"""Independent binary ISM references, distinct from production calculation."""
import itertools
import math
import pytest
from config.exceptions import CodedValidationError
from decision_support.services import validators


def validate(names, matrix):
    return validators.validate_ism_inputs(names, matrix)


@pytest.mark.parametrize('value,code', [(None,'cell_empty'), ('','cell_empty'), ('0','non_numeric'), (True,'non_numeric'), (False,'non_numeric'), (0.5,'ism_relation_invalid'), (-1,'ism_relation_invalid'), (2,'ism_relation_invalid'), (float('inf'),'non_finite'), (float('nan'),'non_finite'), (10**400,'non_finite')])
def test_strict_binary_cell(value,code):
    with pytest.raises(CodedValidationError) as error:validate(['A'],[[value]])
    assert any(i['code']==code and i['path']=='ism_matrix.0.0' for i in error.value.detail['issues'])


@pytest.mark.parametrize('names,matrix,path', [([],[],'criteria'), (['A']*11,[[0]*11]*11,'criteria'), ([' '],[[0]],'criteria.0'), (['A','A'],[[0,0],[0,0]],'criteria.1'), ([True],[[0]],'criteria.0'), (['A'],4,'ism_matrix'), (['A'],[4],'ism_matrix.0'), (['A'],[[]],'ism_matrix.0'), (['A'],[[0],[0]],'ism_matrix')])
def test_names_shapes(names,matrix,path):
    with pytest.raises(CodedValidationError) as error:validate(names,matrix)
    assert any(i['path']==path for i in error.value.detail['issues'])


@pytest.mark.parametrize('value',[0,1,0.0,1.0])
def test_direct_diagonal_and_zero(value):
    assert validate([' A '],[[value]])=={'criteria':['A'],'ism_matrix':[[int(value)]]}

from importlib import import_module

def compute(names,matrix):
    return import_module('decision_support.services.ism_service').compute_ism(names,matrix)

NETWORKS=[
(['A'],[[0]],[[1]],[['A']],[]),
(['A'],[[1]],[[1]],[['A']],[]),
(['A','B','C'],[[0,0,0],[0,0,0],[0,0,0]],[[1,0,0],[0,1,0],[0,0,1]],[['A','B','C']],[]),
(['A','B','C'],[[0,1,0],[0,0,1],[0,0,0]],[[1,1,1],[0,1,1],[0,0,1]],[['C'],['B'],['A']],[]),
(['A','B','C','D'],[[0,1,1,0],[0,0,0,1],[0,0,0,1],[0,0,0,0]],[[1,1,1,1],[0,1,0,1],[0,0,1,1],[0,0,0,1]],[['D'],['B','C'],['A']],[]),
(['A','B','C'],[[0,1,0],[0,0,0],[0,0,0]],[[1,1,0],[0,1,0],[0,0,1]],[['B','C'],['A']],[]),
(['A','B','C'],[[0,1,0],[1,0,1],[0,0,0]],[[1,1,1],[1,1,1],[0,0,1]],[['C'],['A','B']],[{'level':2,'criteria':['A','B']}]),
(['A','B','C'],[[0,1,0],[0,0,1],[1,0,0]],[[1,1,1]]*3,[['A','B','C']],[{'level':1,'criteria':['A','B','C']}]),
(['A','B','C','D'],[[0,1,0,0],[1,0,1,0],[0,0,0,1],[0,0,1,0]],[[1,1,1,1],[1,1,1,1],[0,0,1,1],[0,0,1,1]],[['C','D'],['A','B']],[{'level':1,'criteria':['C','D']},{'level':2,'criteria':['A','B']}]),
(['A','B','C','D'],[[0,1,0,0],[1,0,0,0],[0,0,0,1],[0,0,1,0]],[[1,1,0,0],[1,1,0,0],[0,0,1,1],[0,0,1,1]],[['A','B','C','D']],[{'level':1,'criteria':['A','B']},{'level':1,'criteria':['C','D']}]),
]

@pytest.mark.parametrize('names,direct,reach,layers,groups',NETWORKS)
def test_exact_references(names,direct,reach,layers,groups):
    import copy
    before=copy.deepcopy(direct);result=compute(names,direct)
    assert direct==before
    assert result['reachability_matrix']==reach
    assert result['layers']==[{'level':i+1,'criteria':members} for i,members in enumerate(layers)]
    assert result['mutual_groups']==groups
    assert all(type(cell) is int and cell in (0,1) for row in result['reachability_matrix'] for cell in row)

@pytest.mark.parametrize('cycle',[False,True])
def test_ten_criteria(cycle):
    names=[f'C{i}' for i in range(10)]
    direct=[[int(j==i+1 or (cycle and i==9 and j==0)) for j in range(10)] for i in range(10)]
    result=compute(names,direct)
    assert result['reachability_matrix']==([[1]*10 for _ in range(10)] if cycle else [[int(j>=i) for j in range(10)] for i in range(10)])
    assert result['layers']==([{'level':1,'criteria':names}] if cycle else [{'level':i+1,'criteria':[names[9-i]]} for i in range(10)])

def test_exhaustive_traversal_oracle():
    for bits in itertools.product((0,1),repeat=9):
        direct=[list(bits[i*3:(i+1)*3]) for i in range(3)]
        expected=[]
        for start in range(3):
            visited={start};todo=[start]
            while todo:
                i=todo.pop()
                for j,val in enumerate(direct[i]):
                    if val and j not in visited:visited.add(j);todo.append(j)
            expected.append([int(j in visited) for j in range(3)])
        result=compute(['A','B','C'],direct)
        assert result['reachability_matrix']==expected
        flattened=[name for layer in result['layers'] for name in layer['criteria']]
        assert sorted(flattened)==['A','B','C'] and len(result['layers'])<=3

def test_defensive_derivation_failure_is_not_a_cycle_policy():
    from decision_support.services.ism_service import _extract_layers
    with pytest.raises(CodedValidationError) as error:
        _extract_layers(['A','B','C'],[[1,1,0],[0,1,1],[1,0,1]])
    assert error.value.detail['issues'][0]['code']=='ism_derivation_failed'
    assert compute(['A','B','C'],[[0,1,0],[0,0,1],[1,0,0]])['layers']==[{'level':1,'criteria':['A','B','C']}]
