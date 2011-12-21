// KDETrackTest.cpp

#include <ctime>
#include <iostream>
 
#include "moab/CartVect.hpp"

#include "../../Source/dagmc/KDETrack.hpp"
#include "../../Source/dagmc/KDEKernel.hpp"

using namespace std;

const double PI = 3.14159265359;

// precision for testing the equality of doubles
const double EPSILON = 1e-10;

// checks that the value of a double x equals v
inline bool DOUBLE_EQUAL( double x, double v ) {

  return ( ((v - EPSILON) < x) && (x < ( v + EPSILON )) );

}

// tests functionality of KDETrack::change_bandwidth
bool TestChangeBandwidth() {

  // make default test KDETrack object
  KDEKernel kernel;
  KDETrack track( &kernel );

  // change the bandwidth
  moab::CartVect newBandwidth( 0.1, 0.2, 0.3 );
  track.change_bandwidth( newBandwidth );
  
  // test new bandwidth was set correctly
  moab::CartVect bandwidth = track.get_bandwidth();
  
  for ( int i = 0 ; i < 3 ; ++i ) {

    if ( !DOUBLE_EQUAL( bandwidth[i], newBandwidth[i] ) )
      return false;

  }

  return true;

}

// tests functionality of KDETrack::change_track_segment
bool TestChangeTrackSegment() {

  // make default test KDETrack object
  KDEKernel kernel;
  KDETrack track( &kernel );

  // change the track segment
  moab::CartVect newStartPoint( -1, 0, 1 );
  moab::CartVect newDirection( 0, 0.7071, -0.7071 );
  double newLength = 2.5;
  track.change_track_segment( newStartPoint, newDirection, newLength );

  // test new track segment was set correctly
  moab::CartVect start_point = track.get_start_point();
  moab::CartVect direction = track.get_direction();
  double length = track.get_length();

  if ( !DOUBLE_EQUAL( length, newLength ) )
    return false;
 
  for ( int i = 0 ; i < 3 ; ++i ) {

    if ( !DOUBLE_EQUAL( start_point[i], newStartPoint[i] ) )
      return false;

    if ( !DOUBLE_EQUAL( direction[i], newDirection[i] ) )
      return false;

  }
  
  return true;

}

// tests functionality of KDETrack::point_within_max_radius
bool TestPointWithinMaxRadius() {

  // make default test KDETrack object along the x-axis
  KDEKernel kernel;
  KDETrack track( &kernel );

  // get neighborhood that was set in the constructor
  double box_min[3];
  double box_max[3];
  double r_max = 0;
  track.get_neighborhood( box_min, box_max, r_max );
  
  // create test #1 point objects
  moab::CartVect outside_radius1( 0.7, -0.02, 2 * r_max );
  moab::CartVect on_boundary1( -0.1, r_max * cos(PI/4), r_max * sin(PI/4) );
  moab::CartVect on_line1( 0, 0, 0 );  // catches zero vector errors
  moab::CartVect inside_radius1( 1.05, 0.09, -0.04 );
  
  // test points that should not be within the max radius
  if ( track.point_within_max_radius( outside_radius1 ) )
    return false;

  if ( track.point_within_max_radius( on_boundary1 ) )
    return false;

  // test points that should be within the max radius
  if ( !track.point_within_max_radius( on_line1 ) )
    return false;

  if ( !track.point_within_max_radius( inside_radius1 ) )
    return false;

  // change track segment to a 3D test case
  moab::CartVect newStartPoint( -0.1, 0.1, -0.3 );
  moab::CartVect newDirection( -0.5, -0.3, sqrt(0.66) );
  double newLength = 2.5;
  track.change_track_segment( newStartPoint, newDirection, newLength );

  // create test #2 point objects
  moab::CartVect outside_radius2( -0.7, 2 * r_max, 0.67488 );
  moab::CartVect on_boundary2( -0.1 + 0.514495755428 * r_max,
                                0.1 - 0.857492925713 * r_max, -0.3 );
  moab::CartVect on_line2( -1.35, -0.65, 1.73100960116 );
  moab::CartVect inside_radius2( -0.65, -0.1, 0.59 );

  // test points that should not be within the max radius
  if ( track.point_within_max_radius( outside_radius2 ) )
    return false;

  if ( track.point_within_max_radius( on_boundary2 ) )
    return false;

  // test points that should be within the max radius
  if ( !track.point_within_max_radius( on_line2 ) )
    return false;

  if ( !track.point_within_max_radius( inside_radius2 ) )
    return false;

  return true;
  
}

// tests functionality of KDETrack::compute_contribution( CartVect )
// - first 13 cases assume [Smin,Smax] exists such that Smin != Smax
// - next 5 cases have no valid [Smin,Smax] range
bool TestComputeContribution1() {

  // test case 1: S1
  moab::CartVect start_point( 0, 0, 0 );
  moab::CartVect direction( 1/sqrt(3), 1/sqrt(3), 1/sqrt(3) );
  moab::CartVect bandwidth( 0.1, 0.1, 0.1 );
  double length = 1.0;
  KDEKernel kernel;
  KDETrack track( start_point, direction, bandwidth, length, &kernel );
  
  moab::CartVect calc_point( -0.215, -0.157, -0.1 );
  double contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 0 ) )
    return false;

  // test case 2: S2
  direction = moab::CartVect( 0.1, -sqrt(0.18), 0.9 );
  length = 0.123;
  track.change_track_segment( start_point, direction, length );
    
  calc_point = moab::CartVect( 0.06, 0.1, -0.08 );
  contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 0 ) )
    return false;

  // test case 3: S3
  direction = moab::CartVect( 0.9, -sqrt(0.18), 0.1 );
  length = 0.2;
  track.change_track_segment( start_point, direction, length );
  
  calc_point = moab::CartVect( 0.01, -0.015147186258, 0.085 );
  contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 12.4458166609 ) )
    return false;

  // test case 4: S4
  start_point = moab::CartVect( 1, 2.15, -1.45 );
  direction = moab::CartVect( 1, 0, 0 );
  length = 1.0;
  track.change_track_segment( start_point, direction, length );

  calc_point = moab::CartVect( 1, 2.2, -1.5 );
  contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 15.8203125 ) )
    return false;

  // test case 5: S5
  start_point = moab::CartVect( 0.14, 0, -0.28787753827 );
  direction = moab::CartVect( -0.2, 0, sqrt(0.96) );
  track.change_track_segment( start_point, direction, length );

  bandwidth = moab::CartVect( 0.1, 0.2, 0.3 );
  track.change_bandwidth( bandwidth );

  calc_point = moab::CartVect( 0, 0, 0 );
  contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 10.3007343539 ) )
    return false;

  // test case 6: S6
  start_point = moab::CartVect( 0, 0, 0 );
  direction = moab::CartVect( 0, sqrt(0.5), -sqrt(0.5) );
  track.change_track_segment( start_point, direction, length );
  
  bandwidth = moab::CartVect( 0.1, 0.1, 0.1 );
  track.change_bandwidth( bandwidth );

  calc_point = moab::CartVect( 0, 0.67781745931, -0.67781745931 );
  contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 48.3207689701 ) )
    return false;

  // test case 7: S7
  start_point = moab::CartVect( -0.2, -0.4, -0.1 );
  direction = moab::CartVect( -0.7, 0.2, -sqrt(0.47) );
  track.change_track_segment( start_point, direction, length );
  
  calc_point = moab::CartVect( -0.93, -0.14, -0.817008914036 );
  contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 8.4449424274 ) )
    return false;

  // test case 8: S8
  start_point = moab::CartVect( -0.5, 0.5, -0.5 );
  direction = moab::CartVect( 0.5, 0.1, sqrt(0.74) );
  length = 0.5;
  track.change_track_segment( start_point, direction, length );
  
  bandwidth = moab::CartVect( 0.5, 0.5, 0.5 );
  track.change_bandwidth( bandwidth );

  calc_point = moab::CartVect( -0.5, 1.05, 0.344093010682 );
  contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 0 ) )
    return false;

  // test case 9: S9
  start_point = moab::CartVect( -1, -2, -3 );
  direction = moab::CartVect( -0.5, 0.5, sqrt(0.5) );
  length = 0.725;
  track.change_track_segment( start_point, direction, length );

  bandwidth = moab::CartVect( 0.1, 0.1, 0.1 );
  track.change_bandwidth( bandwidth );

  calc_point = moab::CartVect( -1.85, -1.2, -1.83933982822 );
  contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 0 ) )
    return false;

  // test case 10: S10
  start_point = moab::CartVect( 0.5, 0.4, 0.2 );
  direction = moab::CartVect( 0, 0, -1 );
  length = 1.0;
  track.change_track_segment( start_point, direction, length );

  bandwidth = moab::CartVect( 0.2, 0.4, 0.5 );
  track.change_bandwidth( bandwidth );

  calc_point = moab::CartVect( 0.6, 0.33, -0.3 );
  contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 5.1119384766 ) )
    return false;

  // test case 11: S11
  start_point = moab::CartVect( -1, -1, -1 );
  direction = moab::CartVect( 0.8, sqrt(0.2), 0.4 );
  track.change_track_segment( start_point, direction, length );

  bandwidth = moab::CartVect( 1, 1, 1 );
  track.change_bandwidth( bandwidth );

  calc_point = moab::CartVect( -0.4, -0.2683281573, -0.4 );
  contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 0.2409484342 ) )
    return false;

  // test case 12: S12
  start_point = moab::CartVect( 0, 0, 0 );
  direction = moab::CartVect( -sqrt(0.5) , 0.5, 0.5 );
  track.change_track_segment( start_point, direction, length );
  
  calc_point = moab::CartVect( -0.292893218813, -0.5, 0.5 );
  contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 0.1500140139 ) )
    return false;

  // test case 13: S13
  direction = moab::CartVect( -sqrt(0.63), -0.1, -0.6 );
  length = 1.3;
  track.change_track_segment( start_point, direction, length );

  calc_point = moab::CartVect( -1, 0, -1 );
  contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 0.2573922718 ) )
    return false;

  // test case 14: SA
  start_point = moab::CartVect( 0, 0, 0 );
  direction = moab::CartVect( 0.5, sqrt(0.5), 0.5 );
  length = 1.0;
  track.change_track_segment( start_point, direction, length );

  bandwidth = moab::CartVect( 0.1, 0.1, 0.1 );
  track.change_bandwidth( bandwidth );

  calc_point = moab::CartVect( 0.1, 0.453553390593, -0.15 );
  contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 0 ) )
    return false;

  // test case 15: SB
  calc_point = moab::CartVect( 0, 0.1, 0.3 );
  contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 0 ) )
    return false;

  // test case 16: SC
  calc_point = moab::CartVect( 0, 0.1, 0.225 );
  contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 0 ) )
    return false;

  // test case 17: SD
  calc_point = moab::CartVect( 0.1, -0.1, 0.1 );
  contribution = track.compute_contribution( calc_point );
 
  if ( !DOUBLE_EQUAL( contribution, 0 ) )
    return false;

  // test case 18: SE
  calc_point = moab::CartVect( 0, 0.241421356237, -0.2 );
  contribution = track.compute_contribution( calc_point );

  if ( !DOUBLE_EQUAL( contribution, 0 ) )
    return false;

  return true;

}

// tests functionality of KDETrack::compute_contribution( double[3] )
// - make sure it calls compute_contribution( CartVect ) correctly
bool TestComputeContribution2() {

  // test case 1: S1
  moab::CartVect start_point( 0, 0, 0 );
  moab::CartVect direction( 1/sqrt(3), 1/sqrt(3), 1/sqrt(3) );
  moab::CartVect bandwidth( 0.1, 0.1, 0.1 );
  double length = 1.0;
  KDEKernel kernel;
  KDETrack track( start_point, direction, bandwidth, length, &kernel );
 
  double calc_point1[] = { -0.215, -0.157, -0.1 };
  double contribution = track.compute_contribution( calc_point1 );

  if ( !DOUBLE_EQUAL( contribution, 0 ) )
    return false;

  // test case 5: S5
  start_point = moab::CartVect( 0.14, 0, -0.28787753827 );
  direction = moab::CartVect( -0.2, 0, sqrt(0.96) );
  track.change_track_segment( start_point, direction, length );
  
  bandwidth = moab::CartVect( 0.1, 0.2, 0.3 );
  track.change_bandwidth( bandwidth );

  double calc_point2[] = { 0, 0, 0 };
  contribution = track.compute_contribution( calc_point2 );
  
  if ( !DOUBLE_EQUAL( contribution, 10.3007343539 ) )
    return false;
  
  return true;

}

// tests functionality of KDETrack::set_neighborhood
bool TestSetNeighborhood() {

  // make test KDETrack object
  moab::CartVect start_point( -1, 0, 1 );
  moab::CartVect direction( 0, 0.7071, -0.7071 );
  moab::CartVect bandwidth( 0.1, 0.1, 0.1 );
  double length = 1.0;
  KDEKernel kernel;
  KDETrack track( start_point, direction, bandwidth, length, &kernel );

  // get neighborhood that was set in the constructor
  double box_min[3];
  double box_max[3];
  double max_radius = 0;
  track.get_neighborhood( box_min, box_max, max_radius );
  
  // expected values {min,max}
  double x[2] = { -1.1, -0.9 };
  double y[2] = { -0.1, 0.8071 };
  double z[2] = { 0.1929, 1.1 };

  // test actual results against expected values
  if ( !DOUBLE_EQUAL(box_min[0],x[0]) || !DOUBLE_EQUAL(box_max[0],x[1]) )
    return false;    

  if ( !DOUBLE_EQUAL(box_min[1],y[0]) || !DOUBLE_EQUAL(box_max[1],y[1]) )
    return false; 
  
  if ( !DOUBLE_EQUAL(box_min[2],z[0]) || !DOUBLE_EQUAL(box_max[2],z[1]) )
    return false;

  if ( !DOUBLE_EQUAL( max_radius, sqrt(0.03) ) )
    return false;
  
  return true;

}

// test the effectiveness of point_within_max_radius
void TestPointSpeed() {

  // make test KDETrack object
  moab::CartVect start_point( 0, 0, 0 );
  moab::CartVect direction( 0.2, sqrt(0.96), 0 );
  moab::CartVect bandwidth( 0.1, 0.1, 0.1 );
  double length = 1.0;
  KDEKernel kernel;
  KDETrack track( start_point, direction, bandwidth, length, &kernel );

  // create test calculation points
  moab::CartVect case1( 0.28, 0, 0 );         // outside radius
  moab::CartVect case2( 0.21, 0.35, 0 );      // inside radius, not neighborhood
  moab::CartVect case3( 0.13, 0.45, -0.01 );  // inside neighborhood

  // set timing variables
  clock_t start, end;
  double total_time = 0;
  int num_times = 1e8;

  // test speed for case1
  cout << endl << "  testing case #1 = " << case1 << endl;
  start = clock();

  for ( int i = 0 ; i < num_times ; ++i )
      track.compute_contribution( case1 );  

  end = clock();
  total_time = ( (double) ( end - start ) ) / CLOCKS_PER_SEC;
  cout << "    without point_within_max_radius - " << total_time << endl;
 
  start = clock();

  for ( int i = 0 ; i < num_times ; ++i ) {

    if ( track.point_within_max_radius( case1 ) )
      track.compute_contribution( case1 );
  
  }

  end = clock();
  total_time = ( (double) ( end - start ) ) / CLOCKS_PER_SEC;
  cout << "    with point_within_max_radius - " << total_time << endl;
     
  // speed test for case 2
  cout << endl << "  testing case #2 = " << case2 << endl;
  start = clock();

  for ( int i = 0 ; i < num_times ; ++i )
      track.compute_contribution( case2 );  

  end = clock();
  total_time = ( (double) ( end - start ) ) / CLOCKS_PER_SEC;
  cout << "    without point_within_max_radius - " << total_time << endl;
 
  start = clock();

  for ( int i = 0 ; i < num_times ; ++i ) {

    if ( track.point_within_max_radius( case2 ) )
      track.compute_contribution( case2 );
     
  }

  end = clock();
  total_time = ( (double) ( end - start ) ) / CLOCKS_PER_SEC;
  cout << "    with point_within_max_radius - " << total_time << endl;

  // speed test for case 3
  cout << endl << "  testing case #3 = " << case3 << endl;
  start = clock();

  for ( int i = 0 ; i < num_times ; ++i )
      track.compute_contribution( case3 );  

  end = clock();
  total_time = ( (double) ( end - start ) ) / CLOCKS_PER_SEC;
  cout << "    without point_within_max_radius - " << total_time << endl;
 
  start = clock();

  for ( int i = 0 ; i < num_times ; ++i ) {
   
    if ( track.point_within_max_radius( case3 ) )
      track.compute_contribution( case3 );
  
  }

  end = clock();
  total_time = ( (double) ( end - start ) ) / CLOCKS_PER_SEC;
  cout << "    with point_within_max_radius - " << total_time << endl;

  
}

int main() {

  // logic tests
  cout << "Beginning logic tests.. " << endl;

  int numTests = 6;

  if ( TestSetNeighborhood() )
    --numTests;
  else
    cout << "  set_neighborhood test failed" << endl;

  if ( TestChangeBandwidth() )
    --numTests;
  else
    cout << "  change_bandwidth test failed" << endl;

  if ( TestChangeTrackSegment() )
    --numTests;
  else
    cout << "  change_track_segment test failed" << endl;
  
  if ( TestPointWithinMaxRadius() )
    --numTests;
  else
    cout << "  point_within_max_radius test failed" << endl;

  if ( TestComputeContribution1() )
    --numTests;
  else
    cout << "  compute_contribution( CartVect ) test failed" << endl;

  if ( TestComputeContribution2() )
    --numTests;
  else
    cout  << "  compute_contribution( double[3] ) test failed" << endl;

  if ( numTests == 0 )
    cout << "  all logic tests passed" << endl;

  // speed tests
  cout << endl << "Beginning speed tests.. " << endl;
 
  TestPointSpeed();
  
  return 0;
  
}
