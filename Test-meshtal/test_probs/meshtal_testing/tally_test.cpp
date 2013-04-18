#include <mcnp_funcs.h>
#include <cstring>

extern "C"{
  void __fmesh_mod_MOD_dagmc_mesh_score( int* /*i*/, double* /*erg*/, double* /*wgt*/, 
					 double* d, double *score )
  {
    *score = *d;
  }
}

char* comment = "dagmc";

int main(){

  dagmc_fmesh_initialize_();

  

  int ipt = 1;
  double x, y, z, u, v, w, erg, wgt, d;
  
  x = y = z = 0;
  y = -4;
  u = 1;
  v = 0;
  w = 0;
  erg = wgt = 1;
  d = 100;
  int idx = 0, id = 4;
  int comment_len = strlen(comment);

  dagmc_fmesh_setup_mesh_( &ipt, &id, &idx, comment, &comment_len );


  dagmc_fmesh_score_(&ipt, &x, &y, &z, &u, &v, &w, &erg, &wgt, &d, &idx );
  dagmc_fmesh_end_history_();

  u = 0; v = -1; d = 100;
  dagmc_fmesh_score_(&ipt, &x, &y, &z, &u, &v, &w, &erg, &wgt, &d, &idx );
  dagmc_fmesh_end_history_();

  v = 0; w = 1; d = 200;
  dagmc_fmesh_score_(&ipt, &x, &y, &z, &u, &v, &w, &erg, &wgt, &d, &idx );
  dagmc_fmesh_end_history_();


  dagmc_fmesh_print_(&idx, &x, &y);

  return 0;
}

  /** MESH TALLY FUNCTIONALITY BELOW THIS LINE */
  //void dagmc_fmesh_initialize_();
  //void dagmc_fmesh_end_history_();
  //void dagmc_fmesh_score_(int *ipt, double *x, double *y, double *z,
  //double *u, double *v, double *w, double *erg,double *wgt,double *d, int *idx);
  //void dagmc_fmesh_print_();
