<html>
<head>
<title>WebKickstart Change Log</title>
</head>
<body>

<h1>WebKickstart Change Log</h1>

<ul>
<li>Glaring bugs in the check.py script are fixed.</li>
<li>The docs for the 'use' keyword have been cleared up a bit.  Need
to be carefull about current directories and paths.</li>
<li>Implemented including scripts in the config files after a '%post'
key.  See the examples above.</li>
<li>Completely changed how mouse configuration is done.  This now
works with all types of mice that the Red Hat Kickstart stuff knows
of.  See the docs.</li>
<li>Added support for the 8.0 RK.  The version string is "8.0".</li>
<li>02/14/03 - 
Moved the Debug Tool to a WRAP'd directory that's served from 
secure.linux.ncsu.edu to protect the information while you are debuging.</li>
<li>02/14/03 - 
We do not send a default kickstart anymore if there is no config
file.  You must have a config file.</li>
<li>02/14/03 - 
Moved to permanent location in AFS.</li>
<li>04/14/03 - 
Added support for the NCSU Realm Kit for Red Hat Linux 9 AKA Shreak.  The
version string is "9".</li>
<li>04/24/03 -
Added RK 9 boot CD.</li>
<li>05/08/03 -
Added "enable safepartition" key and changed the default size of /var/cache
to 512MB, /var to 390 and /boot to 75.  I've also added a new option to the src key and changed the
default to that option of "http" which installs from install.linux.ncsu.edu.</li>
<li>06/05/03 -
Added "enable keepmbr" which doesn't overwrite the MBR with the bootloader.
The bootloader is placed in the boot partition (/boot).</li>
<li>06/20/03 -
Implemented "owner" key.  Fixed % handling so that anything after a line
beginning with "%" is included, including that % line.  This makes adding
%post, %pre, etc a bit more useful as you can pass options to them.  Fixed 
case where the use keyword is used more than once.  Fixed the growing URL problem when the Reinstall Workstation boot option is used.</li>
<li>08/26/03 -
RAID and LVM support for versions 9 and higher.  The part, raid, volgroup,
and logvol keys are all used just as you would use them in a Red Hat
Kickstart.  An example provided.</li>
<li>09/02/03 -
Check for and only serve a kickstart to Anaconda not just any HTTP client.
Web-kickstart installs are now logged into a MySQL database.</li>
<li>09/09/03 -
The functionality of the 'users' keyword has been changed.  Currently,
using this keyword will do nothing.  To specify additional admin users
you should now use the 'enable adminusers [user[, user ... ]]' key.  The
'users' key will be changed to behave identically to the Solaris version
RSN.  Also, there is now no way to override pulling an admin user list
from AFS, but 'enable adminusers' will add to this list.</li>
<li>10/10/03 -
Changed the 'root' key to 'rootpw'.  The root key will have new functionality
similar to that of the Solaris config files in the future.  </li>
<li>11/21/03 -
Added support for Realm Linux FC1.  The version string to use is "FC1"
</li>
<li>12/31/03 -
Fixed #286 which makes the 'use' keyword much more saner.  Top level configs
override included configs and top level %posts come after included %posts.
Also changed the system so that admin users and root passwords are pulled
from Jeff's "new" update system.  See /afs/bp/system/common/update/.
</li>
<li>3/8/04 -
Fixed #296 which adds the key 'enable staticip' to configure a client
with a static IP address rather than DHCP.  See the documentation
for exact usage.  Note that web-kickstart will requires DHCP to get
the kickstart to the client.</li>
<li>3/29/04 -
Got some great feedback from a user about the web page and documentation.
The web page and docs were updated to try to make them more user
friendly.</li>
<li>3/31/04 -
Added support for Realm Linux WS3.  Use 'WS3' for the version string.</li>
<li>4/20/04 -
Added <i>enable activationkey &lt;key&gt;</i>.  This allows you to use
a non-default RHN activation key to register RHEL-based systems.</li>
<li>4/23/04 -
Added a call to up2date for RHEL.  This installs all updates to the system
during post-install rather than having to wait until the nightly cron 
job.</li>
<li>05/12/04 -
Ported some bugfixes and improvements from the devel branch to stable.
This fixes usage problems with raid and LVM associated keys.</li>
<li>05/16/04 - 
Merged changes from stable branch to head. Added "firewall" keyword that works 
just like Red Hat's kickstart and "enable nofirewall" which disables the 
firewall all together.</li>
<li>05/21/04 -
Added extra code for RHEL based Realm Linux to configure Up2Date more
completely.  Also made the Grub reinstall trick a bit smarter so that one
can provide the vmlinuz and initrd.img files in a different manager.</li>
<li>06/25/04 -
User/Password update scripts in AFS were removing the admin users added by
'enable adminusers' is fixed by also dropping the user IDs in users.local.base
and .k5login.base.  Also, the 'cluster' keyword now works via the
update.conf file to control login cluster via PTS groups.</li>
<li>06/25/04 -
Fixed bug that was appearing as duplicated output in the update.conf files
and generated kickstarts.</li>
<li>07/23/04 -
A similar bug that was causing the loss of admin users added by 'enable 
adminusers' was also affecting 'enable normalusers'. </li>
<li>09/02/04 -
Added support for Realm Linux FC2.</li>
<li>09/29/04 -
Added the 'xconfig' key to configure X settings from the config file.  Also
release version 20040929.</li>
<li>05/20/05 - 
Changed default size for the / partition to 8GB.</li>
<li>05/20/05 -
add "enable audit" keyword and disable auditd by default.</li>
<li>06/28/05 -
Add support for selinux.  You may use the <tt>selinux</tt> keyword
exactly as documented in Red Hat's Kickstart Options docs.</li>
<li>06/28/05 - 
Add support for detection of machines that no longer resolve in dns</li>
<li>06/28/05 - 
Renamed Specifix to rpath</li>
<li>06/28/05 - 
Add support to turn case sensitivity on/off for version strings</li>
<li>07/06/05 -
Made collision support actually work.  Lots of random updates, fixes,
and web page updates.</li>
<li>05/01/06 -
    <ul>
    <li>Web-Kickstart will set the ksdevice for the re-install target in Grub
to the same ksdevice used to do the inital install.</li>
    <li>Various typos and small differences between RHEL 3 and 4 are corrected.</li>
    <li>Remove the need
for the configs/ symlink, all non-absoulte paths given to the 'use' key
are now relative to the top level config directory and should no longer
start with "config/".  </li>
    <li>Gard against infinite recursion.</li>
    <li>Web-Kickstart
errors no longer generate a traceback, just the error message.  Non-
handled errors still produce a traceback.</li>
    <li>The 'clearpart' key from
the Kickstart documentation is now supported.</li>
    <li>Force the name of the RHN Profile to be the FQDN of the host.</li>
    </ul>
</li>
<li>06/02/06 -
Added the <tt>staticip</tt> keyword.  This adds a script to convert
an installed client to use a static IP setup rather than DHCP.  Usefull
for servers.</li>
<li>06/05/06 -
If a reverse DNS query returns a host name with capital letters Web-Kickstart
will look for a matching file in a case-insensitive manner.</li>
<li>07/03/06 -
In certain cases Web-Kickstart could not find the version key in the config
file.  This bug was corrected.</li>
<li>07/03/06 -
Implement a logging mechanism.</li>
<li>10/11/06 -
Corrected a logic error that was preventing the incorperation of certain
keys in files that were included with 'use.'</li>
<li>11/02/06 -
Changed the 'staticip' key word to use the KSDEVICE rather than a hard
coded "eth0."  I also moved the KSDEVICE variable declaration to the
top of the post so that other bits could use the variable as well.</li>
<li>04/11/07 - Realm Linux 5 Support
<ul>
    <li>Added the following keywords: cmdline, ignoredisk, key, multipath, 
        repo, vnc</li>
    <li>Added support for defining Red Hat INs in the configuration for
        each version tag</li>
    <li>Added support for defining additional repos (via the repo Kickstart
        option) in the configuration per version</li>
    <li>5 has SELinux disabled by default</li>
    <li>5 treats package groups differently, but Web-Kickstart will
        still use the same Realm Linux groups</li>
    <li>Other misc kickstart syntax changes</li>
    <li>Reworked software so that Web-Kickstart acts as a python package</li>
</ul>

</ul>

</body>
</html>

