# The DAG-MCNP5 Test Suites #

## Introduction ##

The directories underneath this one contain groups of test problems 
for DAG-MCNP.  To run the tests in a subdirectory, enter the directory
and run the following commands:

    > ./waf configure
    > ./waf 

To see the results of a previously-run set of tests, run

    > ./waf summary

More details on the use of these test suites are given below.


## Subdirectories ##

 /Dagmc: Regression tests of unusual dagmc-specific geometries 

 /Meshtally: Regression tests of dag-mcnp mesh tallies (tetrahedral 
             track-length tallies and KDE tallies)

 /Regression: General MCNP5 regression tests adapted for dag-mcnp5.
              The 60-series numbered problems are dag-mcnp5 specific
              regression tests (and ought, perhaps, to move to the
              Dagmc suite)

Other MCNP5-derived subdirectories:
 /VALIDATION_CRITICALITY
 /VALIDATION_SHIELDING
 /VERIFICATION_KEFF

The all-caps directories contain longer-running problems,
and may take substantial computational resources to run to completion.


## Testing details ##

The test suites are run using the open-source [waf] tool, which is kept in its
entirety in the top-level Testing directory.  Each subdirectory contains a
symlink to this file.  `waf configure` is usually the first command issued in each
test suite.  `waf help` gives details on available options.  These options are
relevant to dag-mcnp users:

* waf -e [path] : Give the path to the dag-mcnp5 executable to use.  A default
                  path of ../../Source/src will be used if omitted.
* waf -f : Use pre-faceted geometry (instead of CAD files) when available.  
           This option usually saves time, and is compatible with nocgm
           versions of dag-mcnp.
* waf -c [cases] : Specify a test case to run.  In test suites where cases are 
                   numbered, such as the Regression suite, a hyphen-separated
                   group of numbers may be given, e.g. 1-10 to run cases 01 to
                   10.
* waf -j [jobs] : Specify the number of parallel jobs to run during testing.  
* waf --mpi : Use mpiexec to run dag-mcnp5 in parallel.  This changes the meaning
              of the -j option, which will specify the number of mpi tasks.  Be
              sure to use an mpi-enabled executable with this option.  (If -e
              is not specified, the default path will be searched for
              mcnp5.mpi)


## Creating new tests ##

Tests are specified for each test suite using the associated wscript file.  In
most cases, users can add new test cases by extending the existing wscript
files.  If a new test suite is to be created, it is usually most convenient to
copy one of the existing wscripts and edit it.

Each wscript file should include the contents of dagmcetsting.py, 
and implement these two functions:

* setup_testcases(): Sets self.allcases as a list of valid case names for this
                     test suite.  Also sets self.env.XSDIR for test suites with
                     custom cross section inputs (see Regression/wscript for
                     example)
                     
* get_case_definition(): Should return, for any member of self.allcases, 
                         a valid DagmcTestContext.CaseDefn object.  The
                         CaseDefn expects six members:
    * self.name : The name of the test; should be the same as the name given 
                  in setup_testcases
    * self.runname: The runtime name of the test.  This name is set on the 
                    dag-mcnp command line with the n=<runname> syntax.
    * self.flags: A list of strings to pass as options to dag-mcnp5.  E.g. 'fatal' 
                  to tolerate fatal errors.  Input files should not be placed
                  in the flags.
    * self.inputs: A dictionary of input files for dag-mcnp5.  The dictionary 
                   keys are the input specifiers for mcnp's command line, and
                   the values are the file paths for each input file.  Inputs
                   will be symlinked to the results directory before dag-mcnp
                   runs.  Dag-mcnp will be invoked with `key=value' for each
                   entry in this dictionary.
                       * Exception: if the dictionary key starts with 'EXTRA', 
                         the input file will be symlinked but will not be
                         passed on the dag-mcnp command line.  This is used to
                         specify inputs for tetrahedral mesh tallies.

                   example: case.inputs['inp'] = 'my_test_problem/dag.inp'

    * self.outputs: A dictionary of expected output files from dag-mcnp5.  The 
                    keys of the dictionary are the runname suffixes of the
                    output files (e.g. 'o' for outp files), and the values of
                    the dictionary are the paths to the reference files against
                    which the dag-mcnp5 outputs should be compared.

                    example: case.outputs['o'] = 'my_test_problem/reference_outp'

    * self.subcases: A list of sub-cases that must be run to generate output 
                     files that are to be used as input files for this test.
                     Each value is a 3-tuple (A,B,C), where
                     
                     * A = a CaseDefn object describing how to run the subcase.
                     * B = the runtime name of the subcase.
                     * C = the output files from the subcase that should be 
                           used as inputs to this test case.
                     
                     See the Regression/wscript for examples of the use of
                     self.subcases; other test suites do not currently use this
                     feature.


## Test suite history ##

The Dagmc test suite's full history can be found in the logs of DAG-MCNP;
the old trunk/Test-dagmc directory was removed in r357.

The Regression and V&V suites are derived from MCNP5 and were created by
Patrick Snouffer as part of his 2011 Master's thesis.  His original
files (including the old Makefile-based testing harness) can be found
at /filespace/groups/cnerg/archive/dag_vv.

[waf]: https://code.google.com/p/waf
