// LARGE SPOOL PARADOX -- Bambu-ready printable demonstration
// mm; assembled OD 180mm, width 112mm, drum OD 78mm
// Two printed halves meet with a keyed male/female spigot. Three M4x16
// button-head screws fasten the joint. Male half has a recessed string cleat.
// Select "male", "female", "tire" or "assembled".
part = "male";
$fn=160;
wheel_R=90;
hub_R=39;
hub_bore_R=18;
wheel_thickness=9;
barrel_top=56;  // local height to center seam
spigot_R=29;
spigot_h=13;
clearance=0.38;  // radial (0.76mm diametric) FDM tolerance
screw_angles=[60,180,300];
screw_z_male=62.5;
screw_z_female=49.5;

module annulus(ro,ri,h) {
 difference(){cylinder(r=ro,h=h);translate([0,0,-0.1]) cylinder(r=ri,h=h+0.2);}
}

// Wide load-carrying outer tread + light-weight open spokes.
module wheel_blank(){
 linear_extrude(height=wheel_thickness)
 union(){
  difference(){circle(r=wheel_R);circle(r=73);}
  circle(r=43);
  for(a=[0:45:315]) rotate(a)
   hull(){translate([39,0]) circle(r=10);translate([77,0]) circle(r=8.5);}
 }
}

// Readable engraved lettering in the end hub face (printing starts face down).
module arc_word(word, angle0, angle1, bottom=false){
 n=len(word);
 for(i=[0:n-1]){
  a=angle0+(angle1-angle0)*i/max(1,n-1);
  rotate([0,0,a]) translate([33,0,-0.06])
   rotate([0,0,bottom? a*0+90 : -90])
   linear_extrude(height=0.9)
    text(word[i],size=6.6,font="DejaVu Sans:style=Bold",halign="center",valign="center");
 }
}

// Rotation above is about local axes. Characters are tangent to circle:
// top word: angle 132 => rotate(-90) yields 42deg; bottom: 226 => rotate(90) yields 316deg.
module wheel(){
 difference(){
  wheel_blank();
  // Open through-bore at the center. (A finger can assist string routing.)
  translate([0,0,-1]) cylinder(r=hub_bore_R,h=12);
  arc_word("SPOOL",135,45,false);
  arc_word("PARADOX",225,315,true);
  // Small symmetry dots at lateral ends of hub ring
  for(a=[0,180]) rotate([0,0,a]) translate([33,0,-0.1]) cylinder(r=1.4,h=1.0);
 }
}

module drum(){
 difference(){
  union(){
   wheel();
   translate([0,0,wheel_thickness]) cylinder(r=hub_R,h=barrel_top-wheel_thickness);
  }
  translate([0,0,-1]) cylinder(r=hub_bore_R,h=barrel_top+3);
 }
}

// A support-free 6mm vertical anchor post inside a recessed pocket. Knot or
// hitch the string around the post; everything stays below drum OD.
module keyed_spigot(){
 // Joint male: solid annular insert; keyed along the +X direction.
 difference(){
  union(){
   translate([0,0,barrel_top]) cylinder(r=spigot_R,h=spigot_h);
   // 5mm wide index tab. Reaches 2.5mm beyond the cylindrical insert.
   translate([27.1,-3.0,barrel_top]) cube([4.4,6.0,spigot_h]);
  }
  translate([0,0,barrel_top-0.1]) cylinder(r=hub_bore_R,h=spigot_h+0.2);
  // Pilot bore for M4 screws; 3.2mm FDM hole. Tap or use thread-forming screw.
  for(a=screw_angles) rotate([0,0,a])
   translate([29.6,0,screw_z_male]) rotate([0,90,0])
    cylinder(d=3.2,h=20,center=true);
 }
}

module male(){
 difference(){
  union(){
   drum();
   keyed_spigot();
  }
  // String pocket: 22mm around circumference by 20mm tall, 10mm radial depth.
  rotate([0,0,90]) translate([29,-11,30.5]) cube([17,22,20]);
 }
 // Rebuild vertical bridge, with ends penetrating pocket floor/roof for strength.
 rotate([0,0,90]) translate([35,0,30.1]) cylinder(r=3.1,h=21);
}

module female(){
 difference(){
  drum();
  // Female register: bore grows at near-center end.
  translate([0,0,42.7]) cylinder(r=spigot_R+clearance,h=barrel_top-42.7+0.3);
  // Corresponding keyed registration slot. Extra 0.3mm each side.
  translate([26.6,-3.4,42.7]) cube([5.3,6.8,14]);
  // M4 screw clearance and inset button-head counterbores.
  for(a=screw_angles){
   rotate([0,0,a]){
    // Radial hole in outer shell from near axis to outside: r=2.25
    translate([35,0,screw_z_female]) rotate([0,90,0]) cylinder(d=4.5,h=15,center=true);
    // Outer seat radius >=36, 8mm diameter for button head.
    translate([40,0,screw_z_female]) rotate([0,90,0]) cylinder(d=8.4,h=8,center=true);
   }
  }
 }
}

module tire(){
 // Optional slip-on TPU tire; print 2x, flat on bed; 2.3% hoop stretch to fit.
 // Wheel's radius=90; tire relaxed inner radius=88.0, outer radius=92.5.
 // Front/back thickness 8mm fits 9mm rim without overlapping faces.
 difference(){cylinder(r=92.5,h=8);translate([0,0,-0.1]) cylinder(r=88.0,h=8.2);}
}

if(part=="male") male();
else if(part=="female") female();
else if(part=="tire") tire();
else if(part=="assembled"){
 color("royalblue") male();
 color("gold") translate([0,0,112]) rotate([180,0,0]) female();
}
