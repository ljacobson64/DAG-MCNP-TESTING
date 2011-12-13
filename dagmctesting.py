
from waflib.Configure import conf
from waflib import Logs
import os.path

def options(opt):
    opt.add_option('-e', '--exe', action='store', default='', dest='dagexe',
                   help = 'Path to DAG-MCNP executable to test' )
    opt.add_option('-c', '--cases', action='append', default=None, dest='cases',
                   help = 'Test cases to run' )
    opt.add_option('-f', '--facet', action='store_true', default=False, dest='facet_inputs',
                   help = 'Use faceted input geometries instead of CAD geometries' )
    opt.add_option('--mpi', action='store_true', default=False, dest='use_mpi',
                   help = 'Run MPI-based dagmc.  -j argument is used for number of tasks.' )

@conf
def detect_mcnp(ctx):
    ctx.start_msg('Checking for DAG-MCNP')
    if ctx.options.dagexe:
        ctx.env.DAGEXE = ctx.options.dagexe
    else:
        if ctx.options.use_mpi:
            ctx.find_program('mcnp5.mpi', path_list='../../Source/src', var='DAGEXE' )
        else:
            ctx.find_program('mcnp5', path_list='../../Source/src/', var='DAGEXE')
    ctx.env.DAGEXE = os.path.abspath( ctx.env.DAGEXE )
    ctx.end_msg(ctx.env.DAGEXE)

def configure(ctx):
    ctx.detect_mcnp()
    if ctx.options.use_mpi:
        ctx.env.MPI_JOBS= ctx.options.jobs
        ctx.options.jobs = 1
    
from waflib.Build import BuildContext

class DagmcTestContext(BuildContext):

    cmd = 'test'
    fun = 'test'
    
    class CaseDefn:
        def __init__(self):
            self.flags = list()
            self.inputs = dict()
            self.outputs = dict()
            self.subcases = list()

    def range_expand( self, lst ):
        # Helper function for expanding numeric ranges in the -c command line option
        for case in lst:
            # Test for NN-MM format
            chunks = case.split('-')
            if len(chunks) == 2 and all( c.isdigit() for c in chunks ):
                for i in xrange( int( chunks[0]), int(chunks[1])+1  ):
                    yield '{0:02d}'.format( i )
            elif case.isdigit() and int(case) in self.intcases:
                yield '{0:02d}'.format( int(case) ) 
            else:
                yield case

    def setup_requested_options( self ):
        # Turn self.options.cases (a list of strings, or None) into self.cases
        # Note that this may be called twice, so return immediately if self.cases already exists
        if hasattr(self, 'cases'): return

        if self.options.use_mpi:
            self.mpi_jobs = self.options.jobs
            self.options.jobs = 1

        self.setup_testcases()
        
        opt_cases = self.options.cases
        if opt_cases is None or opt_cases == ['all']:
            self.cases = self.allcases  
        else:
            self.cases = []
            for c in self.range_expand( self.options.cases ):
                if c in self.allcases:
                    self.cases.append( c )
                elif c.isdigit() and int(c) in self.intcases:
                    self.cases.append( '{0:02d}'.format(int(c)) )    
                else:
                    Logs.pprint( 'YELLOW', "Unknown case: " + c )

    def mcnp_case_setup( self, case, *k, **kw ):
        indir = kw.get('indir', case.name)
        kw['name']  = 'setup ' + case.name
        kw['target'] = []
        kw['rule']  = 'mkdir -p {0}; cd {0};'.format(indir)
        for key, link in case.inputs.iteritems():
            if link == os.path.basename(link): continue # do not link to preexisting file   
            kw['rule'] += '\n ln -fs ../../{0};'.format( link )
            kw['target'].append( os.path.join(indir, os.path.basename(link)) )
        
        kw['source'] = ['wscript']
         
        return self(*k, **kw)

    def runmcnp( self, case, *k, **kw ):

        indir = kw.get('indir', case.name)

        extra_src = None
        for subcase_params in case.subcases:
            subcase, subname, subouts = subcase_params
            self.mcnp_case_setup(subcase, indir=indir )
            extra_src = [os.path.join(indir,s) for s in subouts]
            self.runmcnp(subcase, indir=indir, mcnpname=subname, target=extra_src )
            #self.sources.extend( extra_src )

        args = case.inputs
        # This command runs after mcnp_case_setup, meaning the args have already been symlinked to ./
        for a,i in args.iteritems():
            args[a] = os.path.basename(i)

        args['n'] = kw.get('mcnpname', case.runname) 

        if hasattr( self.env, 'XSDIR' ) and len(self.env.XSDIR) > 0:
            args['xsdir'] = self.env.XSDIR

        if 'ftol' in kw:
            args['ftol'] = kw['ftol']

        argstring = ' '.join ( ['{0}={1}'.format(a,b) for (a,b) in args.iteritems() if not a.startswith('EXTRA') ] )

        screen_out = 'screen_out'
        redirstring = ' &> {0}'.format(screen_out)
        flagstr = ' '.join( case.flags )

        mpistr = ''
        if( self.options.use_mpi ):
            mpistr = 'mpiexec -np {0}'.format( self.env.MPI_JOBS )
            print mpistr

        kw['rule'] = 'cd {0};'.format(indir) + \
                     'rm -f meshta? {0}? {0}*.vtk;'.format(args['n']) +\
                     ' '.join( [mpistr, '${DAGEXE}', flagstr, argstring, redirstring] )

        kw['name'] = 'run dag-mcnp ' + case.name
        kw['source'] = ['wscript'] + [os.path.join(indir,x) for x in (args['inp'],args['gcad'])]
        if extra_src is not None: kw['source'].extend( extra_src )
        outputs = case.outputs

        target = []
        if 'target' in kw: target = kw['target']
        kw['target'] = target + [ indir+'/'+args['n'] + suffix for suffix in outputs.iterkeys() ]

        return self( *k, **kw )

    def diffmcnp( self, case, *k, **kw ):
        
        indir = kw.get( 'indir', case.name )

        for key, val in case.outputs.iteritems():
            ref = self.path.find_node(val).bldpath()
            check = os.path.join(indir,case.runname+key)

            # First part of the diff rule
            if not key.endswith('.vtk'):
                diff_rule = "diff -bw {0} {1}".format( ref, check )
            else:
                # For diffing vtk files, elide the second line of each file
                # (The second line is a version specifier that changes with each new MOAB revision)
                # Note that this opens a single quote, so needs to be closed below
                diff_rule = "bash -c 'diff <(sed -e 2d {0}) <(sed -e 2d {1})".format( ref,check )
            
            # diff returns 1 if files differ, but we don't want waf to halt in such a case
            # Make waf only halt if diff returns 2, indicating an actual error (like a missing file)
            diff_rule += " > ${TGT}; if [ $? == 2 ] \n then \n exit 1 \n fi"

            if key.endswith('.vtk'):
                diff_rule += "'"
            
            # create the rule
            self( rule = diff_rule, 
                  source = [ref, check], target = [os.path.join(indir,'dif{0}'.format(key)) ],
                  name = 'dif'+key+' '+case.name )
                  
        return self( *k, **kw)


class SummaryContext( DagmcTestContext ):
    cmd = 'summary'
    fun = 'summary'

def summary( bld ):
    
    bld.setup_requested_options()

    okay = True
    outputs = {}
    for c in bld.cases:
        o = bld.get_case_definition(c).outputs
        outputs.update( o )

    #outputs understood by this function, in the order we want them printed
    summary_outputs = ['o','m','e'] 
    #filter by the outputs that actually exist for the requested cases
    summary_outputs = filter( lambda x:x in outputs.keys(), summary_outputs ) 

    mesh_tallies = False
    if any( [x.endswith('.vtk') for x in outputs.keys() ] ):
        mesh_tallies = True

    Logs.pprint( 'CYAN', 'case', sep = '  ')
    for o in summary_outputs[:]:
        Logs.pprint( 'CYAN', ' dif{0} (bytes)'.format(o), sep='    ')
    if mesh_tallies:
        Logs.pprint( 'CYAN', 'Mesh tallies' )
    Logs.pprint( 'CYAN', '' ) # newline
    
    for case in map(bld.get_case_definition, bld.cases): 
        Logs.pprint( 'CYAN', case.name, sep = ' ' )
        for suffix in summary_outputs:
            filepath = '{0}/{1}/dif{2}'.format( bld.out_dir, case.name, suffix )
            diff = None
            if os.path.exists(filepath):
                size = os.path.getsize( filepath )
                diff = int(size)

            if diff is None: 
                if suffix in case.outputs.keys():
                    Logs.pprint( 'YELLOW', '{0:>16s}'.format('missing'), sep = ' ' )
                    okay = False
                else:
                    Logs.pprint( 'GREEN', '{0:>16s}'.format('-'), sep = ' ' )
            elif diff == 0:
                Logs.pprint( 'GREEN', '{0:>16d}'.format(0), sep = ' ')
            else:
                Logs.pprint( 'RED', '{0:>16d}'.format(diff), sep = ' ')
                okay = False
        if mesh_tallies:
            keys = [k for k in outputs.keys() if k.endswith('.vtk') ]
            if len(keys) == 0 : Logs.pprint( 'GREEN', '-' )
            else:
                Logs.pprint( 'GREEN', '[', sep = '' )
                for key in keys:
                    num = key[-6:-4]
                    Logs.pprint( 'CYAN', 'dif'+num+' =', sep = '' )
                    size = os.path.getsize( '{0}/{1}/dif{2}'.format( bld.out_dir, case.name, key ) )
                    if size == 0: Logs.pprint( 'GREEN', '0', sep = '' )
                    else: Logs.pprint( 'RED', size, sep = '' )
                Logs.pprint( 'GREEN', ']' )
                

        Logs.pprint( 'GREEN', '' ) # Print newline to log

    if okay: Logs.pprint('GREEN', 'All test passed.' )
    else:    Logs.pprint('CYAN', 'Some tests failed.')



def test(bld):

    bld.setup_requested_options()

    for c in bld.cases: 
        case = bld.get_case_definition(c)
        bld.mcnp_case_setup( case, geomtype = 'h5m' )
        bld.runmcnp( case, ftol=1e-4, geomtype='h5m' )
        bld.diffmcnp( case ) 
        
    bld.add_post_fun( summary  )
    bld.install_path = None # Disable the waf 'install' step 


def build(bld):
    # This it the default entry point when users invoke waf without specific options.
    # By default, run test.
    import Options
    lst = ['configure','test']
    Options.commands = lst + Options.commands


