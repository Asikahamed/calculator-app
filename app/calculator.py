from typing import Union

Number = Union[int, float]


def add(a: Number, b: Number) -> float:
    return float(a + b)


def subtract(a: Number, b: Number) -> float:
    return float(a - b)


def multiply(a: Number, b: Number) -> float:
    return float(a * b)


def divide(a: Number, b: Number) -> float:
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    return float(a / b)


def power(a: Number, b: Number) -> float:
    return float(a ** b)


def modulo(a: Number, b: Number) -> float:
    if b == 0:
        raise ValueError("Modulo by zero is not allowed")
    return float(a % b)


OPERATIONS = {
    "add":      add,
    "subtract": subtract,
    "multiply": multiply,
    "divide":   divide,
    "power":    power,
    "modulo":   modulo,
}
