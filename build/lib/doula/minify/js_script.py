from jinja2 import environmentfilter
from jsmin import jsmin
from pyramid import threadlocal
from time import time

import fnmatch
import shutil
import os
import pdb
import re
import sys
import time

VERSION_FILE = 'version.txt'
# Template files to search in project
TPL_FILE_TYPES = ['.htm', '.html', '.jinja2']

COM_LIB_LIST = ['jquery.js', 'jquery.cookie.js']

# The cStringIO class used for speed and memory efficiency
# see http://www.skymind.com/~ocrow/python_string/
from cStringIO import StringIO

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


# alextodo, use the name of the context, it's the name of the template owning this context
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
    # the COM_LIB_LIST files would always go into they're own file and served as a single
    # resource. That list of files would always come down as a whole. So even if you don't
    # list a specific lib file, you'll still get it to ensure we don't have to recompile
    """
    registry = threadlocal.get_current_registry()
    prodjs_path = registry.settings['prod_js_path']
    
    # need the template file name
    tpl_filename = 'tpl_file.html'
    version = get_version_from_env(env, prodjs_path)
    
    prod_filename = get_prod_filename(filename, prodjs_path, version)
    script_tag = '<script type="text/javascript" src="'
    script_tag+= '/prodjs/' + prod_filename + '"></script>'
    
    return script_tag


def get_version_from_env(env, prodjs_path):
    if env.globals.get('js_version', 0) > 0:
        return env.globals.get('js_version')
    else:
        # get version, save to env
        version = get_version(prodjs_path, 0)
        env.globals['js_version'] = version
        
        return version


def get_minified_js(js_files, js_dir):
    """
    Minify js files in the list as a single file.
    Roll through the js_files, read their contents,
    put them into a single string for writing
    """
    minified_js = StringIO()
    
    # roll through the js files and minify them
    # save result to string to save to a single file
    for js_file in js_files:
        js_path = clean_path(js_dir + js_file.replace('/js', ''))
        
        if os.path.isfile(js_path):
            actual_js_file = open(js_path, 'r')
        else:
            raise Exception(js_path + ' is not a file')
        
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


def index_project_files(path):
    """
    Builds a list of all the template files that need to
    be searched for js_scripts
    """
    files = [ ]
    
    for root, dirnames, filenames in os.walk(path):
        # Ignore directories that start with a dot
        if root.find('/.') == -1:
            for file_name in filenames:
                if is_approved_file_type(file_name):
                    path_to_file = root.rstrip('/') + '/' + file_name
                    files.append(path_to_file)
    
    return files


def is_approved_file_type(file_name):
    is_approved = False
    
    for ftype in TPL_FILE_TYPES:
        if file_name.endswith(ftype):
            is_approved = True
            break
    
    return is_approved


def find_js_scripts(path_to_file):
    """
    Find the js_scripts embedded in our templates
        ex. ['/js/jquery.js', '/js/bootstrap-dropdown.js', '/js/doula.js']
    """
    regex = r'\[(.*)\]|js_script'
    contents = get_clean_contents(path_to_file)
    matches = re.findall(regex, contents)
    js_scripts = ''
    
    if len(matches) > 0:
        js_scripts = matches[0].strip()
    
    return js_scripts


def get_clean_contents(path_to_file):
    """
    Read the contents of the file into a single string.
    Replace all new line characters with a space so that
    we can run regex on the entire file as a single string
    """
    tpl = open(path_to_file)
    contents = tpl.read()
    tpl.close()
    
    contents = re.sub(r'\s+', ' ', contents)
    
    return contents


def get_cleaned_scripts(scripts):
    """
    Return string '/js/jquery.js', '/js/home.js'
    as list of individual strings split by commas
    """
    scripts_list = scripts.split(',')
    scripts = [script.replace('"', '').replace("'", "").strip() 
                for script in scripts_list ]
    
    return scripts


def get_prod_filename(filename, prodjs_path, version=0):
    """
    Return the production file name:
        Format template_name.version.js
    """
    filename_list = filename.split('/')
    prod_name = filename_list[len(filename_list) - 1].split('.')[0]
    
    version = get_version(prodjs_path, version)
    
    return prod_name + '.' + version + '.js'


def get_version(prodjs_path, version):
    if version > 0:
        return str(version)
    else:
        version_file = open(clean_path(prodjs_path + '/' + VERSION_FILE))
        version = version_file.read()
        version_file.close()
        
        return str(version)


def create_prod_file(prodjs_dir, prod_filename, minified_js):
    # Actually write the minified files
    path = clean_path(prodjs_dir + '/' + prod_filename)
    prod_file = open(path, 'w')
    prod_file.write(minified_js)
    prod_file.close()


def minify_page_scripts(filename, scripts, js_path, prodjs_path):
    scripts = get_cleaned_scripts(scripts)
    minified_js = get_minified_js(scripts, js_path)
    prod_filename = get_prod_filename(filename, prodjs_path)
    create_prod_file(prodjs_path, prod_filename, minified_js)


def get_filename_to_scripts(files):
    """
    Roll through the project files and find the scripts.
    Add to the dict, with format:
        { filename: [list_of_js_files] }
    """
    filenames_to_scripts = { }
    
    for f in files:
        js_scripts = find_js_scripts(f)
        
        if js_scripts:
            filenames_to_scripts[f] = js_scripts
            
    return filenames_to_scripts


def minify_all_js_files(tpl_path, js_path, prodjs_path):
    """
    Find all the js_script filters embedded in template files.
    Find the scripts in the js folder and minify them into a single js file
    named after the template they were created for.
    
    For example the template home_page.html with the following filter:
        {{ ['/js/jquery.js', '/js/home.js']|js_script|safe }}
    
    Will create a production file named:
        /prodjs/home_page.[version].js
        
    The version number is stored in the /prodjs/version.txt file.
    """
    prep_prodjs_dir(prodjs_path)
    
    files = index_project_files(tpl_path)
    filenames_to_scripts = get_filename_to_scripts(files)
    
    for filename, scripts in filenames_to_scripts.items():
        minify_page_scripts(filename, scripts, js_path, prodjs_path)


def prep_prodjs_dir(prodjs_path):
    """
    Prepare the /prodjs/ directory for minification
    """
    # Remove all the files in this directory
    shutil.rmtree(prodjs_path)
    
    # Make sure the prod js dir exists
    os.makedirs(prodjs_path)
    
    # Make the /prodjs/version.txt file and save current unix timestamp
    t = str(time.time())
    version = t.split('.')[0]
    
    version_file = open(clean_path(prodjs_path + '/' + VERSION_FILE), 'w')
    version_file.write(version)
    version_file.close()


if __name__ == '__main__':
    path = '/Users/alexvazquezOLD/boxes/doula'
    tpl_path = path + '/doula/templates/'
    js_path = path + '/doula/static/js/'
    prodjs_path = path + '/doula/static/prodjs/'
    
    print 'Minifying ...'
    minify_all_js_files(tpl_path, js_path, prodjs_path)
    
    print 'Done minifying'
    
