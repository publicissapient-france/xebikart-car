/* 
    Copyright (C) 2017 by Mark Woehrer. This work is licensed under the Creative Commons Attribution 3.0 Unported License. To view a copy of this license, visit https://creativecommons.org/licenses/by-sa/3.0/legalcode.
*/

include <Utility.scad>
include <Shared_Interface.scad>


import("Melded2.stl", convexity = 5  , center = true);

$fn = 100; // For faster rendering comment this line out. Enable for final print.

// Screws

Nominal_M2_ScrewHoleDiameter = 2.0;

// Nuts

Nominal_M2o5_NutHeight = 2.0;

// Front Part

FrontBaseDepth = 95;
FrontBaseWidth = 30;
FrontFaceBaseDepth = 40;

FrontHeight = 90;
FrontInnerHeight = 70;

RollCageTopHeight = FrontHeight - FrontInnerHeight;

// Camera Mount

CameraPitchAngle = 15;

WedgeCutoutWidth = 26;
WedgeCutoutDepth = 10;
WedgeCutoutHeight = 25;
WedgeCutoutAngle = CameraPitchAngle;

CameraMountHoleSpacingTopToBottom = 13;
CameraMountHoleSpacingSideToSide = 21;

// Camera Mount Spacers

CameraMountSpacerLength = 2; // For M2x6 screw
//CameraMountSpacerLength = 4; // For M2x8 screw

//CameraMountSpacerOuterDiamter = 6; // Original Donkey
CameraMountSpacerOuterDiameter = 4.5;
CameraMountSpacerInnerDiameter = 2 + 0.2;

NominalCameraMountHoleDiameter = 2.25;
CameraMountHoleDiameter = NominalCameraMountHoleDiameter + 0.2;

// Roll Cage Handle

FrontHandleHeight = 18.9;
FrontHandleTopWidth = 34.299;
FrontHandleBottomWidth = 20.279;

HandleHeight = 11.658;
HandleTopWidth = 22.486;
HandleBottomWidth = 14;

HandleFooLength = 114;
HandleEndLength = 10;

// Roll Cage

RollCageMountHoleLength = 20;
RollCageMountHoleDiameter = M2o5_ScrewHoleDiameter;

RollCageNutSlotCutoutHeightFromBase = 3;

RollCageNutSlotCutoutWidth = 8;
RollCageNutSlotCutoutDepth = 20;
//RollCageNutSlotCutoutHeight = 2; // Original Donkey
RollCageNutSlotCutoutHeight = Nominal_M2o5_NutHeight + 0.5;

// Nut Tray

NutTrayWidth = RollCageNutSlotCutoutWidth - 0.2;
NutTrayDepth = 10;
NominalNutTrayHeight = Nominal_M2o5_NutHeight;
NutTrayHeight = NominalNutTrayHeight - 0.3; // Adjustment for printer

NominalNutTrayNutCutoutWidthAcrossFlats = 5;
NutTrayNutCutoutWidthAcrossFlats = NominalNutTrayNutCutoutWidthAcrossFlats + 0.15;


// ---

module front_part_shape()
{
    polygon(points=[
    [-FrontBaseWidth/2,FrontBaseDepth/2], 
    [FrontBaseWidth/2,FrontBaseDepth/2],
    [FrontBaseWidth/2, -FrontBaseDepth/2],
    [-FrontBaseWidth/2, -FrontBaseDepth/2],
    [-7, -FrontFaceBaseDepth/2],
    [-7, FrontFaceBaseDepth/2],
    ]);
    
    
}

//front_part_shape();

module front_part_solid()
{
    //color("Blue",1.0)
    //linear_extrude(height=90, scale=[0.63,0.9], slices = 100)
    linear_extrude(height=FrontHeight, scale=[0.63,0.9])
    front_part_shape();
}    

//front_part_solid();

module front_part_without_camera_mount()
{
    difference()
    {
        front_part_solid();
        
        linear_extrude(height=FrontInnerHeight, scale=[1.0,0.80])
        square([40,75],center=true);
    }    

}    

//front_part_without_camera_mount();

module camera_mount_face_cutout()
{
    // Mounting Screw Holes and Nut Cutouts

    // Screw Holes
    
    //ScrewHoleDepth = 5; // Original Donkey
    ScrewHoleDepth = 6;
    NominalScrewHoleDiameter = Nominal_M2_ScrewHoleDiameter;
    ScrewHoleDiameter = NominalScrewHoleDiameter - 0.1; // Adjustment for printer

    translate([0,0,ScrewHoleDepth/2])
    four_point_stamper_mirror(CameraMountHoleSpacingSideToSide, CameraMountHoleSpacingTopToBottom)
    {
        cylinder(d=ScrewHoleDiameter, h=ScrewHoleDepth, center=true);
        
    }

    // Lens Mount Screw Head Cutouts

//    translate([CameraLensMountScrewHoleSpacing/2, 0, CameraLensMountScrewHeadCutoutHeight/2])
//    cylinder(d=CameraLensMountScrewHeadCutoutDiameter, h=CameraLensMountScrewHeadCutoutHeight, center=true);
//
//    translate([-CameraLensMountScrewHoleSpacing/2, 0, CameraLensMountScrewHeadCutoutHeight/2])
//    cylinder(d=CameraLensMountScrewHeadCutoutDiameter, h=CameraLensMountScrewHeadCutoutHeight, center=true);
    
    
}

//camera_mount_face_cutout();


module camera_mount_cutout()
{
    rotate([WedgeCutoutAngle, 0, 0])
    translate([0, 0, -WedgeCutoutHeight/2])
    rotate([90,0,180])
    {
        translate([0,0,-WedgeCutoutDepth/2])
        cube([WedgeCutoutWidth, WedgeCutoutHeight, WedgeCutoutDepth], center=true);

        translate([0,-CameraMountHoleSpacingTopToBottom/2 + WedgeCutoutHeight/2 - 3,0])
        camera_mount_face_cutout();
        
    }
    
}

//camera_mount_cutout();

module test_roll_cage_camera_mount()
{
    RollCageCameraMountTestWidth = 36;
    RollCageCameraMountTestHeight = RollCageTopHeight;
    RollCageCameraMountTestDepth = 13.9;
    
    difference()
    {
        translate([0,RollCageCameraMountTestDepth/2,RollCageCameraMountTestHeight/2])
        cube([RollCageCameraMountTestWidth, RollCageCameraMountTestDepth, RollCageCameraMountTestHeight], center=true);
        
        translate([0, 0, RollCageTopHeight])
        camera_mount_cutout();
    }
    
}

//rotate([0,180,0])
//test_roll_cage_camera_mount();


module front_part()
{
    difference()
    {
        front_part_without_camera_mount();
        
        // Camera Mount Wedge Cutout
        
        translate([-4.4, 0, FrontHeight])
        rotate([0,0,-90])
        camera_mount_cutout();
        
    }    
}    

//front_part();

// ---

module handle()
{
    Polygon2DPointsA = convex_isosceles_trapezoid_points(FrontHandleTopWidth, FrontHandleBottomWidth, FrontHandleHeight);
    
    Polygon2DPointsB = convex_isosceles_trapezoid_points(HandleTopWidth, HandleBottomWidth, HandleHeight);
    
    Polygon2DPointsBTranslated = my_translate_y(Polygon2DPointsB, FrontHandleHeight-HandleHeight);
    
    my_loft_2d(Polygon2DPointsA, Polygon2DPointsBTranslated, HandleFooLength);
    
    
}

//handle();

module handle_end()
{
    Polygon2DPointsA = convex_isosceles_trapezoid_points(FrontHandleTopWidth, FrontHandleBottomWidth, FrontHandleHeight);
    
    Polygon2DPointsB = convex_isosceles_trapezoid_points(HandleTopWidth, HandleBottomWidth, HandleHeight);
    
    Polygon2DPointsBTranslated = my_translate_y(Polygon2DPointsB, FrontHandleHeight-HandleHeight);
    
    my_loft_2d(Polygon2DPointsA, Polygon2DPointsBTranslated, HandleEndLength);
    
}

//handle_end();


module roll_cage_handle()
{
//    translate([-rollCageHandleLength/2,0,0])
//    rotate([90,0,90])
//    linear_extrude(height=rollCageHandleLength)
//    handle_shape();

    translate([-57,0,-(FrontHandleHeight-HandleHeight)])
    rotate([90,0,90])
    handle();
    
    // Front Handle End

//    translate([-57, 0, -(FrontHandleHeight-HandleHeight)])
//    rotate([90,0,90])
//    //linear_extrude(HandleEndLength)
//    //convex_isosceles_trapezoid(FrontHandleTopWidth, FrontHandleBottomWidth, FrontHandleHeight);
//    handle_end();

    // Back Handle End

    mirror([1,0,0])
    translate([-57, 0, -(FrontHandleHeight-HandleHeight)])
    rotate([90,0,90])
    //linear_extrude(10)
    //convex_isosceles_trapezoid(FrontHandleTopWidth, FrontHandleBottomWidth, FrontHandleHeight);
    handle_end();
}

//roll_cage_handle();

module back_part()
{
    mirror([1,0,0])
    front_part_without_camera_mount();
    
}

//back_part();

module roll_cage_mount_hole_cutout()
{
    translate([0,0,RollCageMountHoleLength/2])
    cylinder(d=RollCageMountHoleDiameter, h=RollCageMountHoleLength, center=true);

}

//roll_cage_mount_hole_cutout();

module roll_cage_nut_slot_cutout()
{
    translate([0,0,RollCageNutSlotCutoutHeight/2])
    cube([RollCageNutSlotCutoutWidth,RollCageNutSlotCutoutDepth,RollCageNutSlotCutoutHeight], center=true);
    
}

//roll_cage_nut_slot_cutout();

module test_roll_cage_nut_slot_cutout()
{
    testWidth = 30;
    testDepth = 20;
    testHeight = 8;

    rotate([180,0,0])
    translate([RollCageMountHoleSpacingFrontToBack/2,RollCageMountHoleSpacingSideToSide/2,-testHeight])
    intersection()
    {
        translate([-RollCageMountHoleSpacingFrontToBack/2,-RollCageMountHoleSpacingSideToSide/2,testHeight/2])
        cube([testWidth,testDepth,testHeight],center=true);
        
        roll_cage();
    }
    
}

//test_roll_cage_nut_slot_cutout();


module roll_cage()
{
    
    difference()
    {
        union()
        {
            // Front Part
            
            translate([-RollCageMountHoleSpacingFrontToBack/2,0,0])
            front_part();
     
            // Handle
            
            translate([0,0,FrontHeight-HandleHeight])
            roll_cage_handle();

            // Back Part
            
            translate([RollCageMountHoleSpacingFrontToBack/2,0,0])
            back_part();
            
        }
        
        // Hole and Nut Cutouts
        
        four_point_stamper(RollCageMountHoleSpacingFrontToBack, RollCageMountHoleSpacingSideToSide)
        {
            roll_cage_mount_hole_cutout();
            // translate([0,0,RollCageNutSlotCutoutHeightFromBase])
            // roll_cage_nut_slot_cutout();
        }



    }
}    


//roll_cage();

module camera_mount_spacers()
{
    four_point_stamper(10, 10)
    
    //spacer(CameraMountSpacerOuterDiameter, CameraMountSpacerInnerDiameter, CameraMountSpacerLength);

    difference()
    {
        translate([0, 0, CameraMountSpacerLength/2])
        cylinder(d=CameraMountSpacerOuterDiameter, h=CameraMountSpacerLength, center=true);        

        echo("CameraMountSpacerInnerDiameter");
        echo(CameraMountSpacerInnerDiameter);

        translate([0, 0, CameraMountSpacerLength/2])
        cylinder(d=CameraMountSpacerInnerDiameter, h=CameraMountSpacerLength, center=true);       
       
        echo("CameraMountHoleDiameter");
        echo(CameraMountHoleDiameter);

        // Top Cutout
        SpacerInnerHeight = 0.5;
        TopCutoutHeight = CameraMountSpacerLength - SpacerInnerHeight;
        translate([0, 0, CameraMountSpacerLength - TopCutoutHeight/2])
        cylinder(d=CameraMountHoleDiameter, h=TopCutoutHeight, center=true);  
        
    }

}

//camera_mount_spacers();


module nut_tray()
{
    difference()
    {
        translate([0, 0, NutTrayHeight/2])
        cube([NutTrayWidth, NutTrayDepth, NutTrayHeight], center=true);
        
        rotate([0, 0, 30])
        nut_shape_cutout(NutTrayNutCutoutWidthAcrossFlats, NutTrayHeight);
    }
    
}

//nut_tray();

module nut_trays()
{
    four_point_stamper(15, 20)
    nut_tray();
    
}

//nut_trays();

// ---

// Things to test/tune before printing the roll cage

//test_roll_cage_camera_mount();

//test_roll_cage_nut_slot_cutout();

// ---

translate([0,0,FrontHeight])
rotate([180,0,0])
roll_cage();

//nut_trays();
