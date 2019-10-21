/* 
    Copyright (C) 2017 by Mark Woehrer. This work is licensed under the Creative Commons Attribution 3.0 Unported License. To view a copy of this license, visit https://creativecommons.org/licenses/by-sa/3.0/legalcode.
*/

include <Utility.scad>
include <Shared_Interface.scad>

$fn = 100; // For faster rendering comment this line out. Enable for final print.

// Screws

Nominal_M2o5_ScrewHoleDiameter = 2.5 + 0.25;
M2o5_ScrewHoleDiameter = Nominal_M2o5_ScrewHoleDiameter + 0.2; // Adjustment for printer

// Nuts
Nominal_M2o5_NutWidthAcrossFlats = 5;
M2o5_NutWidthAcrossFlats = Nominal_M2o5_NutWidthAcrossFlats + 0.2; // Adjustment for printer

// Cart
CartMountHoleSpacingFrontToBack = 175;
CartMountHoleSpacingSideToSide = 25;
NominalCarMountHoleDiameter = 5;
CarMountHoleDiameter = NominalCarMountHoleDiameter + 0.2; // Adjustment for printer

// Base Plate
BasePlateLength = 195;
BasePlateWidth = 95;
BasePlateHeight = 5;
BasePlateCornerRadius = 15;

BasePlateNutCutoutHeight = 2.5;

ClipCutoutHeightOffset = 3.0;
ClipCutoutHeight = BasePlateHeight - ClipCutoutHeightOffset;

// Pi Mounting Holes
PiMountingHolesSpacingA = 58;
PiMountingHolesSpacingB = 49;
PiMountingHoleDiameter = M2o5_ScrewHoleDiameter;

// Servo Driver Mounting Holes
ServoDriverMountingHolesSpacingA = 19;
ServoDriverMountingHolesSpacingB = 56;
ServoDriverMountingHoleDiameter = M2o5_ScrewHoleDiameter;

// Wire Cutouts
LargeWireCutoutCenterLength = 25;
LargeWireCutoutHoleDiameter = 15;

SmallWireCutoutCenterLength = 15;
SmallWireCutoutHoleDiameter = 5;
SmallWireCutoutSpacing = 56;

// Roll Cage
// See "Shared Interface.scad"

RollCageBackMountHoleFromCenterOffset = BasePlateLength/2 - 6.174;

// Base Plate Spacers

SpacerOuterDiameter = 5;
SpacerInnerDiameter = M2o5_ScrewHoleDiameter;
SpacerHeight = 6;

// ---

// Base Plate

module mounting_hole_cutout(MountingHoleDiameter)
{
    cylinder(d=MountingHoleDiameter, h=BasePlateHeight, center=true);
    
}

//mounting_hole_cutout(5);

module cart_mounting_holes_cutout()
{
    four_point_stamper(CartMountHoleSpacingFrontToBack, CartMountHoleSpacingSideToSide)
    mounting_hole_cutout(CarMountHoleDiameter);
}

//cart_mounting_holes_cutout();

module test_cart_mounting_holes()
{
    TestBasePlateLength = 20;
    TestBasePlateWidth = 45;
    
    TestBasePlateHeight = 3;
    
    difference()
    {
        cube([TestBasePlateLength,TestBasePlateWidth,TestBasePlateHeight],center=true);

        // Mounting Holes

        translate([0,CartMountHoleSpacingSideToSide/2,0])
        cylinder(d=CarMountHoleDiameter, h=TestBasePlateHeight, center=true);

        translate([0, -CartMountHoleSpacingSideToSide/2,0])
        cylinder(d=CarMountHoleDiameter, h=TestBasePlateHeight, center=true);

    }
    
}

//test_cart_mounting_holes();


module board_mounting_hole_cutout(MountingHoleDiameter)
{
    mounting_hole_cutout(MountingHoleDiameter);
    translate([0,0,-BasePlateHeight/2])
    nut_shape_cutout(M2o5_NutWidthAcrossFlats, BasePlateNutCutoutHeight);
    
}

//board_mounting_hole_cutout(M2o5_ScrewHoleDiameter);

module test_board_mounting_hole()
{
    difference()
    {
        cube([10,10,BasePlateHeight],center=true);
        
        board_mounting_hole_cutout(PiMountingHoleDiameter);        
        
    }
    
    
}

//test_board_mounting_hole();


module pi_mounting_holes_cutout()
{
    four_point_stamper(PiMountingHolesSpacingA, PiMountingHolesSpacingB)
    {
        board_mounting_hole_cutout(PiMountingHoleDiameter);

    }

}

//pi_mounting_holes_cutout();


module servo_driver_mounting_holes_cutout()
{
    four_point_stamper(ServoDriverMountingHolesSpacingA, ServoDriverMountingHolesSpacingB)
    {
        board_mounting_hole_cutout(ServoDriverMountingHoleDiameter);
    }

}

//servo_driver_mounting_holes_cutout();


module test_servo_servo_driver_mounting_holes()
{
    difference()
    {
        rounded_corners_block([ServoDriverMountingHolesSpacingA + 10,ServoDriverMountingHolesSpacingB + 10,BasePlateHeight], radius=5);

        
        servo_driver_mounting_holes_cutout();


    }
    
}

//test_servo_servo_driver_mounting_holes();


module wire_cutout(WireCutoutCenterLength, WireCutoutHoleDiameter)
{
    cube([WireCutoutHoleDiameter, WireCutoutCenterLength, BasePlateHeight], center=true);
    
    translate([0,WireCutoutCenterLength/2,0])
    cylinder(d=WireCutoutHoleDiameter, h=BasePlateHeight, center=true);

    translate([0,-WireCutoutCenterLength/2,0])
    cylinder(d=WireCutoutHoleDiameter, h=BasePlateHeight, center=true);
}

module large_wire_cutout()
{
    wire_cutout(LargeWireCutoutCenterLength, LargeWireCutoutHoleDiameter);

}

//large_wire_cutout();

module small_wire_cutout()
{
    wire_cutout(SmallWireCutoutCenterLength, SmallWireCutoutHoleDiameter);
}

//small_wire_cutout();

module small_wire_cutouts()
{
        translate([0, SmallWireCutoutSpacing/2,0])
        rotate([0,0,90])
        small_wire_cutout();

        translate([0, -SmallWireCutoutSpacing/2,0])
        rotate([0,0,90])
        small_wire_cutout();
}

//small_wire_cutouts();

module test_roll_cage_mounting_hole()
{
   translate([0,10,0])
    difference()
   {
        cube([10,10,BasePlateHeight],center=true);
        mounting_hole_cutout(RollCageMountHoleDiameter);

   } 

   translate([0,-10,0])
   difference()
   {
        cube([10,10,BasePlateHeight],center=true);
        mounting_hole_cutout(RollCageMountHoleDiameter);

   } 
   
    
}

//test_roll_cage_mounting_hole();

module roll_cage_mounting_holes_cutout()
{
    // Side Holes
    four_point_stamper(RollCageMountHoleSpacingFrontToBack, RollCageMountHoleSpacingSideToSide)
    mounting_hole_cutout(RollCageMountHoleDiameter);

    // Back Hole
    translate([RollCageBackMountHoleFromCenterOffset,0,0])
    mounting_hole_cutout(RollCageMountHoleDiameter);

}    
    
//roll_cage_mounting_holes_cutout();    

module clip_cutout()
{
    ClipCutoutLength = 16;
    ClipCutoutWidth = 10;

    translate([0,-ClipCutoutWidth/2,0])
    cube([ClipCutoutLength, ClipCutoutWidth, ClipCutoutHeight]);

    translate([ClipCutoutLength, 0, ClipCutoutHeight/2])
    cylinder(d=ClipCutoutWidth, h=ClipCutoutHeight, center=true);
}

//clip_cutout();

module front_clip_cutouts()
{
    translate([0,-CartMountHoleSpacingSideToSide/2,0])
    clip_cutout();

    translate([0,+CartMountHoleSpacingSideToSide/2,0])
    clip_cutout();
    
    
}

//front_clip_cutouts();

module clip_cutouts()
{
    // Front Clip Cutouts
    
    translate([-BasePlateLength/2, 0, 0])
    front_clip_cutouts();

    // Back Clip Cutouts

    // See here for mirror discription/discussion...
    // https://cubehero.com/2013/11/19/know-only-10-things-to-be-dangerous-in-openscad/

    mirror([1,0,0]) // Mirror across the yz-plane
    translate([-BasePlateLength/2, 0, 0])
    front_clip_cutouts();
    
    
}

//clip_cutouts();

module test_clip_cutout()
{
    testLength = 25;
    testWidth = 20;

    intersection()
    {
        translate([-BasePlateLength/2 + testLength/2,-CartMountHoleSpacingSideToSide/2,0])
        cube([testLength,testWidth,BasePlateHeight],center=true);

        base_plate();
    }
}

//test_clip_cutout();

module test_clip_cutout_two()
{
    testLength = 25;
    testWidth = 45;

    intersection()
    {
        translate([-BasePlateLength/2 + testLength/2,0,0])
        cube([testLength,testWidth,BasePlateHeight],center=true);

        base_plate();
    }
}

//test_clip_cutout_two();

module base_plate()
{
    difference()
    {
        rounded_corners_block([BasePlateLength,BasePlateWidth,BasePlateHeight],BasePlateCornerRadius);

        // Cart Mounting Holes

        cart_mounting_holes_cutout();

        // Pi Mounting Holes

        translate([-BasePlateLength/2 + PiMountingHolesSpacingA/2 + 58, 0, 0])
        pi_mounting_holes_cutout();

        // Servo Driver Mounting Holes

        translate([-BasePlateLength/2 + ServoDriverMountingHolesSpacingA/2 + 150, 0, 0])
        servo_driver_mounting_holes_cutout();

        // Large Wire Cutout
        
        translate([BasePlateLength/2 - 67,0,0])
        large_wire_cutout();

        // Small Wire Cutouts
        
        translate([-SmallWireCutoutCenterLength/2, 0, 0])
        small_wire_cutouts();
        
        // Roll Cage Mounting Holes

        roll_cage_mounting_holes_cutout();
        
        // Clip Cutouts

        translate([0,0,-BasePlateHeight/2 + ClipCutoutHeightOffset])
        clip_cutouts();

    }
   
}

//base_plate();

module spacer(SpacerOuterDiameter, SpacerInnerDiameter, SpacerHeight)
{
    difference()
    {
        cylinder(d=SpacerOuterDiameter, h=SpacerHeight, center=true);        

        cylinder(d=SpacerInnerDiameter, h=SpacerHeight, center=true);        
        
    }
    
}

module base_plate_spacers()
{
    four_point_stamper(10, 10)
    translate([0,0,SpacerHeight/2])
    spacer(SpacerOuterDiameter, SpacerInnerDiameter, SpacerHeight);
   
}

//base_plate_spacers();


// ---

// Things to test/tune before printing the base plate

//test_clip_cutout_two();

//test_roll_cage_mounting_hole();

//test_board_mounting_hole();


// ---

base_plate();

//base_plate_spacers();

