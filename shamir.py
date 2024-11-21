import random
from functools import reduce

# Función para evaluar un polinomio en un punto
def _evaluate_polynomial(coefficients, x):
    result = 0
    for coefficient in reversed(coefficients):
        result = result * x + coefficient
    return result

# Función para generar coeficientes aleatorios
def _generate_coefficients(secret, degree):
    coefficients = [secret]  # La clave es el término independiente
    for _ in range(degree):
        coefficients.append(random.randint(0, 2**128 - 1))  # Aleatorio de 128 bits
    return coefficients

# Generar fragmentos usando el esquema de Shamir
def make_random_shares(minimum, shares, secret=None):
    if minimum > shares:
        raise ValueError("El número mínimo de fragmentos debe ser menor o igual al total.")

    if secret is None:
        raise ValueError("Debes proporcionar un secreto (clave maestra) como entero.")

    coefficients = _generate_coefficients(secret, minimum - 1)

    fragments = []
    for x in range(1, shares + 1):
        y = _evaluate_polynomial(coefficients, x)
        fragments.append((x, y))  # (x, y)

    return secret, fragments

# Recuperar el secreto usando interpolación de Lagrange
def recover_secret(shares):
    def lagrange_interpolation(x, x_s, y_s):
        terms = []
        for j in range(len(x_s)):
            numerator = 1
            denominator = 1
            for m in range(len(x_s)):
                if m != j:
                    numerator *= x - x_s[m]
                    denominator *= x_s[j] - x_s[m]
            terms.append(y_s[j] * numerator // denominator)
        return reduce(lambda a, b: a + b, terms)

    # Separar x e y
    x_s, y_s = zip(*shares)

    # Evaluar el secreto en x = 0
    secret = lagrange_interpolation(0, x_s, y_s)
    return secret
