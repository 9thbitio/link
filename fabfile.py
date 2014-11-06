"""
Fabfile for deploying and setting up code that looks like the production
environment.  it also makes it easy to start up the servers 

If you want to run on the localhost you may need to first do::

    rm -rf ~/.ssh/known_hosts

"""

from __future__ import with_statement
import os
import re
from fabric.api import local, settings, abort, run , cd, env, lcd, sudo, prompt
from fabric.contrib.console import confirm
from fabric.contrib import files

env.roledefs = {'local':['localhost']}

env.use_ssh_config=True

TAG_REGEX = re.compile('^[0-9]+\.[0-9]+\.[0-9]+')
STABLE_MSG = '**stable**'

LINK_CODE_DIR = os.path.split(os.path.abspath(__file__))[0]

def dir_code_base():
    """
    If you are using any localhost then it will use the current directory.
    Otherwise you will use the code_dir
    """
    if 'localhost' in env.host_string:
        return os.getcwd()

    return code_dir

def dir_scripts():
    """
    The directory where you house all the scripts
    """
    return '%s/scripts' % (dir_code_base())

config_dir = '~/.link' 

def test_install():
    import os
    #set the link dir to something silly
    os.environ['LNK_DIR']='saodusah'
    #create a virtual environment
    local('echo $LNK_DIR')
    local('virtualenv env')
    #remove everything from the build directory
    local('rm -rf build')
    #run this and see that it works
    local('source env/bin/activate && python setup.py install')

def configure():
    """
    Create the base configuration so that you can change it.  Might want to
    include the configuration in a different repo
    """
    if not files.exists(config_dir):
        run('mkdir %s' % config_dir)
    lnk_config = '%s/link.config' % config_dir
    if not files.exists(lnk_config):
        run('touch %s' % lnk_config)

def script(script_name, command = 'python', **args):
    """
    Will run the script that is in the scripts folder.  you can pass in a
    dictionory of args and it will pass it through to the script as command line
    args in this format

    fab -R local script:example.py,arg1=value1,arg2=value2
    
    that will result in running this command
    <command> <scripts_directory>/<scriptname> --arg1=value1 --arg2=value2
    """
    with cd(dir_scripts()):
        parameters = ''
        if args:
            parameters = ' '.join(['--%s=%s' % (key, value) for key,value in
                                   args.iteritems()])
        run("%s %s %s" % (command , script_name, parameters))

def commit(msg=None):
    """
    Commit your changes to git

    :msg: @todo
    :returns: @todo

    """
    print '---Commiting---'
    print
    
    msg =  msg or prompt('Commit message: ')
    commit = False

    commit = prompt('Confirm commit? [y/n]') == 'y'

    if commit:
        with settings(warn_only=True):
            _commit = not local('git commit -a -m "%s"'  % msg).failed
            if not _commit:
                #nothing was committed
                commit = False
                print "Nothing to commit"
    else:
        abort('commit aborted')
    print
    print '---Done---'
    return commit

def tag_names(number = 10, stable=False):
    number = int(number)
    print "fetching tags first"
    local('git fetch --tags ')
    print "Showing latest tags for reference"
    tags =  local('git tag -n1 ', capture = True)
    tags = [x for x in tags.split('\n') if TAG_REGEX.findall(x) and 
                        (not stable or STABLE_MSG in x)]
    
    tags.sort(reverse=True)
    #take the first <number> things in the list
    tags = tags[0:min(len(tags), number)]
    print '\n'.join(tags)
    print
    return tags

def check_tag_format(tag):
    """
    Checks the tag format and returns the component parts
    """
    parsed =  tag.split('.')

    try:
        #allow for at most 2 minor decimals...i mean comeon
        major = int(parsed[0])
        minor = int(parsed[1])
        build = int(parsed[2][0:2])
        return (major, minor, build)
    except Exception as e:
        print e
        abort("""Must be of the form <major_version>.<minor>.<maintence>, like
              0.0.1. Only integers allowed""")

def write_version(version):
    """
    Write out the version python file to the link directory before installing
    
    version needs to be a list or tuple of the form (<major>, <minor>, <build>)
    or a string in the format <major>.<minor>.<build> all ints
    """
    file_name ='link/__init__.py'
    init = open(file_name)
    init_read = init.readlines()
    init.close()
    version_line =  [idx for idx, x in enumerate(init_read) if '__version__ = ' in x]
    if len(version_line)>1:
        raise Exception('version is in there more than once')
    
    if isinstance(version, str):
        try:
            version_split = map(int, version.split('.'))
        except:
            raise Exception("Version string must be in the format <major>.<minor>.<build>")

    if not isinstance(version_split, (list, tuple)) or len(version_split)!=3:
        raise Exception('invalid version %s' % version)

    init_read[version_line[0]] = "__version__ = '%s'\n" % version
    init = open(file_name, 'w')
    try:
        init.write(''.join(init_read))
    finally:
        init.close()

def prompt_for_tag(default_offset=1, stable_only = False):
    """
    Prompt for the tag you want to use, offset for the default by input
    """
    tags = tag_names(10, stable_only)
    print "Showing latest tags for reference"
    default = '0.0.1'
    if tags:
        default = tags[0] 
    (major, minor, build) = check_tag_format(default)

    build = build+default_offset

    new_default = '%s.%s.%s' % (major, minor, build)
    tag = prompt('Tag name [in format x.xx] (default: %s) ? ' % new_default)
    tag = tag or new_default
    return tag

def push_to_pypi():
    """
    Will push the code to pypi
    """
    if prompt('would you like to tag a new version first [y/n]') == 'y':
        tag()
    local('python setup.py sdist upload')

def prompt_commit():
    """
    prompts if you would like to commit
    """
    local('git status')
    print 
    print
    _commit = prompt('Do you want to commit? [y/n]') == 'y'
    if _commit:
        msg = prompt('Commit message: ') 
        return commit(msg)

def tag(mark_stable=False):
    """
    Tag a release, will prompt you for the tag version.  You can mark it as
    stable here as well
    """
    tag = prompt_for_tag()
    print "writing this tag version to version.py before commiting"
    write_version(tag)

    print 
    _commit = prompt_commit()
    print
    

    if not _commit and not tag:
        print 
        print "Nothing commited, using default tag %s" % default
        print 
        tag = default
    else:
        msg = ''
        if mark_stable:
            msg = STABLE_MSG + ' '
        msg += prompt("enter msg for tag: ")

        local('git tag %(ref)s -m "%(msg)s"' % { 'ref': tag, 'msg':msg})

    local('git push --tags')
    return tag
 
def merge(branch=None, merge_to = 'master'):
    """
    Merge your changes and delete the old branch
    """
    if not branch:
        print "no branch specified, using current"
        branch = current_branch()
    if prompt('confirm merge with of branch %s to %s [y/N]' % (branch, merge_to)) == 'y':
        prompt_commit()
        local('git checkout %s ' % merge_to)
        local('git merge %s ' % branch)
        if prompt('delete the old branch locally and remotely? [y/N]') == 'y':
            local('git branch -d %s' % branch)
            local('git push origin :%s' % branch)
        else:
            print "leaving branch where it is"
    if prompt('push results [y/N]' ) == 'y':
        local('git push')

def tag_deploy(mark_stable=False):
    """
    Asks you to tag this release and Figures out what branch you are on. 
    It then calls the deploy function
    """
    local('git fetch --tags')
    branch = local('git branch | grep "^*" | cut -d" " -f2', capture=True)

    _tag = tag(mark_stable=mark_stable)

    deploy(_tag, branch)

def retag(tag, msg):
    """
    Retag a tag with a new message
    """
    local('git tag %s %s -f -m "%s"' % (tag, tag, msg))
    local('git push --tags')

def mark_stable(tag, msg = None):
    """
    Mark a previous tag as stable
    """
    retag(tag, '%s %s' % (STABLE_MSG, msg) )

def current_branch():
    current_branch = local('git branch | grep "^*"', capture=True).lstrip('* ')
    print "Current branch is %s" % current_branch
    return current_branch

def deploy(tag=None, branch=None, stable_only=False):
    """
    This is only for deployment on a dev box where everything can be owned by
    this user.  This is NOT for production deployment.  Put's the code in
    code_dir
    """
    if not tag:
        tag = prompt_for_tag(0, stable_only = stable_only)

    configure()
    setup_environment()
   
    #check out all the code in the right place
    with cd(code_dir):
        # i **THINK** you have to have the branch checked out before you can
        # checkout the tag
        if branch:
            #then you haven't even checkout this branch
            branches = run('git branch')
            
            if branch not in branches:
                run('git checkout -b %s' % branch)
            
            _current_branch = current_branch()

            if "* %s" % branch != _current_branch:
                run('git checkout %s' % branch)

            #pull the latest
            run('git pull origin %s' % branch)
        else:
            run("git pull origin master")
        #check out a specific tag
        if tag:
            run("git fetch --tags")
            run("git checkout %s" % tag)

    #hacky 
    if env.user == 'root':
    #make sure everything is still owned by the deployer
        run('chown -R %s %s' % (deploy_user, code_dir))


###
# How to setup a fresh box.  You probably have to run this as root for it to
# work
###
def install_easy_install():
    """
    Installs setup tool, this should also go into an RPM
    """
    run('wget http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11-py2.7.egg#md5=fe1f997bc722265116870bc7919059ea')
    run('sh setuptools-0.6c11-py2.7.egg') 

def install_python():
    """
    Installs python, I should be able to create an RPM eventually
    """
    run('wget http://python.org/ftp/python/2.7.2/Python-2.7.2.tgz')
    run('tar -xvf Python-2.7.2.tgz')
    with cd('Python-2.7.2'):
        run('./configure')
        run('make')
        run('make install')


###
# This isn't reall necessary but i'll keep it for now
###
def install_python_dependancies():
    """
    Easy install all the packages we need
    """
    run('easy_install requests')
    run('easy_install numpy')
    run('easy_install pandas')
    run('easy_install happybase')
    run('easy_install flask')
    run('easy_install ipython')
    run('easy_install gunicorn')
    run('easy_install link')
    run('easy_install pymongo')
    run('easy_install mysql-python')
    run('easy_install docutils')

def install_box_libraries():
    """
    Installs the libs you need like readlines and libsqlite. This will only 
    run on a ubuntu machine with apt-get
    """
    with settings(warn_only=True):
        has_apt = run('which apt-get') 

    if has_apt:
        run('apt-get install make')
        run('apt-get install libsqlite3-dev') 
        run('apt-get install libreadline6 libreadline6-dev')
        run('apt-get install libmysqlclient-dev')
    else:
        print "this is not an ubuntu system...skipping"

def setup_box():
    """
    Will install python and all libs needed to set up this box to run the 
    examjam code.  Eventually this needs to be more RPM based
    """
    #place_pub_key()
    install_box_libraries()
    install_python()
    install_easy_install()
    install_python_dependancies()

