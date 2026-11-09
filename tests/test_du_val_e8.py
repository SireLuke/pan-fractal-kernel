try:
    from ..du_val_e8 import du_val_minimal_vectors, verify_du_val_e8
except ImportError:
    from du_val_e8 import du_val_minimal_vectors, verify_du_val_e8


def test_du_val_minimal_vectors_recover_e8_roots():
    roots = du_val_minimal_vectors()
    assert len(roots) == 240
    assert len(set(roots)) == 240
    assert all(sum(x * x for x in root) == 50 for root in roots)


def test_du_val_model_has_e8_root_invariants():
    result = verify_du_val_e8()
    assert result["independent_dimension"] == 8
    assert result["scaled_minimum_squared_norm"] == 2
    assert result["inner_product_distribution"] == {
        -2: 1, -1: 56, 0: 126, 1: 56, 2: 1
    }
    assert result["all_240_root_reflections_preserve_set"] is True
    assert result["scaled_covolume"] == 1
