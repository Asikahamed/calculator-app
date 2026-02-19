import pytest
from app.calculator import add, subtract, multiply, divide, power, modulo


class TestAdd:
    def test_positive_numbers(self):
        assert add(2, 3) == 5.0

    def test_negative_numbers(self):
        assert add(-1, -1) == -2.0

    def test_mixed_sign(self):
        assert add(-1, 1) == 0.0

    def test_floats(self):
        assert add(1.5, 2.5) == 4.0

    def test_zero(self):
        assert add(0, 0) == 0.0


class TestSubtract:
    def test_basic(self):
        assert subtract(10, 4) == 6.0

    def test_negative_result(self):
        assert subtract(2, 10) == -8.0

    def test_floats(self):
        assert subtract(5.5, 2.5) == 3.0


class TestMultiply:
    def test_basic(self):
        assert multiply(3, 4) == 12.0

    def test_by_zero(self):
        assert multiply(100, 0) == 0.0

    def test_negative(self):
        assert multiply(-3, 4) == -12.0

    def test_two_negatives(self):
        assert multiply(-3, -4) == 12.0


class TestDivide:
    def test_basic(self):
        assert divide(10, 2) == 5.0

    def test_float_result(self):
        assert divide(7, 2) == 3.5

    def test_divide_by_zero(self):
        with pytest.raises(ValueError, match="Division by zero"):
            divide(10, 0)

    def test_negative(self):
        assert divide(-10, 2) == -5.0


class TestPower:
    def test_basic(self):
        assert power(2, 3) == 8.0

    def test_power_of_zero(self):
        assert power(5, 0) == 1.0

    def test_power_of_one(self):
        assert power(5, 1) == 5.0

    def test_negative_exponent(self):
        assert power(2, -1) == 0.5


class TestModulo:
    def test_basic(self):
        assert modulo(10, 3) == 1.0

    def test_exact_division(self):
        assert modulo(10, 5) == 0.0

    def test_modulo_by_zero(self):
        with pytest.raises(ValueError, match="Modulo by zero"):
            modulo(10, 0)
