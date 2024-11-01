from pint import UnitRegistry

def quantity_to_array(quantity):
    """
    Convert a pint.Quantity to an array of length 2 where index 0 is the scalar
    and index 1 is the unit as a string.

    Parameters:
    quantity (pint.Quantity): The quantity to convert.

    Returns:
    list: A list where index 0 is the scalar value and index 1 is the unit.
    """
    return [quantity.magnitude, str(quantity.units)]