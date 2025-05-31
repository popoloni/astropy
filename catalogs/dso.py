"""
Additional deep sky objects catalog beyond Messier objects.
"""

from models import CelestialObject


def get_additional_dso():
    """Additional major deep sky objects beyond Messier catalog with magnitudes"""
    return [
        # Large/Emission Nebulae
        CelestialObject("NGC 7000/C20 North America Nebula", 20.968, 44.533, "120'x100'", 4.0),
        CelestialObject("NGC 6960/C34 Western Veil - Witch's Broom Nebula", 20.764, 30.711, "70'x6'", 7.0),
        CelestialObject("NGC 6992/C33 Eastern Veil - Network Nebula", 20.917, 31.717, "75'x12'", 7.0),
        CelestialObject("NGC 1499/C31 California Nebula", 4.033, 36.417, "145'x40'", 5.0),
        CelestialObject("IC 5070/C19 Pelican Nebula", 20.785, 44.357, "60'x50'", 8.0),
        CelestialObject("NGC 2237/C49 Rosette Nebula", 6.533, 4.950, "80'x80'", 6.0),
        CelestialObject("IC 1396 Elephant's Trunk Nebula", 21.619, 57.500, "170'x140'", 7.5),
        CelestialObject("IC 1805/C31 Heart Nebula", 2.567, 61.833, "100'x100'", 6.5),
        CelestialObject("NGC 2264/C41 Cone Nebula - Christmas Tree Cluster", 6.691, 9.890, "20'x10'", 7.2),
        CelestialObject("IC 2118 Witch Head Nebula", 5.417, -7.233, "180'x60'", 13.0),
        CelestialObject("NGC 7293/C63 Helix Nebula", 22.493, -20.837, "28'x23'", 7.6),
        CelestialObject("IC 434/B33 Horsehead Nebula", 5.683, -2.450, "60'x10'", 6.8),
        CelestialObject("NGC 6888/C27 Crescent Nebula", 20.192, 38.356, "25'x18'", 7.4),
        CelestialObject("NGC 2359/C46 Thor's Helmet", 7.250, -13.200, "22'x15'", 11.5),
        CelestialObject("NGC 6302/C69 Bug Nebula", 17.139, -37.097, "12.9'x6.2'", 12.8),
        CelestialObject("IC 1318 Butterfly - Gamma Cygni Nebula", 20.183, 40.250, "180'x180'", 7.0),
        CelestialObject("IC 2177 Seagull Nebula", 7.067, -10.700, "120'x30'", None),
        CelestialObject("IC 4628 Prawn Nebula", 16.567, -40.333, "60'x35'", None),
        CelestialObject("NGC 2024 Flame Nebula", 5.417, -1.850, "30'x30'", None),
        CelestialObject("NGC 2070 Tarantula Nebula", 5.642, -69.100, "40'x25'", 8.0),
        CelestialObject("NGC 2467 Skull and Crossbones Nebula", 7.583, -26.433, "15'x15'", None),
        CelestialObject("NGC 3576 Statue of Liberty Nebula", 11.167, -61.317, "4'x4'", None),
        CelestialObject("NGC 6357 Lobster - War and Peace Nebula", 17.475, -34.200, "40'x30'", None),
        CelestialObject("NGC 2736 Pencil Nebula", 9.050, -45.950, "20'x0.5'", None),

        # Open Clusters
        CelestialObject("IC 4665 Summer Beehive Cluster", 17.788, 5.700, "70'x70'", 4.2),
        CelestialObject("Collinder399 Coathanger/Brocchi's Cluster", 19.433, 20.183, "60'x60'", 3.6),
        CelestialObject("NGC 869/884/C14 Double Cluster - h and χ Persei", 2.367, 57.133, "60'x60'", 4.3),
        CelestialObject("NGC 752 C28", 1.950, 37.683, "50'x50'", 5.7),
        CelestialObject("NGC 7160", 21.900, 62.600, "7'x7'", 6.1),
        CelestialObject("IC 4756 Graff's Cluster", 18.650, 5.433, "52'x52'", 4.6),

        # Galaxies
        CelestialObject("NGC 253/C65 Sculptor Galaxy", 0.792, -25.288, "27.5'x6.8'", 7.1),
        CelestialObject("NGC 4565/C38 Needle Galaxy", 12.608, 25.983, "15.8'x1.9'", 9.6),
        CelestialObject("NGC 891/C23 Silver Sliver Galaxy", 2.375, 42.350, "13.5'x2.5'", 9.9),
        CelestialObject("NGC 5128/C77 Centaurus A", 13.425, -43.017, "25.7'x20.0'", 6.8),
        CelestialObject("NGC 4631/C32 Whale Galaxy", 12.700, 32.533, "15.5'x2.7'", 9.2),
        CelestialObject("NGC 4236 Draco Dwarf", 12.283, 69.467, "21.9'x7.2'", 9.7),
        CelestialObject("NGC 7331/C30 Deer Lick Group", 22.617, 34.417, "10.5'x3.7'", 9.5),
        CelestialObject("NGC 7814/C43 Little Sombrero", 0.050, 16.150, "5.5'x2.3'", 10.5),
        CelestialObject("NGC 6946/C12 Fireworks Galaxy", 20.583, 60.150, "11.2'x9.8'", 8.8),
        CelestialObject("NGC 4449/C21 Box Galaxy", 12.467, 44.100, "6.2'x4.4'", 9.6),

        # Planetary Nebulae
        CelestialObject("NGC 6543/C6 Cat's Eye Nebula", 17.967, 66.633, "0.3'x0.3'", 8.1),
        CelestialObject("NGC 7009/C55 Saturn Nebula", 21.067, -11.383, "0.4'x0.2'", 8.0),
        CelestialObject("NGC 6826/C15 Blinking Nebula", 19.750, 50.533, "0.5'x0.5'", 8.8),
        CelestialObject("NGC 7662/C22 Blue Snowball", 23.433, 42.550, "0.3'x0.3'", 8.3),
        CelestialObject("NGC 3242/C59 Ghost of Jupiter", 10.400, -18.633, "0.8'x0.7'", 7.8),
        CelestialObject("NGC 2392/C39 Eskimo Nebula", 7.483, 20.917, "0.8'x0.8'", 9.2),

        # Globular Clusters  
        CelestialObject("NGC 5139/C80 Omega Centauri", 13.442, -47.483, "36.3'x36.3'", 3.7),
        CelestialObject("NGC 104/C106 47 Tucanae", 0.400, -72.083, "30.9'x30.9'", 4.0),
        CelestialObject("NGC 6752/C93", 19.175, -59.983, "20.4'x20.4'", 5.4),
        CelestialObject("NGC 362/C104", 1.033, -70.850, "12.9'x12.9'", 6.4),
        CelestialObject("NGC 6397/C86", 17.683, -53.683, "25.7'x25.7'", 5.7),

        # Supernova Remnants
        CelestialObject("NGC 6960/6992 Veil Nebula Complex", 20.833, 31.033, "180'x180'", 7.0),
        CelestialObject("IC 443 Jellyfish Nebula", 6.283, 22.483, "50'x40'", None),
        CelestialObject("Simeis 147 Spaghetti Nebula", 5.650, 27.967, "180'x180'", None),
    ] 