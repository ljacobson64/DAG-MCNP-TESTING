
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
    opt.add_option('-l', action='store_true', default=False, dest='early_diffs',
                   help = 'Print output diff counts as early as possible' )

@conf
def detect_mcnp(ctx):
    ctx.start_msg('Checking for DAG-MCNP')
    if ctx.options.dagexe:
        ctx.env.DAGEXE = ctx.options.dagexe
        if not os.path.exists(ctx.env.DAGEXE):
            raise ctx.errors.ConfigurationError('Specified path {0} does not exist'.format(ctx.env.DAGEXE))
    else:
        try:
            progname = 'mcnp5'
            if ctx.options.use_mpi:
                progname = 'mcnp5.mpi'
            ctx.find_program(progname, path_list='../../../Source/src', var='DAGEXE' )
        except ctx.errors.ConfigurationError as e:
            print e
            raise ctx.errors.ConfigurationError("Use -e to specify path to "+progname)
    ctx.env.DAGEXE = os.path.abspath( ctx.env.DAGEXE )
    ctx.end_msg(ctx.env.DAGEXE)

def configure(ctx):
    ctx.detect_mcnp()
    if ctx.options.use_mpi:
        ctx.env.MPI_JOBS= ctx.options.jobs
        ctx.options.jobs = 1
    
from waflib.Build import BuildContext
from waflib import Task, Build

# To force the most appropriate ordering for mcnp tests, we will probably
# have to override this method, to return Task.ASK_LATER for tests that are
# otherwise ready to run but would be better waiting on an available diff-
# and-report-results rule
#old_run_stat = Task.Task.runnable_status
#def alt_runnable_status(self):
#    print self.name
#    return old_run_stat(self)
#Task.Task.runnable_status = alt_runnable_status

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

        if 'DAGEXE' not in self.env:
            self.fatal( 'Need a dag-mcnp5 executable' )

        extra_src = None
        for subcase_params in case.subcases:
            subcase, subname, subouts = subcase_params
            self.mcnp_case_setup(subcase, indir=indir )
            extra_src = [os.path.join(indir,s) for s in subouts]
            self.runmcnp(subcase, indir=indir, mcnpname=subname, target=extra_src )
            #self.sources.extend( extra_src )

        args = case.inputs
        # This command runs after mcnp_case_setup, meaning the args have already been symlinked to the cwd
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

        kw['rule'] = "bash -c 'cd {0};".format(indir) + \
                     'rm -f meshta? {0}? {0}*.vtk;'.format(args['n']) +\
                     ' '.join( [mpistr, '${DAGEXE}', flagstr, argstring, redirstring] ) + "'"

        kw['name'] = 'run dag-mcnp ' + case.name
        kw['source'] = ['wscript', os.path.join(indir,args['inp'])] 
        if 'gcad' in args: kw['source'].append( os.path.join(indir, args['gcad']) )
        if extra_src is not None: kw['source'].extend( extra_src )
        outputs = case.outputs

        target = []
        if 'target' in kw: target = kw['target']
        kw['target'] = target + [ indir+'/'+args['n'] + suffix for suffix in outputs.iterkeys() 
                                                                   if suffix != 'meshtal' ]

        if 'meshtal' in outputs.keys(): kw['target'] = kw['target'] + [os.path.join(indir,'meshtal')] 
        return self( *k, **kw )

    def diffmcnp( self, case, *k, **kw ):
        
        indir = kw.get( 'indir', case.name )
        target_files = []


        for key, val in case.outputs.iteritems():
            ref = self.path.find_node(val).bldpath()
            check = os.path.join(indir,case.runname+key)
            if key == 'meshtal':
                check = os.path.join(indir,key)

            # First part of the diff rule
            if not key.endswith('.vtk'):
                diff_rule = "bash -c 'diff -abw {0} {1}".format( ref, check )
            else:
                # For diffing vtk files, elide the second line of each file
                # (The second line is a version specifier that changes with each new MOAB revision)
                diff_rule = "bash -c 'diff <(sed -e 2d {0}) <(sed -e 2d {1})".format( ref,check )
            
            # diff returns 1 if files differ, but we don't want waf to halt in such a case
            # Make waf only halt if diff returns 2, indicating an actual error (like a missing file)
            diff_rule += " > ${TGT}; if [ $? == 2 ] \n then \n exit 1 \n fi'"

            target_files.append( os.path.join(indir, 'dif{0}'.format(key)) )

            # create the rule
            self( rule = diff_rule, 
                  source = [ref, check], target = [ target_files[-1] ],
                  name = 'dif'+key+' '+case.name )

        if( self.options.early_diffs ): 
            ctx = SummaryContext()
            ctx.options = self.options
            ctx.cases = [case.name]
            post = lambda x:summary( ctx )
            r = self( rule = post, source=target_files, name = "diff sizes, case "+case.name )

        return self( *k, **kw)


class SummaryContext( DagmcTestContext ):
    cmd = 'summary'
    fun = 'summary'

def summary( bld ):
    
    bld.setup_requested_options()

    # inner class to use as shared namespace with print_filesize subfunction defined below
    # if this was python3 we'd use the nonlocal keyword instead
    class N:pass
    v = N()
    v.okay = True

    maxlen = max( [len(x) for x in bld.cases] )

    column1 = '{0:<' + str(maxlen+2) + '}'
    columnN = '{0:>14}'

    outputs = {}
    for c in bld.cases:
        o = bld.get_case_definition(c).outputs
        outputs.update( o )

    #outputs understood by this function, in the order we want them printed
    summary_outputs = ['o','m','e'] 
    #filter by the outputs that actually exist for the requested cases
    summary_outputs = filter( lambda x:x in outputs.keys(), summary_outputs ) 

    meshtal_file = False
    if 'meshtal' in outputs.keys():
        meshtal_file = True

    mesh_tallies = False
    if any( [x.endswith('.vtk') for x in outputs.keys() ] ):
        mesh_tallies = True

    Logs.pprint( 'CYAN', column1.format('case'), sep = '')
    for o in summary_outputs[:]:
        Logs.pprint( 'CYAN', columnN.format('dif{0} (bytes)'.format(o)), sep='')
    if meshtal_file:
        Logs.pprint( 'CYAN', columnN.format('difmeshtal'), sep='' )
    if mesh_tallies:
        Logs.pprint( 'CYAN', columnN.format('Mesh tallies'), sep='' )
    Logs.pprint( 'CYAN', '' ) # newline

    def diff_file_path( suffix ):
        return '{0}/{1}/dif{2}'.format( bld.out_dir, case.name, suffix )

    def print_filesize( suffix, filepath, fmt=columnN ):
        diff = None
        if os.path.exists( filepath ):
            size = os.path.getsize( filepath )
            diff = int(size)
        if diff is None:
            if suffix in case.outputs.keys():
                Logs.pprint( 'YELLOW', fmt.format('missing'), sep = '' )
                v.okay = False
            else:
                Logs.pprint( 'GREEN', fmt.format('-'), sep = '' )
        elif diff == 0:
            Logs.pprint( 'GREEN', fmt.format(0), sep = '' )
        else:
            Logs.pprint( 'RED', fmt.format(diff), sep = '' )
            v.okay = False

    for case in map(bld.get_case_definition, bld.cases): 
        Logs.pprint( 'CYAN', column1.format(case.name), sep = '' )
        for suffix in summary_outputs:
            filepath = diff_file_path(suffix)
            print_filesize( suffix, filepath )

        if meshtal_file:
            print_filesize( 'meshtal', diff_file_path('meshtal') )

        if mesh_tallies:
            keys = [k for k in case.outputs.keys() if k.endswith('.vtk') ]
            if len(keys) == 0 : Logs.pprint( 'GREEN', '  -', sep = '' )
            else:
                Logs.pprint( 'GREEN', '  [', sep = '' )
                for key in sorted(keys):
                    num = ''.join( [x for x in list(key) if x.isdigit() ] )
                    Logs.pprint( 'CYAN', 'dif'+num+' =', sep = '' )
                    filepath = '{0}/{1}/dif{2}'.format( bld.out_dir, case.name, key ) 
                    print_filesize( key, filepath, '{0}' )
                Logs.pprint( 'GREEN', ']', sep='' )
                

        Logs.pprint( 'GREEN', '' ) # Print newline to log

    if len(bld.cases) == 1:
        if v.okay: Logs.pprint('GREEN', 'passes' )
        else:      Logs.pprint('CYAN',  'fails'  )
    else:
        if v.okay: Logs.pprint('GREEN', 'All test passed.' )
        else:      Logs.pprint('CYAN',  'Some tests failed.')



def test(bld):

    bld.setup_requested_options()

    for c in bld.cases: 
        case = bld.get_case_definition(c)
        bld.mcnp_case_setup( case )
        bld.runmcnp( case )
        bld.diffmcnp( case ) 
        
    bld.add_post_fun( summary  )
    bld.install_path = None # Disable the waf 'install' step 


def build(bld):
    # This it the default entry point when users invoke waf without specific options.
    # By default, run test.
    import Options
    lst = ['configure','test']
    Options.commands = lst + Options.commands


