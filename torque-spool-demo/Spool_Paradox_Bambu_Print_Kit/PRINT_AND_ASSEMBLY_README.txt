LARGE SPOOL PARADOX DEMONSTRATOR — print and assembly
======================================================
Designed for Bambu-style FDM printers with 256 x 256 mm print area.

DIMENSIONS (assembled)
  Rolling wheel diameter:    180 mm
  Center drum diameter:       78 mm
  Overall width:             112 mm
  Ideal pull reversal angle: acos(39/90) = 64.3 degrees above horizontal
  (with optional TPU tires: ~65.1 degrees, depending on tire radius)

PRINT THESE
  1 x Spool_MALE_print_1x.stl   [includes recessed anchor post and alignment tongue]
  1 x Spool_FEMALE_print_1x.stl [includes matching socket and 3 screw countersinks]
  Optional: 2 x Optional_TPU_tire_print_2x.stl (print from flexible TPU)

HARDWARE / STRING
  3 x M4 x 16 mm BUTTON-HEAD screws (head diameter <= 8 mm)
  A hand M4 x 0.7 tap is recommended for the three pilot holes in the male plug.
  ~2 m of 1.5-2 mm braided cord. Avoid a very stretchy cord.
  Optional: glue at the center joint, not needed when screws hold securely.

SLICER STARTING POINT
  Printer: Bambu P1/X1/A1 series, 256 mm square build plate (or larger)
  Material: PLA or PETG. TPU 95A for optional tires.
  Print each main half as supplied, large wheel flat on build plate.
  Layer height: 0.20 mm
  Perimeters/walls: 4
  Infill: 18-25% gyroid (recommend 20%)
  Top/bottom layers: 5
  Supports: none.  Brim is optional.
  Tire, if used: print flat, in TPU, 3-4 walls, 15-25% infill.
  All parts are watertight meshes, verified after STL export.

ASSEMBLY
  1. Keep the two main parts wheel-outwards. Identify the small alignment
     tongue on the MALE plug and the matching notch in the FEMALE socket.
  2. Lightly deburr mating surfaces as needed. Align and slide the plug
     into the socket. They are printed with ~0.76 mm diametric clearance.
  3. The FEMALE piece has three radial counterbored holes close to the
     central seam. Align them with the pilot holes in the MALE plug.
  4. Tap the male pilot holes M4 x 0.7, if possible. Insert three M4 x 16 mm
     button-head screws through the female shell into the male plug.
     Tighten gently; overtightening can crack FDM plastic.
  5. Find the recessed vertical post in the center drum. Pass the string
     behind the post, tie it securely (e.g. two half hitches) and tuck the
     short end into its pocket. Wind several neat turns around the drum.
     The anchor stays below the cylindrical winding surface.
  6. Optional: stretch TPU tires over the two outer wheel rims. They are
     slightly undersized to grip the rims.

DEMONSTRATION
  Set the spool on a tabletop, with string coming off the UNDER-SIDE of
  the central drum and pulling away at angle theta above horizontal.
  Pull gently at low and high angles. The direction of rolling reverses
  around theta ~= 64 degrees. At the ideal critical angle, the pulling
  force has no moment about the floor contact point. With sufficient
  static friction the spool may remain at rest; on a slippery surface
  it may slip or slide instead. Try rubberized tires for more repeatable
  rolling, or remove tires to deliberately demonstrate the role of friction.

NOTES
  The engraved wheel-face label reads SPOOL PARADOX.
  The editable parametric OpenSCAD source is included.
  This is a classroom prop, not a load-bearing device.
