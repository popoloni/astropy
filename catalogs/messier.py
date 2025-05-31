"""
Messier catalog of deep sky objects.
"""

from models import CelestialObject


def get_messier_catalog():
    """Complete Messier Catalog with coordinates, FOV, and magnitudes"""
    return [
        # Nebulae
        CelestialObject("M1/NGC 1952 Crab Nebula", 5.575, 22.017, "6'x4'", 8.4),
        CelestialObject("M8/NGC 6523 Lagoon Nebula", 18.063, -24.383, "90'x40'", 6.0),
        CelestialObject("M16/NGC 6611 Eagle Nebula", 18.313, -13.783, "35'x28'", 6.4),
        CelestialObject("M17/NGC 6618 Omega - Swan Nebula", 18.346, -16.183, "46'x37'", 6.0),
        CelestialObject("M20/NGC 6514 Trifid Nebula", 18.033, -23.033, "28'x28'", 6.3),
        CelestialObject("M27/NGC 6853 Dumbbell Nebula", 19.994, 22.717, "8.0'x5.7'", 7.5),
        CelestialObject("M42/NGC 1976 Great Orion Nebula", 5.588, -5.391, "85'x60'", 4.0),
        CelestialObject("M43/NGC 1982 De Mairan's Nebula", 5.593, -5.267, "20'x15'", 9.0),
        CelestialObject("M57/NGC 6720 Ring Nebula", 18.884, 33.033, "1.4'x1'", 8.8),
        CelestialObject("M76/NGC 650/651 Little Dumbbell Nebula", 1.702, 51.567, "2.7'x1.8'", 10.1),
        CelestialObject("M97/NGC 3587 Owl Nebula", 11.248, 55.017, "3.4'x3.3'", 9.9),

        # Galaxies
        CelestialObject("M31/NGC 224 Andromeda Galaxy", 0.712, 41.269, "178'x63'", 3.4),
        CelestialObject("M32/NGC 221 Andromeda Companion", 0.712, 40.867, "8'x6'", 8.1),
        CelestialObject("M33/NGC 598 Triangulum Galaxy", 1.564, 30.660, "73'x45'", 5.7),
        CelestialObject("M51/NGC 5194 Whirlpool Galaxy", 13.497, 47.195, "11'x7'", 8.4),
        CelestialObject("M63/NGC 5055 Sunflower Galaxy", 13.158, 42.033, "12.6'x7.2'", 8.6),
        CelestialObject("M64/NGC 4826 Black Eye Galaxy", 12.944, 21.683, "10'x5'", 8.5),
        CelestialObject("M81/NGC 3031 Bode's Galaxy", 9.926, 69.067, "26.9'x14.1'", 6.9),
        CelestialObject("M82/NGC 3034 Cigar Galaxy", 9.928, 69.683, "11.2'x4.3'", 8.4),
        CelestialObject("M101/NGC 5457 Pinwheel Galaxy", 14.053, 54.349, "28.8'x26.9'", 7.9),
        CelestialObject("M104/NGC 4594 Sombrero Galaxy", 12.667, -11.617, "8.7'x3.5'", 8.0),
        CelestialObject("M106/NGC 4258", 12.317, 47.300, "18.6'x7.2'", 8.4),
        CelestialObject("M110/NGC 205", 0.683, 41.683, "17'x10'", 8.0),

        # Globular Clusters
        CelestialObject("M2/NGC 7089", 21.558, -0.817, "12.9'x12.9'", 6.5),
        CelestialObject("M3/NGC 5272", 13.703, 28.383, "16.2'x16.2'", 6.2),
        CelestialObject("M4/NGC 6121", 16.392, -26.533, "26.3'x26.3'", 5.6),
        CelestialObject("M5/NGC 5904", 15.310, 2.083, "17.4'x17.4'", 5.6),
        CelestialObject("M10/NGC 6254", 16.950, -4.100, "15.1'x15.1'", 6.6),
        CelestialObject("M13/NGC 6205 Great Hercules Cluster", 16.695, 36.459, "20'x20'", 5.8),
        CelestialObject("M15/NGC 7078", 21.500, 12.167, "12.3'x12.3'", 6.2),
        CelestialObject("M22/NGC 6656", 18.608, -23.900, "24'x24'", 5.1),
        CelestialObject("M55/NGC 6809", 19.667, -30.967, "19'x19'", 7.0),
        CelestialObject("M92/NGC 6341", 17.171, 43.133, "11.2'x11.2'", 6.4),

        # Open Clusters
        CelestialObject("M6/NGC 6405 Butterfly Cluster", 17.667, -32.217, "25'x15'", 4.2),
        CelestialObject("M7/NGC 6475 Ptolemy Cluster", 17.897, -34.817, "80'x80'", 3.3),
        CelestialObject("M23/NGC 6494", 17.950, -19.017, "27'x27'", 5.5),
        CelestialObject("M24/NGC 6603", 18.283, -18.517, "90'x90'", 4.6),
        CelestialObject("M25/IC 4725", 18.528, -19.233, "32'x32'", 4.6),
        CelestialObject("M34/NGC 1039", 2.702, 42.783, "35'x35'", 5.2),
        CelestialObject("M35/NGC 2168", 6.148, 24.333, "28'x28'", 5.1),
        CelestialObject("M36/NGC 1960 Pinwheel Cluster", 5.536, 34.133, "12'x12'", 6.0),
        CelestialObject("M37/NGC 2099 Salt and Pepper Cluster", 5.873, 32.550, "24'x24'", 5.6),
        CelestialObject("M38/NGC 1912 Starfish Cluster", 5.478, 35.833, "21'x21'", 6.4),
        CelestialObject("M39/NGC 7092", 21.535, 48.433, "32'x32'", 4.6),
        CelestialObject("M41/NGC 2287", 6.783, -20.733, "38'x38'", 4.5),
        CelestialObject("M44/NGC 2632 Beehive Cluster/Praesepe", 8.667, 19.983, "95'x95'", 3.1),
        CelestialObject("M45 Pleiades - Seven Sisters", 3.790, 24.117, "110'x110'", 1.6),
        CelestialObject("M46/NGC 2437", 7.697, -14.817, "27'x27'", 6.1),
        CelestialObject("M47/NGC 2422", 7.615, -14.483, "30'x30'", 4.4),
        CelestialObject("M48/NGC 2548", 8.233, -5.800, "54'x54'", 5.8),
        CelestialObject("M50/NGC 2323 Heart-Shaped Cluster", 7.033, -8.333, "16'x16'", 5.9),
        CelestialObject("M67/NGC 2682", 8.850, 11.817, "30'x30'", 6.9),
        CelestialObject("M93/NGC 2447", 7.742, -23.867, "22'x22'", 6.2),
    ] 