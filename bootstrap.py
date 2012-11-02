#!/usr/bin/env python
import sys
from os import path
import tempfile
from subprocess import call, check_call, check_output, CalledProcessError, Popen, PIPE

OSX_COMMAND_LINE_TOOLS_URLS = {
    "10.8": "http://adcdownload.apple.com/Developer_Tools/command_line_tools_os_x_mountain_lion_for_xcode__october_2012/xcode451cltools_10_86938200a.dmg",
    "10.7": "http://adcdownload.apple.com/Developer_Tools/cltools_lion_from_xcode_4.5.1/xcode451cltools_10_76938201a.dmg",
    "10.6": "http://adcdownload.apple.com/Developer_Tools/command_line_tools_for_xcode_4.5_os_x_lion__september_2012/command_line_tools_for_xcode_4.5_os_x_lion.dmg",
}
VIRTUALBOX_URL = "https://www.virtualbox.org/wiki/Downloads"
VAGRANT_URL = "http://downloads.vagrantup.com/tags/v1.0.5"
NULL_FH = None


def confirm(prompt, retries=4, complaint='Please enter y or n!'):
    while True:
        ok = raw_input("%s " % prompt)
        if ok in ('y', 'ye', 'yes'):
            return True
        if ok in ('n', 'no', 'nop', 'nope'):
            return False
        retries = retries - 1
        if retries < 0:
            raise IOError('Hm. Maybe your keyboard is broken?')
        print complaint


def program_exists(program):
    try:
        p = Popen("if [ -f ~/.flintrc ]; then . ~/.flintrc; fi; export PATH=/usr/local/bin:/usr/local/sbin:/usr/local/share/python:$PATH;%s" % program, shell=True, stdout=PIPE, stderr=PIPE)
        p.communicate()
        return p.returncode == 0

    except:
        return False


def sysprint(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def verify_existance(name, cmd):
    sysprint("Checking for %s... " % name)
    if program_exists(cmd):
        print "found."
        return True
    else:
        print "not found."
        return False


def command_output(cmd):
    try:
        return Popen(cmd, shell=True, stderr=PIPE, stdout=PIPE).communicate()[1]
    except CalledProcessError, e:
        return e.output


def string_in_command_output(cmd, s):
    return "%s" % command_output(cmd)


def verify_or_install(name, cmd, install_cmd, required=True):
    if not verify_existance(name, cmd):
        sysprint("  Installing %s... " % name)
        program_exists(install_cmd)
        if not program_exists(cmd):
            sys.exit("Error installing %s.\n\nPlease run '%s' manually and fix any errors, then retry bootstrap. Sorry!\n" %
                    (name, install_cmd)
                )
        else:
            print "done."


def verify_or_brew_install(name, cmd, brew_package, required=True):
    return verify_or_install(name, cmd, 'brew install %s' % brew_package)


def verify_or_gem_install(name, cmd, gem_package, required=True):
    return verify_or_install(name, cmd, 'gem install %s' % gem_package)


def verify_or_pip_install(name, cmd, pip_package, required=True):
    return verify_or_install(name, cmd, '/usr/local/bin/pip install %s' % pip_package)


def pip_install(package, package_name=None, required=True):
    if not package_name:
        package_name = package
    sysprint("Installing %s... " % package_name)

    try:
        program_exists('/usr/local/bin/pip install %s' % package)
    except:
        sys.exit("Error installing %s.\n\nPlease '/usr/local/bin/pip install %s' manually and fix any errors, then retry bootstrap. Sorry!\n" %
            (package_name, package)
        )
    print "done."


def ensure_file_contains_wrapped_fragment(filename, header, content, footer):
    if path.isfile(filename):
        mode = "r+"
    else:
        mode = "w+"
    with open(filename, mode) as f:
        contents = "%s" % f.read()
        if header in contents and footer in contents:
            old_header = "%s" % contents[:contents.find(header) + len(header)]
            old_footer = "%s" % contents[contents.find(footer):]
            new_contents = old_header
            new_contents += content
            new_contents += old_footer
        else:
                new_contents = contents
                new_contents += header
                new_contents += content
                new_contents += footer
        f.seek(0)
        f.truncate(0)
        f.write(new_contents)
        f.close()


def main(args=sys.argv):
    global NULL_FH
    NULL_FH = open("/dev/null", "w")
    TEMP_DIR = tempfile.mkdtemp()

    print """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX IXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX   RXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX     VXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX       ;XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXV         ,XXYXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX,           .XX ,XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXi              ,XX  .XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXX.                +XV   ,XXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXYXV                   VX=    tXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXY XX                     XR     :XXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXX, ;X=                     IX;     .XXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXV   IX                       XV      ,XXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXY    YX                       XR       iXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXX     +X:                      VX        XXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXX.     .XY                      YX        tXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXX       YX                      VR        ;XXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXI        XY                     XX        :XXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXY        =X:                   .X;        tXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXX         YX                   YR         XXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXX=         VX                  X:        VXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXX.         XV                VY        VXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXX,         VV              =X       ,XXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXi         IV             R       IXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXX;        +X           X      +XXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXX;       .X         X     =XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXIYXXXXXXXXXXV:      Y.      V   .IXXXXXXXXXXIt=.YXXXXXXXXXXXXXXXX
XXXXXXXXXXXY       :tIXXXXXXX;    ::    I  ;XXXXXXVI+         YXXXXXXXXXXXXXXX
XXXXXXXXXXX               tIXXXXY:  =  ::XXXXYt                RXXXXXXXXXXXXXX
XXXXXXXXXXi                     +IVXRYRVI;                     IXXXXXXXXXXXXXX
XXXXXXXXXX=                                               .,tRXXXXXXXXXXXXXXXX
XXXXXXXXXXX,,                                        ,;XXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXR   ,,,,                            =YYXXXXX .RXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXVXXVi                                        VVXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXVi                                                =XXXXXXXXXXXXX
XXXXXXXXXXXX:                   :RXXXXXXX:                      +XXXXXXXXXXXXX
XXXXXXXXXXXXt             .YRXXXXXXXXXXXXXXXXXX:                RXXXXXXXXXXXXX
XXXXXXXXXXXXX.       +RXXXXXXXXXXXXXXXXXXXXXXXXXXXXXV,         VXXXXXXXXXXXXXX
XXXXXXXXXXXXXX,=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXRY   YXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
"""

    ### Sanity check dev tools, etc installed. ###
    print """
##############################################################################
############                  System Dev Tools                    ############
##############################################################################"""

    IS_A_MAC = False
    MAC_OS_VERSION = check_output("sw_vers | grep 'ProductVersion:' | grep -o '[0-9]*\.[0-9]*\.[0-9]*'", shell=True).replace("\n", "")
    if "command not found" in MAC_OS_VERSION:
        MAC_OS_VERSION = None
        IS_A_MAC = False
        print "Looks like you're not using a Mac.  Flint doesn't support bootstrapping non-macs quite yet, but we'll give it a shot."
    else:
        IS_A_MAC = True
        # BASE_MAC_OS_VERSION = MAC_OS_VERSION[:MAC_OS_VERSION.rfind(".")]
        print "Detected Mac OS %s." % MAC_OS_VERSION

        # See if we have the developer tools installed.
        sysprint("Checking for the developer tools or xCode... ")
        while not program_exists("gcc -v") or not program_exists("make -v"):
            print "not found."

            # Download the dev tools, open the instaaller.
            print "\nPlease download and install the latest Mac OS X Command Line Tools (or XCode)."
            raw_input("Press any key to open the website for download... ")
            call("open https://developer.apple.com/downloads", shell=True)

            # cmd = call("curl -#o ~/Desktop/devtools.dmg %s" % OSX_COMMAND_LINE_TOOLS_URLS[BASE_MAC_OS_VERSION], shell=True)
            print ""
            raw_input("Press any key to continue when you're done installing the command line tools..")
            sysprint("\nChecking for the developer tools or xCode... ")
        else:
            print "found."
        print "System dev tools look good!"

    if IS_A_MAC:
        # if we have brew, just run update
        print """
##############################################################################
############                      Homebrew                        ############
##############################################################################"""

        if not verify_existance("homebrew", "brew -v"):
            sysprint("Installing homebrew...")
            call('ruby -e "$(curl -fsSkL raw.github.com/mxcl/homebrew/go)"', shell=True, stdout=NULL_FH, stderr=NULL_FH)
            print "done."

        # Update homebrew
        sysprint("Updating homebrew... ")
        if call("brew update", shell=True, stdout=NULL_FH, stderr=NULL_FH) == 0:
            print "done."
        else:
            sys.exit("Error updating homebrew.\n\nPlease run 'brew update' manually and fix any errors, then retry bootstrap. Sorry!\n")

        print "Homebrew looks good!"

        print """
##############################################################################
############                      Virtualbox                      ############
##############################################################################"""

        while not verify_existance("Virtualbox", "ls /Applications/Virtualbox.app"):

            # Download the dev tools, open the instaaller.
            print "\nPlease download and install the latest version of Virtualbox."
            raw_input("Press any key to open the website for download... ")
            call("open %s" % (VIRTUALBOX_URL,), shell=True)

            # cmd = call("curl -#o ~/Desktop/devtools.dmg %s" % OSX_COMMAND_LINE_TOOLS_URLS[BASE_MAC_OS_VERSION], shell=True)
            print ""
            raw_input("Press any key to continue when you're done installing virtualbox..")

        print "Virtualbox looks good!"

    # No longer mac-only.
    print """
##############################################################################
############                       Vagrant                        ############
##############################################################################"""

    verify_or_gem_install("Vagrant", "vagrant", "vagrant")

 # if we have brew, just run update
    print """
##############################################################################
############                     Github Auth                      ############
##############################################################################"""

    # Verify that you have access to github.
    sysprint("Verifying your SSH key on github... ")
    while not string_in_command_output('ssh -q -o "StrictHostKeyChecking no" -T git@github.com', "successfully authenticated"):
        print "failed."
        print "\nYour ssh keys have either not been set up on this machine or configured with github."

        raw_input("Please setup your ssh keys and press any key to try again.")
        print ""
        sysprint("Verifying your SSH key on github... ")

    ssh_check = command_output('ssh -q -o "StrictHostKeyChecking no" -T git@github.com')
    GITHUB_USERNAME = ssh_check[ssh_check.find(" ") + 1:ssh_check.find("!")]
    print "verified as %s." % (GITHUB_USERNAME,)

    # Verify that you've been added to the Building Energy dev team.
    sysprint("Verifying you have access to the Building Enegy repos... ")
    while string_in_command_output("git clone git+ssh://git@github.com/buildingenergy/flint.git %s/flint.git" % TEMP_DIR, "Permission denied"):
        print "failed."
        print "\nYour github user does not appear to be in the Building Energy developer team."

        raw_input("Please get someone to add you to the team, and try again.")

    print "verified."
    call("rm -rf %s/flint.git" % TEMP_DIR, shell=True, stdout=NULL_FH, stderr=NULL_FH)

 # if we have brew, just run update
    print """
##############################################################################
############                   Core Packages                      ############
##############################################################################"""
    #### Install python2.7 ####
    verify_or_brew_install("Python 2.7", "/usr/local/bin/python2.7 --version", "python")

    #### Install pip ####
    verify_or_install("pip", "/usr/local/bin/pip --version", "/usr/local/bin/easy_install-2.7 pip")
    verify_or_install("readline", "/usr/local/bin/python2.7 -c 'import readline'", "/usr/local/bin/easy_install-2.7 readline")

    # install virtualenv / virtualenvwrapper
    pip_install("virtualenv")
    pip_install("virtualenvwrapper")

    # make .virtualenvs
    if not program_exists("ls ~/.virtualenvs"):
        sysprint("Creating .virtualenv folder... ")
        call("mkdir ~/.virtualenvs", shell=True, stdout=NULL_FH, stderr=NULL_FH)
        print "done."

    verify_or_brew_install("Git", "/usr/local/bin/git --version", "git")
    verify_or_brew_install("Git-flow plugin", "git-flow version", "git-flow")
    verify_or_brew_install("Git autocomplete", "ls `brew --prefix`/etc/bash_completion", "bash-completion")

    #### Install flint ####
    verify_or_pip_install("Flint", "/usr/local/share/python/use_flint", "git+ssh://git@github.com/buildingenergy/flint.git#egg=flint -q --upgrade")

    # set up /etc/hosts
    # sysprint("Setting up /etc/hosts for be.com")
    # print "done."

    # Update the bash profile.
    sysprint("Adding homebrew paths and virtualenv to your .bash_profile... ")
    profile_header = "\n#### Start BE config ####\n"
    bash_content = ". ~/.flintrc\n"
    profile_content = """alias kill_pyc="find . -name '*.pyc' -delete"
export BE_BOOTSTRAP_VERSION=1.1
export PATH=/usr/local/bin:/usr/local/sbin:/usr/local/share/python:$PATH
if [ -f /usr/local/share/python/virtualenvwrapper.sh ]; then
    source /usr/local/share/python/virtualenvwrapper.sh
fi
source /usr/local/etc/flint/flint_wrapper.sh
source /usr/local/etc/flint/flint_autocompletion.sh
if [ -f `brew --prefix`/etc/bash_completion ]; then
    . `brew --prefix`/etc/bash_completion
fi
source /usr/local/etc/bash_completion.d/git-flow-completion.bash
"""
    profile_footer = "#### End BE config ####\n"
    try:
        ensure_file_contains_wrapped_fragment(
            path.join(path.expanduser("~"), ".flintrc"),
            profile_header,
            profile_content,
            profile_footer
        )
    except:
        import traceback
        traceback.print_exc()
        print "failed."
        print "Unable to create the ~/.flintrc file. Please create a .flintrc file in your home directory and run bootstrap again."
        print "\n%s\n" % profile_content
    try:
        ensure_file_contains_wrapped_fragment(
            path.join(path.expanduser("~"), ".bash_profile"),
            profile_header,
            bash_content,
            profile_footer
        )
        print "done."
    except:
        from traceback import print_exc
        print_exc()
        print "failed."
        print "Unable to automatically add to your .bash_profle. Please add the following to your shell .rc file of choice."
        print "\n%s\n" % profile_content

    # Do you want to install sublime packages?
    if confirm("Would you like to have some useful sublime plugins installed (Linter, codeIntel, etc?) (y/n)"):
        sub_dir = "~/Library/Application\ Support/Sublime\ Text\ 2/Packages"
        verify_or_install("Sublime CodeIntel", "ls %s/SublimeCodeIntel/*" % sub_dir, "git clone git://github.com/Kronuz/SublimeCodeIntel.git %s/SublimeCodeIntel" % sub_dir)
        verify_or_install("Sublime Linter", "ls %s/SublimeLinter/*" % sub_dir, "git clone git://github.com/SublimeLinter/SublimeLinter.git %s/SublimeLinter" % sub_dir)
        verify_or_install("Cucumber Syntax", "ls %s/Cucumber/*" % sub_dir, "git clone git://github.com/npverni/cucumber-sublime2-bundle.git %s/Cucumber" % sub_dir)
        verify_or_install("Django Syntax", "ls %s/Djaneiro/*" % sub_dir, "git clone git://github.com/squ1b3r/Djaneiro.git %s/Djaneiro" % sub_dir)
        verify_or_install("HTML5 Syntax", "ls %s/HTML5/*" % sub_dir, "git clone git://github.com/mrmartineau/HTML5.git %s/HTML5" % sub_dir)
        verify_or_install("Package Control", "ls %s/Package\ Control.sublime-package" % sub_dir, "curl http://sublime.wbond.net/Package%%20Control.sublime-package -so %s/Package\ Control.sublime-package" % sub_dir)

    print """

##############################################################################
############                Bootstrap Complete!                   ############
##############################################################################

You can now use flint to work on our codebase.
To get started, just type:

flint help

Have fun!
"""

    #### Flint pitch-camp ####

    NULL_FH.close()

if __name__ == '__main__':
    main()
