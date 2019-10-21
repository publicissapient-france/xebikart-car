/* 
    Copyright (C) 2017 by Mark Woehrer. This work is licensed under the Creative Commons Attribution 3.0 Unported License. To view a copy of this license, visit https://creativecommons.org/licenses/by-sa/3.0/legalcode.
*/

use <Roll Cage.scad>
use <Base Plate.scad>

// Use this file to check hole alignment between base plate and the roll cage.

BasePlateHeight = 5; // Copy/paste from base plate file

// Roll Cage

roll_cage();

// Base Plate
translate([0,0,-BasePlateHeight/2])
base_plate();