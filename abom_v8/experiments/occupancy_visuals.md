# Occupancy and radial-shell visual experiments

This document records the design concepts supplied for the ABOM-V8 experiment series.

## Occupancy boundary sequence

The supplied five-state sequence depicts complementary UHFE/UDFE lobes within a circular boundary, with occupancy values (N=0.95,0.75,0.50,0.25,0.05). The stated intended invariant is equal-and-opposite area partitioning (excluding the eye features) and a changing pair of semicircular boundary diameters. Treat these as a visual construction to reproduce and test, not as a proven geometric identity of every lemniscate.

The plotted occupancy relation is a Fermi-Dirac sigmoid with complement (1-N). Its midpoint is (N=1/2).

## Focus-radius and entropy plots

A separate plot compares occupied and unoccupied focal radii with binary entropy over reduced energy. These curves are a visualization hypothesis. The implementation should keep radius laws configurable and test whether the displayed formulas are mutually consistent; do not hard-code them as canonical physical laws.

## Radial shell sequence

The radial-point visual suggests a scale-shell view. The shell generator should be a separate visualization plug-in with explicit scale ratio, shell count, point-count policy and orientation. It must not assume that a visually radial pattern is an E8 root system or a quasicrystal. Any connection to Gosset (4_{21}), E8 or quasicrystal cut-and-project requires independent exact mapping and validation.

## Vector differential operators

The accompanying operator sheet motivates optional gradient/divergence/curl/Laplacian diagnostics. See `../diagnostics/README.md` for domain and operator qualifications.