"""
Module containing functions to format data to a human readable string
"""


def format_duration(secs):
    """
    format a duration in seconds to a human readable string: "Hours h Minutes min Seconds s"
    """
    if secs < 60:
        return f"{secs} secondes"
    elif secs < 3600:
        if secs % 60 == 0:
            return f"{secs // 60}min"
        return f"{secs // 60}min {secs % 60}s"
    else:
        if secs % 3600 == 0:
            return f"{secs // 3600} heures"
        if secs % 60 == 0:
            return f"{secs // 3600}h {(secs % 3600) // 60}min"
        return f"{secs // 3600}h {(secs % 3600) // 60}min {secs % 60}s"


def format_mass(kg):
    """
    Format a mass in kg to a human readable string: "Mass kg" or "Mass g"

    Args:
        kg (float): the mass in kg

    Returns:
        (mass, unit): a tuple containing the mass (in the following unit) and the unit
    """
    if kg < 1:
        return (kg * 1000, "g")
    return (kg, "kg")
