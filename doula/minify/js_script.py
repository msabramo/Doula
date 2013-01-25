from cStringIO import StringIO
from jinja2 import contextfilter
from jsmin import jsmin
from os import listdir

import json
import os
import re
import shutil

#################################
# Load the production JS files
# into memory from disk
#################################

prodjs_path = os.path.dirname(os.path.realpath(__file__)) + '/../static/prodjs'
production_js_filenames = {}


def load_production_js_filenames():
    """
    Load the production_js_filenames into memory
    """
    prodjs_files = []

    for f in listdir(prodjs_path):
        if os.path.isfile(os.path.join(prodjs_path, f)):
            prodjs_files.append(f)

    for prodjs_file in prodjs_files:
        last_js_filename = re.sub(r'\d+\.', '', prodjs_file)
        production_js_filenames[last_js_filename] = prodjs_file

load_production_js_filenames()

############################
# js_script and js_script_dev are called from jinja2 templates
# they return the proper script tags
############################


def js_script_dev(js_files):
    """
    Creates the script tags for development
    """
    script_tags = ''

    for js_file in js_files:
        script_tags += '<script type="text/javascript" src="'
        script_tags += js_file + '"></script>'
        script_tags += "\n"

    return script_tags


@contextfilter
def js_script(ctx, js_files):
    """
    Handles creating the script tags for production.
    The last filename is always used as the name of the production file.
    """
    script_tag = ''
    # Get a clean name of the last js file
    last_js_file = js_files.pop()
    last_js_file = last_js_file.replace('/', '_').lstrip('_')

    if production_js_filenames[last_js_file]:
        prodjs_filename = production_js_filenames[last_js_file]
        script_tag = "<script type=\"text/javascript\" src=\""
        script_tag += "/prodjs/%s\"></script>" % prodjs_filename

    return script_tag


def read(file_path):
    if os.path.isfile(file_path):
        f = open(file_path, 'r')
        contents = f.read()
        f.close()

        return contents
    else:
        raise Exception(file_path + ' is not a file')


###########################
# Minify Project Class
###########################

class MinifyProject():
    def __init__(self, tpl_path, static_path):
        self.tpl_path = tpl_path
        self.static_path = static_path
        self.template_js_files_order = {}

    # Main minification function
    def minify_all_js_files(self):
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
        self._create_prodjs_directories()

        template_files = self._find_templates_files()
        template_to_js_files = self._find_js_files_for_every_template(template_files)

        # Step 3 and 4
        # Create invididual minified files
        self._create_minified_single_files(template_to_js_files)

        # Step 5 and 6
        self._create_minified_combined_files(template_to_js_files)

        # Step 7
        self._save_dot_jsmin(template_to_js_files)

        return 0

    def _create_prodjs_directories(self):
        """
        Prepare the prodjs and prodjs/single_files directories for minification
        """
        # Clear the directory
        shutil.rmtree(self.static_path + '/prodjs')

        # Make sure the prod_js and prod_js/single_files dirs exists
        if not os.path.isdir(self.static_path + '/prodjs'):
            os.makedirs(self.static_path + '/prodjs')

        if not os.path.isdir(self.static_path + '/prodjs/single_files'):
            os.makedirs(self.static_path + '/prodjs/single_files')

    # Step 1
    def _find_templates_files(self):
        """
        Builds a list of all the template files that need to
        be searched for js_scripts
        """
        files = []

        for root, dirnames, filenames in os.walk(self.tpl_path):
            # Ignore directories that start with a dot
            if root.find('/.') == -1:
                for file_name in filenames:
                    if self._is_approved_file_type(file_name):
                        path_to_file = root.rstrip('/') + '/' + file_name
                        files.append(path_to_file)

        return files

    def _is_approved_file_type(self, file_name):
        is_approved = False

        # Search only these file types
        for ftype in ['.htm', '.html', '.jinja2']:
            if file_name.endswith(ftype):
                is_approved = True
                break

        return is_approved

    # Step 2 and 3. Get list of files and their timestamps
    def _find_js_files_for_every_template(self, files):
        """
        Roll through the project files and find the scripts.
        Add to the dict, with format:
            { filename: [list_of_js_files] }
        """
        filenames_to_scripts = {}

        for path_to_file in files:
            js_scripts = self._find_js_files_for_template(path_to_file)

            if js_scripts:
                filenames_to_scripts[path_to_file] = js_scripts

        return filenames_to_scripts

    def _find_js_files_for_template(self, path_to_file):
        """
        Find the js_scripts embedded in our templates.
        Return the js file name with path and the timestamp
            ex. {'/js/jquery.js': 1349805083.0, '/js/bootstrap-dropdown.js':1349805083.0}
        """
        # Pull the js files out of the template
        regex = r'{{\s+\[(.*)\]|js_script'
        contents = self._get_clean_contents(path_to_file)
        matches = re.findall(regex, contents)
        js_scripts = ''

        if len(matches) > 0:
            js_scripts = matches[0].strip()

        # break the js_scripts into a list of files
        js_script_files = [js_script.strip().rstrip("'").lstrip("'")
                           for js_script in js_scripts.split(',')
                           if js_script]

        # create a dictionary with file path to timestamp
        js_to_timestamps = {}

        for js_script_file in js_script_files:
            if js_script_file:
                file_stats = os.stat(self.static_path + js_script_file)
                js_to_timestamps[js_script_file] = file_stats.st_mtime

        # Save the order of js files for the future
        if len(js_script_files) > 0:
            self.template_js_files_order[path_to_file] = js_script_files

        return js_to_timestamps

    def _get_clean_contents(self, path_to_file):
        """
        Read the contents of the file into a single string.
        Replace all new line characters with a space so that
        we can run regex on the entire file as a single string
        """
        contents = read(path_to_file)
        return re.sub(r'\s+', ' ', contents)

    # Step 3 and 4
    def _create_minified_single_files(self, template_to_js_files):
        """
        Create the individual single files in the /prodjs/single_files directory
        """
        for template in template_to_js_files:
            # Run through the js_files in the order they were added to the template
            for js_file in self.template_js_files_order[template]:
                timestamp = template_to_js_files[template][js_file]
                clean_file_name = self._clean_js_filename(js_file, timestamp)
                new_js_file_path = self.static_path + '/prodjs/single_files/' + clean_file_name

                if not os.path.isfile(new_js_file_path):
                    f = open(new_js_file_path, 'w')
                    f.write(jsmin(read(self.static_path + js_file)))
                    f.close()

    # Step 5 and 6
    def _create_minified_combined_files(self, template_to_js_files):
        """
        Create the minified/combined files in the prodjs directory.
        The name of the minified file format is:
            [_clean_js_filename].[combined timestamps values].js
        """
        for template in template_to_js_files:
            js_to_timestamps = template_to_js_files[template]
            combined_timestamps = sum(int(x) for x in js_to_timestamps.values())

            last_js_file = None
            minified_js_buffer = StringIO()

            # Run through the js files in the correct order
            for js_file in self.template_js_files_order[template]:
                timestamp = template_to_js_files[template][js_file]
                last_js_file = self._clean_js_filename(js_file, combined_timestamps)
                single_js_filename = self._clean_js_filename(js_file, timestamp)

                # print 'Adding singlejs_filename: ' + single_js_filename
                minified_js_file = self.static_path + '/prodjs/single_files/' + single_js_filename

                minified_js_buffer.write(read(minified_js_file))
                minified_js_buffer.write(";")

            f = open(self.static_path + '/prodjs/' + last_js_file, 'w')
            f.write(minified_js_buffer.getvalue())
            f.close()

    def _clean_js_filename(self, js_file, timestamp):
        clean_file_name = js_file.replace('/', '_').lstrip('_')
        clean_timestamp = str(timestamp).replace('.0', '')
        clean_file_name = clean_file_name.replace('.js', '.' + clean_timestamp + '.js')

        return clean_file_name

    # Step 7
    def _save_dot_jsmin(self, template_to_js_files):
        f = open(self.static_path + '/prodjs/.jsmin', 'w')
        f.write(json.dumps(template_to_js_files))
        f.close()


if __name__ == '__main__':
    # Steps for this process are
    # 1) get list of files // done
    # 2) get their timestamps // done
    # 3) see if the prodjs/single_files/[name of file].timestamp.js exists // done
    # 4) if it does not exist. create minified version of that file // done
    # 5) combo those files into the update version. minified version of that dir.
    # 6) The comboed file name will be prodjs/[name of last file in array].[comboed timestamps].js
    # 7) save reference info to a .jsmin file with json indicating that referencing these files gets you this filename for prod
    # 8) Make it work for prod
    static_path = os.getcwd() + '/doula/static'
    tpl_path = os.getcwd() + '/doula/templates'
    js_path = os.getcwd() + '/doula/static/js'
    prodjs_path = os.getcwd() + '/doula/static/prodjs'

    print 'Minifying Project...'
    mp = MinifyProject(tpl_path, static_path)
    mp.minify_all_js_files()
    print 'Done minifying'
