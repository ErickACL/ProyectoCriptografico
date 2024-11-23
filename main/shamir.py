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

def lagrange_interpolation(x, x_values, y_values):
    """
    Realiza la interpolación de Lagrange.
    
    :param x: El valor de x en el cual se debe evaluar el polinomio interpolante.
    :param x_values: Los valores de x correspondientes a los puntos de interpolación (IDs de fragmentos).
    :param y_values: Los valores de y correspondientes a los puntos de interpolación (fragmentos).
    :return: El valor interpolado en el punto x.
    """
    total_sum = 0
    for i in range(len(x_values)):
        xi, yi = x_values[i], y_values[i]
        product = yi
        for j in range(len(x_values)):
            if i != j:
                product *= (x - x_values[j]) / (xi - x_values[j])
        total_sum += product
    return total_sum

def combine_shares(shares):
    """
    Combina los fragmentos para recomponer la clave maestra.
    
    :param shares: Lista de fragmentos como tuplas (id, valor).
    :return: La clave maestra recombinada.
    """
    # Asegurarse de que haya suficientes fragmentos para recomponer la clave
    if len(shares) < 3:
        raise ValueError("Se requieren al menos 3 fragmentos para recomponer la clave.")
    
    # Ordenar los fragmentos por id
    shares = sorted(shares, key=lambda x: x[0])

    # Extraer los valores de x (IDs de los fragmentos) y y (valores de los fragmentos)
    x_values = [share[0] for share in shares]
    y_values = [share[1] for share in shares]
    
    # La clave se puede reconstruir evaluando el polinomio en x=0
    recombined_key = lagrange_interpolation(0, x_values, y_values)
    
    # El valor resultante será un número entero
    return int(recombined_key)
