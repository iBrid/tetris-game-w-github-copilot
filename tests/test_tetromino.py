import sys
from pathlib import Path

# Ensure project root is on sys.path so tests can import project modules
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from tetromino import rotate_shape


def test_rotate_I_shape():
    I = [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]]
    r = rotate_shape(I)
    # after rotation there should still be exactly 4 blocks and they should form a vertical line
    total = sum(sum(row) for row in r)
    assert total == 4
    # check there's a column with 4 blocks
    has_full_column = any(sum(row[c] for row in r) == 4 for c in range(4))
    assert has_full_column

def test_rotate_roundtrip():
    shape = [[0,1,0,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]]
    r1 = rotate_shape(shape)
    r2 = rotate_shape(rotate_shape(rotate_shape(r1)))
    assert r2 == shape
