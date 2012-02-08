from jinja2 import environmentfilter
from pyramid import threadlocal
from time import time
from jsmin import jsmin

# The cStringIO class used for speed and memory efficiency
# see http://www.skymind.com/~ocrow/python_string/
from cStringIO import StringIO

# todo, also look at async loader, would that be any good?
# see require.js
def js_script_dev(js_files):
    """
    Handles creating the script tags for development.
    """
    script_tags = ''
    
    for js_file in js_files:
        script_tags += '<script type="text/javascript" src="'
        script_tags += js_file + '"></script>'
        script_tags += "\n"
    
    return script_tags


library_list = ['jquery.js', 'jquery.cookie.js']

@environmentfilter
def js_script(env, js_files, js_file_name = ''):
    """
    Handles creating the script tags for production.
    If the js_file_name isn't passed in, the last js file name
    passed in the list js_file will be used to name the prod
    js file.
    
    For example the following function call:
        js_script(env, ['jquery.js', 'jquery.someplugin.js', '/subfolder/form.js'])
    
    will output a compiled file
        /prodjs/subfolder/form.js
        
    # todo, take a look at putting a common file list into a special combine list
    # the library_list files would always go into they're own file and served as a single
    # resource. That list of files would always come down as a whole. So even if you don't
    # list a specific lib file, you'll still get it to ensure we don't have to recompile
    
    # todo, look at adding a version number, maybe pull from ini file? dunno, pull from git?
    # could also consider setting a unix timestamp everytime the server is restarted
    # on env.globals['timestamp'], then setting that up
    """
    make_scripts_dict(env)
    prod_js_filename = get_prod_js_filename(js_files, js_file_name)
    
    if file_does_not_exist(prod_js_filename, env):
        make_prod_js_file(prod_js_filename, js_files)
        print 'Done making js file: ' + prod_js_filename
        env.globals['scripts'].append(prod_js_filename)
    
    script_tag = '<script type="text/javascript" src="'
    script_tag+= '/prodjs' + prod_js_filename + '"></script>'
    
    return script_tag


def make_scripts_dict(env):
    if not 'scripts' in env.globals:
        env.globals['scripts'] = [ ]


def get_prod_js_filename(js_files, js_file_name):
    prod_js_filename = ''
    
    if js_file_name:
        prod_js_filename = js_file_name
    else:
        prod_js_filename = js_files[len(js_files) - 1]
        
    return prod_js_filename.replace('/js', '')


def file_does_not_exist(js_file, env):
    """
    Determine if the JS file already exist on disk by
    checking the env.globals provided by jinja2
    """
    if js_file in env.globals['scripts']:
        return False
    else:
        return True


def make_prod_js_file(prod_js_filename, js_files):
    registry = threadlocal.get_current_registry()
    minified_js = minify_js_files(js_files, registry)
    
    # Create and write to the final file we'll use to serve
    path_to_prod_js = clean_path(registry.settings['prod_js_path'] + '/' + prod_js_filename)
    prod_js_file = open(path_to_prod_js, 'w')
    prod_js_file.write(minified_js)
    prod_js_file.close()


def minify_js_files(js_files, registry):
    minified_js = StringIO()
    path_to_js_dir = registry.settings['js_path']
    
    # roll through the js files and minify them
    # save result to string to save to a single file
    for js_f in js_files:
        path_to_js = clean_path(path_to_js_dir + js_f.replace('/js', ''))
        actual_js_file = open(path_to_js, 'r')
        
        try:
            minified_js.write(jsmin(actual_js_file.read()))
        finally:
            actual_js_file.close()
    
    return minified_js.getvalue()


def clean_path(path):
    """
    Ensure we don't get any double forward slashes if 
    ini settings are entered incorrectly
    """
    return path.replace('//', '/')

