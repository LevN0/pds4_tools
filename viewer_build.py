from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import sys
import json
import time
import glob
import errno
import shutil
import zipfile
import plistlib
import argparse
import textwrap
import platform
import threading
import subprocess


LOCAL_DIR = os.path.dirname(os.path.realpath(__file__))
BUILD_DIR = os.path.join(LOCAL_DIR, 'build')

EXCLUDE_DATA_PYINSTALLER = [os.path.join('mpl-data', 'sample_data')]
EXCLUDE_DATA_PY2APP = [os.path.join('Contents', 'Resources', 'lib', 'python*', 'matplotlib', 'mpl-data')]


def build():

    system = platform.system().lower()

    build_func = {'windows': build_windows,
                  'linux':   build_linux,
                  'darwin':  build_mac
                  }.get(system)

    if build_func is None:
        raise RuntimeError('Unknown OS.')

    build_func()


def build_windows():

    DEPS = (
        'pyinstaller==3.6',
        'numpy==1.16.6',
        'matplotlib==3.1.3'
    )

    SPEC_FILE = """
        import os
            
        code_dir  = os.path.abspath(r'{code_dir}')
        viewer       = os.path.join(code_dir, 'viewer_script.py')
        window_icon  = os.path.join(code_dir, 'pds4_tools/viewer/logo/logo.gif')
        taskbar_icon = os.path.join(code_dir, 'pds4_tools/viewer/logo/logo.ico')
        
        a = Analysis([viewer],
                     pathex=[code_dir],
                     binaries=None,
                     datas=[ (window_icon, '.'), (taskbar_icon, '.') ],
                     hiddenimports=['pds4_tools', 'numpy', 'matplotlib', 'FileDialog',
                                    'tkinter', 'tkinter.colorchooser', 'tkinter.filedialog'],
                     hookspath=None,
                     runtime_hooks=None,
                     excludes=None,
                     win_no_prefer_redirects=None,
                     win_private_assemblies=None,
                     cipher=None)
        
        exclude_data = {exclude_data}
        a.datas = [x for x in a.datas if not any(exclude in x[1] for exclude in exclude_data)]
         
        pyz = PYZ(a.pure, 
                  a.zipped_data,
                  cipher=None)
        
        exe = EXE(pyz,
                  a.scripts,
                  a.binaries,
                  a.zipfiles,
                  a.datas,
                  name='{exe_name}',
                  debug=False,
                  strip=None,
                  upx=True,
                  console=False,
                  icon=taskbar_icon)
    """

    output_dir = os.path.join(BUILD_DIR, 'dist')
    output_file = os.path.join(output_dir, 'pds4_viewer.exe')

    # Install dependencies
    install_dependencies(DEPS)

    # Write PyInstaller spec file
    spec_file_ = os.path.join(BUILD_DIR, 'pds4_viewer.spec')
    with open(spec_file_, 'w') as file_handler:

        content = SPEC_FILE.format(code_dir=LOCAL_DIR,
                                   exclude_data=json.dumps(EXCLUDE_DATA_PYINSTALLER),
                                   exe_name=os.path.basename(output_file))

        file_handler.write(textwrap.dedent(content))

    # Create the build
    run_pyinstaller(spec_file_, output_dir)

    # Set LICENSE file line-endings to CRLF
    license_file = os.path.join(LOCAL_DIR, 'LICENSES')
    license_file_crlf = os.path.join(output_dir, 'LICENSES.TXT')

    with open(license_file, 'rU') as file_handler_in:
        with open(license_file_crlf, 'w', newline='\r\n') as file_handler_out:
            file_handler_out.writelines(file_handler_in.readlines())

    # Create ZIP containing binary and LICENSE
    zip_file_ = os.path.join(BUILD_DIR, 'PDS4_viewer_windows-{}.zip'.format(get_package_version()))
    create_zip(zip_file_,
               inputs=[output_file,
                       license_file_crlf])


def build_linux():

    DEPS = (
        'pyinstaller==3.5',
        'numpy==1.16.6 --no-binary :all:',
        'matplotlib==3.1.3',
        'certifi'
    )

    SPEC_FILE = """
        import os

        code_dir  = os.path.abspath(r'{code_dir}')
        viewer       = os.path.join(code_dir, 'viewer_script.py')
        window_icon  = os.path.join(code_dir, 'pds4_tools/viewer/logo/logo.gif')
        taskbar_icon = os.path.join(code_dir, 'pds4_tools/viewer/logo/logo.ico')

        a = Analysis([viewer],
                     pathex=[code_dir],
                     binaries=None,
                     datas=[ (window_icon, '.'), (taskbar_icon, '.') ],
                     hiddenimports=['pds4_tools', 'numpy', 'matplotlib', 'FileDialog',
                                    'tkinter', 'tkinter.colorchooser', 'tkinter.filedialog'],
                     hookspath=None,
                     runtime_hooks=None,
                     excludes=None,
                     win_no_prefer_redirects=None,
                     win_private_assemblies=None,
                     cipher=None)

        exclude_data = {exclude_data}
        a.datas = [x for x in a.datas if not any(exclude in x[1] for exclude in exclude_data)]

        pyz = PYZ(a.pure, 
                  a.zipped_data,
                  cipher=None)

        exe = EXE(pyz,
                  a.scripts,
                  a.binaries,
                  a.zipfiles,
                  a.datas,
                  name='{exe_name}',
                  debug=False,
                  strip=None,
                  upx=True,
                  console=False,
                  icon=taskbar_icon)
    """

    output_dir = os.path.join(BUILD_DIR, 'dist')
    output_file = os.path.join(output_dir, 'pds4_viewer')

    # Install dependencies
    install_dependencies(DEPS)

    # Write PyInstaller spec file
    spec_file_ = os.path.join(BUILD_DIR, 'pds4_viewer.spec')
    with open(spec_file_, 'w') as file_handler:

        content = SPEC_FILE.format(code_dir=LOCAL_DIR,
                                   exclude_data=json.dumps(EXCLUDE_DATA_PYINSTALLER),
                                   exe_name=os.path.basename(output_file))

        file_handler.write(textwrap.dedent(content))

    # Create the build
    run_pyinstaller(spec_file_, output_dir)

    # Give chmod +x permissions to binary
    os.chmod(output_file, 0o755)

    # Create ZIP containing binary and LICENSE
    zip_file_ = os.path.join(BUILD_DIR, 'PDS4_viewer_linux-{}.zip'.format(get_package_version()))
    create_zip(zip_file_,
               inputs=[output_file,
                       os.path.join(LOCAL_DIR, 'LICENSES')])


def build_mac():

    version = platform.mac_ver()[0]
    version_split = version.split('.')
    major, minor = int(version_split[0]), int(version_split[1])

    if major == 10 and minor <= 10:
        build_mac_10_6()

    else:
        build_mac_10_11()


def build_mac_10_11():

    DEPS = (
        'py2app==0.20',      # must use 0.13 bootloader to support OSX 10.11
        'numpy==1.13.3',     # keep NumPy wheel size down
        'matplotlib==3.1.3',
        'certifi'
    )

    SPEC_FILE = """
    
        from setuptools import setup
         
        setup(name='{exe_name}',
         
            app=['viewer_script.py'],
            setup_requires=['py2app'],
            
            options=dict(py2app=dict(
            
                iconfile='pds4_tools/viewer/logo/logo.icns',
                packages=['certifi'],
                
                plist=dict(NSPrincipalClass='NSApplication',
                           NSHighResolutionCapable=True,
                           LSBackgroundOnly=False,
                           CFBundleDevelopmentRegion='en'),

            )),
        )
    """

    BROKEN_WARN="""
        def _prevent_broken_osx():
     
            import os
            import sys
            import platform
            import subprocess
         
            if sys.platform != 'darwin':
                return
         
            version, _, _ = platform.mac_ver()
            if (version == '10.14.6') and ('--bypass-broken' not in sys.argv):

                msg = ['PDS4 Viewer: OS-X 10.14.6 is not supported due to a serious OS bug.',
                       'Use --bypass-broken to continue at your own risk. Save all work first!',
                       'Exiting...', '']

                sys.stderr.write(os.linesep.join(msg))
                subprocess.call("osascript -e '"
                                'tell app (path to frontmost application as text) to display dialog "{0}"'
                                'with title "PDS4 Viewer" with icon stop buttons {{"Quit"}}'
                                "'".format(' '.join(msg)), shell=True)
                
                sys.exit(1)
     
        _prevent_broken_osx()
    """

    output_dir = os.path.join(BUILD_DIR, 'dist')
    output_file = os.path.join(output_dir, 'pds4_viewer.app')

    # Install dependencies
    install_dependencies(DEPS)

    # Write Py2app setup file
    spec_file_ = os.path.join(BUILD_DIR, 'setupApp.py')
    with open(spec_file_, 'w') as file_handler:

        content = SPEC_FILE.format(exe_name=os.path.splitext(os.path.basename(output_file))[0])
        file_handler.write(textwrap.dedent(content))

    # Create the build
    run_py2app(spec_file_, output_dir)

    # Insert patch for OS X 10.14.6
    boot_file = os.path.join(output_file, 'Contents', 'Resources', '__boot__.py')

    with open(boot_file, 'r+') as file_handler:

        content = file_handler.read()
        index = content.index('def _setup_ctypes()')
        content = content[:index-2] + textwrap.dedent(BROKEN_WARN) + content[index-2:]

        file_handler.seek(0)
        file_handler.writelines(content)

    # Remove unnecessary keys from Info.plist
    plist_file = os.path.join(output_file, 'Contents', 'Info.plist')
    remove_keys = ['PythonInfoDict', 'CFBundleIdentifier', 'CFBundleVersion', 'CFBundleSignature',
                   'NSHumanReadableCopyright', 'NSMainNibFile=']

    with open(plist_file, 'rb+') as file_handler:

        # API change in plistlib between Python2.7 and Python3.4+
        plist_load = plistlib.load if hasattr(plistlib, 'load') else plistlib.readPlist
        plist_dump = plistlib.dump if hasattr(plistlib, 'load') else plistlib.writePlist

        plist = plist_load(file_handler)

        for key in remove_keys:
            del plist[key]

        file_handler.seek(0)
        file_handler.truncate()

        plist_dump(plist, file_handler)

    # Remove excluded data
    # (Py2app does not provide a method to exclude data files with-in config)
    for exclude_path in EXCLUDE_DATA_PY2APP:
        _remove_path(os.path.join(output_file, exclude_path))

    # Give chmod +x permissions to binary
    files = glob.glob(os.path.join(output_file, 'Contents', 'MacOS'))
    for file in files:
        os.chmod(file, 0o755)

    # Create ZIP containing binary and LICENSE
    zip_file_ = os.path.join(BUILD_DIR, 'PDS4_viewer_mac10_13-{}.zip'.format(get_package_version()))
    create_zip(zip_file_,
               inputs=[output_file,
                       os.path.join(LOCAL_DIR, 'LICENSES')])


def build_mac_10_6():

    DEPS = (
        'pyinstaller==3.3',   # must use 3.2.1 bootloader to support OSX 10.6
        'numpy==1.13.3',      # keep NumPy wheel size down
        'matplotlib==2.2.4',  # latest working version with python 2.7
        'certifi'
    )

    SPEC_FILE = """
        import os

        code_dir  = os.path.abspath(r'{code_dir}')
        viewer       = os.path.join(code_dir, 'viewer_script.py')
        window_icon  = os.path.join(code_dir, 'pds4_tools/viewer/logo/logo.gif')
        taskbar_icon = os.path.join(code_dir, 'pds4_tools/viewer/logo/logo.icns')

        a = Analysis([viewer],
                     pathex=[code_dir],
                     binaries=None,
                     datas=[ (window_icon, '.'), (taskbar_icon, '.') ],
                     hiddenimports=['pds4_tools', 'numpy', 'matplotlib', 'FileDialog',
                                    'Tkinter', 'tkColorChooser', 'tkFileDialog'],
                     hookspath=None,
                     runtime_hooks=None,
                     excludes=None,
                     win_no_prefer_redirects=None,
                     win_private_assemblies=None,
                     cipher=None)

        exclude_data = {exclude_data}
        a.datas = [x for x in a.datas if not any(exclude in x[1] for exclude in exclude_data)]

        pyz = PYZ(a.pure, 
                  a.zipped_data,
                  cipher=None)

        exe = EXE(pyz,
                  a.scripts,
                  a.binaries,
                  a.zipfiles,
                  a.datas,
                  name='{exe_name}',
                  debug=False,
                  strip=None,
                  upx=True,
                  console=False,
                  icon=taskbar_icon)

        app = BUNDLE(exe,
                     name='{app_name}',
                     icon=taskbar_icon,
                     info_plist=dict(
                           NSPrincipalClass='NSApplication',
                           NSHighResolutionCapable=True,
                           LSBackgroundOnly=False,
                           CFBundleDevelopmentRegion='en'),
                     bundle_identifier=None)
    """

    output_dir = os.path.join(BUILD_DIR, 'dist')
    output_file = os.path.join(output_dir, 'pds4_viewer.app')

    # Install dependencies
    install_dependencies(DEPS)

    # Write PyInstaller spec file
    spec_file_ = os.path.join(BUILD_DIR, 'pds4_viewer.spec')
    with open(spec_file_, 'w') as file_handler:

        content = SPEC_FILE.format(code_dir=LOCAL_DIR,
                                   exclude_data=json.dumps(EXCLUDE_DATA_PYINSTALLER),
                                   app_name=os.path.basename(output_file),
                                   exe_name=os.path.splitext(os.path.basename(output_file))[0])

        file_handler.write(textwrap.dedent(content))

    # Create the build
    run_pyinstaller(spec_file_, output_dir)

    # Give chmod +x permissions to binary
    files = glob.glob(os.path.join(output_file, 'Contents', 'MacOS'))
    for file in files:
        os.chmod(file, 0o755)

    # Create ZIP containing binary and LICENSE
    zip_file_ = os.path.join(BUILD_DIR, 'PDS4_viewer_mac10_6-{}.zip'.format(get_package_version()))
    create_zip(zip_file_,
               inputs=[output_file,
                       os.path.join(LOCAL_DIR, 'LICENSES')])


def run_pyinstaller(spec_file, output_dir):

    print('\nCreating the build ...\n')

    import PyInstaller.__main__
    PyInstaller.__main__.run(['--workpath', os.path.join(os.path.dirname(output_dir), 'build'),
                              '--distpath', output_dir,
                              spec_file])


def run_py2app(spec_file, output_dir):

    print('\nCreating the build ...\n')

    run_command([sys.executable, spec_file, 'py2app',
                 '--bdist-base', os.path.join(os.path.dirname(output_dir), 'build'),
                 '--dist-dir',   output_dir])


def run_command(args, **kwargs):
    print('Running CMD: {0}'.format(' '.join(args)))
    subprocess.check_call(args, **kwargs)


def create_zip(filename, inputs, mode=None):
    """ Create a compressed ZIP file.

    Parameters
    ----------
    filename : str
       The filename, including path, for the ZIP file to create.
    inputs : list
        A list of files or directories to add to the ZIP file. For directories,
        the basename is kept by default. Each value in *inputs* may also be a list
        itself, where the second element represents the archive name, thus
        allowing files or directories to be renamed.
    mode : str, optional
        Mode to open ``ZipFile`` with. Defaults to 'w'.

    Returns
    -------
    None
    """

    print('\nCreating the ZIP file ...\n')

    # Ensure that file / directories to compress are given in an array-like
    if not isinstance(inputs, (tuple, list)):
        raise ValueError('The *inputs* must be given as a tuple or list.')

    # Obtain mode to open ZipFile
    if mode is None:
        mode = 'w'

    # Create ZIP archive with specified input files/directories
    with zipfile.ZipFile(filename, mode, zipfile.ZIP_DEFLATED) as zip:

        for input_ in inputs:

            if isinstance(input_, (tuple, list)):
                file_or_dir = input_[0]
                archive_name = input_[1]
            else:
                file_or_dir = input_
                archive_name = os.path.basename(input_)

            if os.path.isdir(file_or_dir):

                for path, dirs, files in os.walk(file_or_dir):
                    for file in files:
                        file = os.path.join(path, file)
                        archive_name_ = os.path.join(archive_name, os.path.relpath(file, file_or_dir))
                        zip.write(file, arcname=archive_name_)

            else:
                zip.write(file_or_dir, arcname=archive_name)

    print('Output location: \n{0}'.format(filename))


def install_dependencies(deps):

    print('\nInstalling dependencies...\n')

    try:
        import pip
    except IOError as e:
        print('pip must be available.')
        raise

    for dep in deps:
        print('Installing {0} ...'.format(dep))
        run_command([sys.executable, '-m', 'pip', 'install', '--upgrade'] + dep.split(' '))


def get_package_version():

    cmd = [sys.executable, os.path.join(LOCAL_DIR, 'setup.py'), '--version']
    version = subprocess.check_output(cmd, universal_newlines=True)

    return version.strip()


def get_system_info():

    system = platform.system().lower()

    if system == 'windows':
        system_info = '{0} {1} {2}'.format(platform.system(), platform.release(), platform.version())

    elif system == 'linux':
        system_info = '{0} {1}'.format(*platform.linux_distribution())

    elif system == 'darwin':
        system_info = 'MacOS {0} {1}'.format(platform.mac_ver()[2], platform.mac_ver()[0])

    else:
        system_info = 'Unknown OS'

    return system_info


def _makedirs(path, exists_ok=True):

    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST or (not exists_ok):
            raise


def _remove_path(path, ignore_paths=(), ignore_errors=True):

    # Obtain list of paths to remove, and skip those on ignore list
    paths = [p for p in glob.glob(path) if p not in ignore_paths]

    # Remove the path
    for path_ in paths:

        if os.path.isdir(path_):
            shutil.rmtree(path_, ignore_errors=ignore_errors)

        else:

            try:
                os.remove(path_)
            except IOError:
                if not ignore_errors:
                    raise

    # Additional logic is to ensure we wait until  directory (if given) is actually deleted on Windows
    timeout = 0
    for path_ in paths:

        while os.path.exists(path_) and timeout < 10:
            timeout += 1
            time.sleep(1)


def _shlex_join(split_command):

    # Return a shell-escaped version of the string
    def quote(s):

        # Python2 does not have re.ASCII but matches that way by default
        try:
            flags = re.ASCII
        except AttributeError:
            flags = 0

        _find_unsafe = re.compile(r'[^\w@%+=:,./-]', flags).search

        if not s:
            return "''"
        if _find_unsafe(s) is None:
            return s

        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        return "'" + s.replace("'", "'\"'\"'") + "'"

    return ' '.join(quote(arg) for arg in split_command)


def _teed_call(cmd_args, **kwargs):

    def tee(infile, *files):
        def fanout(infile, *files):
            for line in iter(infile.readline, ''):
                for f in files:
                    f.write(line)
                    f.flush()
            infile.close()

        t = threading.Thread(target=fanout, args=(infile,) + files)
        t.daemon = True
        t.start()
        return t

    stdout, stderr = [kwargs.pop(s, None) for s in ('stdout', 'stderr')]
    timeout = kwargs.pop('timeout', None)
    stream = kwargs.pop('stream', False)
    p = subprocess.Popen(cmd_args,
                         stdout=subprocess.PIPE if (stdout is not None) else None,
                         stderr=subprocess.PIPE if (stderr is not None) else None,
                         universal_newlines=True,
                         shell=True,
                         **kwargs)

    threads = []
    tee_stdout = [stdout, sys.stdout] if stream else [stdout]
    tee_stderr = [stderr, sys.stderr] if stream else [stderr]
    if stdout is not None: threads.append(tee(p.stdout, *tee_stdout))
    if stderr is not None: threads.append(tee(p.stderr, *tee_stderr))

    try:

        # Wait for IO completion
        for t in threads:
            t.join()

        return p.wait()

    except KeyboardInterrupt:
        p.terminate()
        raise


def main():

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.register('type', 'bool', lambda x: x.lower() in ('yes', 'true', 't', '1'))

    parser.add_argument("--log", help="Filename, including path, for the log file.",
                        default=os.path.join(BUILD_DIR, 'log.txt'))
    parser.add_argument("--no-log", help=argparse.SUPPRESS, type='bool',
                        nargs='?', const=True, default=False, )

    args = parser.parse_args()
    log_file = args.log

    # Enable logging to file if requested
    # (works by calling this code again as subprocess while outputting the result to
    # both console and a file handler)
    if not args.no_log:

        _makedirs(os.path.dirname(log_file))

        with open(log_file, 'w') as file_handler:

            args_ = _shlex_join(['-u'] + sys.argv + ['--no-log'])
            cmd = '{0} {1}'.format(sys.executable, args_)

            return _teed_call(cmd, stream=True, stdout=file_handler, stderr=file_handler)

    # Print debugging information
    print('Building PDS4 Python Tools...\n')
    print('OS information:\n  {0}'.format(get_system_info()))
    print('Python information:\n  {0}'.format(sys.version))
    print('PDS4 Tools version:\n  {0}'.format(get_package_version()))
    print('Log File:\n  {0}'.format(log_file))
    print('Build location:\n {0}'.format(BUILD_DIR))

    # Wait a few seconds to allow user to read the above info
    time.sleep(5)

    # Ensure BUILD_DIR exists
    _makedirs(BUILD_DIR, exists_ok=True)

    # Ensure BUILD_DIR is clean
    print('\nCleaning build location ...')
    _remove_path(os.path.join(BUILD_DIR, '*'), ignore_paths=[log_file])

    # Create the build for current OS
    build()


if __name__ == '__main__':
    main()
