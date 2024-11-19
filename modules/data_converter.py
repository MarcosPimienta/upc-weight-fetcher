def convert_to_grams(weight, unit):
    """
    Converts weight to grams based on the unit.

    Parameters:
    - weight: The weight value as a float.
    - unit: The unit of weight as a string.

    Returns:
    - Weight in grams as a float.
    """
    conversion_factors = {
        'kg': 1000,
        'g': 1,
        'lb': 453.592,
        'pound': 453.592,
        'pounds': 453.592,
        'oz': 28.3495,
        'ounce': 28.3495,
        'ounces': 28.3495
    }
    unit = unit.lower()
    factor = conversion_factors.get(unit)
    if factor:
        return weight * factor
    else:
        print(f"Unknown weight unit '{unit}'. Cannot convert to grams.")
        return None
