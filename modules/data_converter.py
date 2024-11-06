def convert_to_grams(weight, unit):
    conversion_factors = {
        'kg': 1000,
        'g': 1,
        'lb': 453.592,
        'oz': 28.3495,
        'pounds': 453.592
    }
    return weight * conversion_factors.get(unit.lower(), 1)
