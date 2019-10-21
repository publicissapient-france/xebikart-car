/* 
    Copyright (C) 2017 by Mark Woehrer. This work is licensed under the Creative Commons Attribution 3.0 Unported License. To view a copy of this license, visit https://creativecommons.org/licenses/by-sa/3.0/legalcode.
*/

module four_point_stamper(SpacingFrontToBack, SpacingSideToSide)
{
    translate([-SpacingFrontToBack/2,-SpacingSideToSide/2,0])
    children();

    translate([-SpacingFrontToBack/2,+SpacingSideToSide/2,0])
    children();

    translate([+SpacingFrontToBack/2,-SpacingSideToSide/2,0])
    children();

    translate([+SpacingFrontToBack/2,+SpacingSideToSide/2,0])
    children();
    
}

module four_point_stamper_mirror(SpacingFrontToBack, SpacingSideToSide)
{
    translate([-SpacingFrontToBack/2,-SpacingSideToSide/2,0])
    children();

    mirror([0,1,0])
    translate([-SpacingFrontToBack/2,-SpacingSideToSide/2,0])
    children();

    mirror([1,0,0])
    translate([-SpacingFrontToBack/2,-SpacingSideToSide/2,0])
    children();

    mirror([0,1,0])
    mirror([1,0,0])
    translate([-SpacingFrontToBack/2,-SpacingSideToSide/2,0])
    children();
    
}

module nut_shape(widthAcrossFlats = 5)
{
    sideLength = widthAcrossFlats / sqrt(3);

	for (i = [0:2]) // implicit intersection
	{
        rotate(i*60 + 30)
        square([widthAcrossFlats,sideLength], center=true);

    }
    
}

//nut_shape();

module test_nut_shape()
{
    difference()
    {
        height = 2;
        translate([0,0,height/2])
        cube([10,10,height], center=true);
        linear_extrude(height=height)
        nut_shape(5);
        
    }
}

//test_nut_shape();

module nut_shape_cutout(widthAcrossFlats = 5, thickness = 1)
{
    linear_extrude(height=thickness)
    nut_shape(widthAcrossFlats,thickness);
    
}

//nut_shape_cutout();

function convex_isosceles_trapezoid_points(topWidth, bottomWidth, height)
  = [
    [-bottomWidth/2,0], 
    [-topWidth/2,height], 
    [+topWidth/2,height], 
    [+bottomWidth/2,0]];

module convex_isosceles_trapezoid(topWidth, bottomWidth, height)
{
    // Link: https://en.wikipedia.org/wiki/Isosceles_trapezoid

    polygon(points=convex_isosceles_trapezoid_points(topWidth, bottomWidth, height));
}


//convex_isosceles_trapezoid(15,10,5);

function my_translate_y(points, distance) = [
    [points[0][0], points[0][1] + distance, points[0][2]],
    [points[1][0], points[1][1] + distance, points[1][2]],
    [points[2][0], points[2][1] + distance, points[2][2]],
    [points[3][0], points[3][1] + distance, points[3][2]]];

function my_set_z(points, height) = [
    [points[0][0],points[0][1], height],
    [points[1][0],points[1][1], height],
    [points[2][0],points[2][1], height],
    [points[3][0],points[3][1], height]];


module my_loft(PolygonPointsA, PolygonPointsB)
{
    CubePoints = [
      [ PolygonPointsA[0][0],  PolygonPointsA[0][1], PolygonPointsA[0][2] ],  //0
      [ PolygonPointsA[1][0],  PolygonPointsA[1][1], PolygonPointsA[1][2] ],  //1
      [ PolygonPointsA[2][0],  PolygonPointsA[2][1], PolygonPointsA[2][2] ],  //2
      [ PolygonPointsA[3][0],  PolygonPointsA[3][1], PolygonPointsA[3][2] ],  //3

      [ PolygonPointsB[0][0],  PolygonPointsB[0][1], PolygonPointsB[0][2] ],  //4
      [ PolygonPointsB[1][0],  PolygonPointsB[1][1], PolygonPointsB[1][2] ],  //5
      [ PolygonPointsB[2][0],  PolygonPointsB[2][1], PolygonPointsB[2][2] ],  //6
      [ PolygonPointsB[3][0],  PolygonPointsB[3][1], PolygonPointsB[3][2] ]]; //7
      
    CubeFaces = [
      [0,1,2,3],  // bottom
      [4,5,1,0],  // front
      [7,6,5,4],  // top
      [5,6,2,1],  // right
      [6,7,3,2],  // back
      [7,4,0,3]]; // left
      
    polyhedron( CubePoints, CubeFaces );
    
}

module my_loft_2d(Polygon2DPointsA, Polygon2DPointsB, height)
{
    PolygonPointsA = my_set_z(Polygon2DPointsA, 0);

    //echo("PolygonPointsA:");
    //echo(PolygonPointsA);
    
    PolygonPointsB = my_set_z(Polygon2DPointsB, height);
    
    //echo("PolygonPointsB:");
    //echo(PolygonPointsB);
   
    my_loft(PolygonPointsA, PolygonPointsB);
}

// ---

module rounded_corner_shape(CornerRadius)
{
    difference()
    {
        square(2*CornerRadius,center=true);
        
        translate([CornerRadius,CornerRadius,0])
        circle(CornerRadius);
    }

}

//rounded_corner_shape(5);

module rounded_corner_cutout(height, radius)
{
    translate([0, 0, -height/2])
    linear_extrude(height)
    rounded_corner_shape(radius);
}

//rounded_corner_cutout(height=2, radius=2);


module rounded_corners_block(size, radius)
{
    difference()
    {
        cube(size, center=true);
        
        width=size[0];
        depth=size[1];
        height = size[2];
        
        four_point_stamper_mirror(width, depth)
        {
            rounded_corner_cutout(height, radius);
        
        }

    }
}

//rounded_corners_block([15,10,5], radius=1);
