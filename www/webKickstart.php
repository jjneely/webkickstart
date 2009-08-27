<html>
<head>
<title>Jump Start for the Linux Realm Kit</title>
</head>
<body>

<h1>Jump Start for the Linux Realm Kit</h1>

<p>Red Hat Linux uses an automated install system known as Kickstart.
Very basically, this is a detailed text file that the Red Hat Linux
installer can retrieve and use to install the machine rather than
asking the a human many questions.  One of the most powerful methods
of delivering a kickstart file to the installer is by HTTP which
allows complex scripting to generate the proper kickstart file.  This
is what we are doing here.</p>

<p>Sun Solaris uses a similar system called JumpStart to perform automated
installs. An advantage of JumpStart is that its' format is already
familiar to those that do Solaris installs, and JumpStart configuration
files are often significantly simpler than Kickstart files. To leverage
our Jumpstart knowledge, we decided to use the JumpStart file format and
convert it to the equivalent Kickstart format, which would then be used
to perform the install via HTTP.</p>

<p>Maintained by <a href="mailto:linux@help.ncsu.edu">NCSU CLS</a>.</p>

<h2>Documentation</h2>

<p>Web-Kickstart is designed to install <a
href="http://www.linux.ncsu.edu/realmkit">Realm Linux</a>
from a simple config file.  This config file is used to
dynamically create a Red Hat Kickstart to do the install.
The filename of the config files must be the fully quantified domain
name of the machine you want to install.  Files must be placed under the 
following directory:</p>
 
<tt>/afs/bp/system/config/linux-kickstart/configs</tt>.

<p><b>Note:</b> In addition to the jump start config file, the computers' DNS
entry must be  configured to use DHCP and the IP address received from
DHCP must resolve to a domain name.</p>

<p>A full description of all possible key words and what they do can be
found in <a href="docs/keywords.txt">keywords.txt</a>.</p>

<p>Currently, the following products are supported:</p>

<table align="center" border="1" cellspacing="0" cellpadding="3">
<tr><th>Product</th><th>Version Key</th><th>Status</th></tr>
<tr><th colspan="3">Production Products</th></tr>
<tr><td>Realm Linux 5.3 Server (x86_64)</td><td>server5.x86_64</td><td>Production</td></tr>
<tr><td>Realm Linux 5.3 Server (i386)</td><td>server5</td><td>Production</td></tr>
<tr><td>Realm Linux 5.3 Client (x86_64)</td><td>client5.x86_64</td><td>Production</td></tr>
<tr><td>Realm Linux 5.3 Client (i386)</td><td>client5</td><td>Production</td></tr>

<tr><td>Realm Linux WS4 U6 (i386)</td><td>WS4</td><td>Production</td></tr>
<tr><td>Realm Linux AS4 U6 (i386)</td><td>AS4</td><td>Production</td></tr>
<tr><td>Realm Linux WS4 U6 (AMD64/EM64T)</td><td>WS4.x86_64</td><td>Production</td></tr>
<tr><td>Realm Linux AS4 U6 (AMD64/EM64T)</td><td>AS4.x86_64</td><td>Production</td></tr>

<tr><th colspan="3">Non-Production and Testing Products</th></tr>

<tr><td>Realm Linux WS4 U8 (i386)</td><td>WS4.8</td><td>Beta</td></tr>
<tr><td>Realm Linux AS4 U8 (i386)</td><td>AS4.8</td><td>Beta</td></tr>
<tr><td>Realm Linux WS4 U8 (AMD64/EM64T)</td><td>WS4.8.x86_64</td><td>Beta</td></tr>
<tr><td>Realm Linux AS4 U8 (AMD64/EM64T)</td><td>AS4.8.x86_64</td><td>Beta</td></tr>

<tr><th colspan="3">End of Life Products</th></tr>
<tr><td>Realm Linux AS3 U8 (i386)</td><td>AS3.8</td><td>Production - EOL 1/1/2007</td></tr>
<tr><td>Realm Linux WS3 U4 (i386)</td><td>WS3</td><td>Production - EOL 1/1/2007</td></tr>
<tr><td>Realm Linux AS3 U4 (i386)</td><td>AS3</td><td>Production - EOL 1/1/2007</td></tr>
</table>

<h2>Examples and More Documentation.</h2>
<ul>
<li><a href="docs/keywords.txt">keywords.txt</a> - Keywords and
syntax for the Realm Linux JumpStart files.</li>
<!--<li><a href="docs/design.txt">design.txt</a> - A rough design
document.</li>-->
</ul>

<h2>Disk Image</h2>
<p>Here's a disk image that is set up to automatically do a
kickstart install from web-kickstart.linux.ncsu.edu.  (This was done
by modifying the syslinux.cfg file on the floppy.  After you setup
your config file all you need to do is boot off of one of these
disks to install the machine.  This boot disk you use must match
the version of Realm Linux you have the config file set to install.</p>

<h3>Production Products</h3>

<h4>Realm Linux 5.3</h4>
<ul>
<li><a href="server-5.3-x86_64-webks.iso">server-5.3-x86_64-webks.iso</a> - Realm Linux 5.3 Server for x86_64</li>
<li><a href="server-5.3-x86-webks.iso">server-5.3-x86-webks.iso</a> - Realm Linux 5.3 Server for i386</li>
<li><a href="client-5.3-x86_64-webks.iso">client-5.3-x86_64-webks.iso</a> - Realm Linux 5.3 Client for x86_64</li>
<li><a href="client-5.3-x86-webks.iso">client-5.3-x86-webks.iso</a> - Realm Linux 5.3 Client for i386</li>
</ul>

<h4>Realm Linux 4.6</h4>
<ul>
<li><a href="RHEL4-U6-x86-webks.iso">RHEL4-U6-x86-webks.iso</a> - Realm Linux AS/WS 4 U6 (Beta) Boot CD (Server and Workstation) for i386</li>
<li><a href="RHEL4-U6-x86_64-webks.iso">RHEL4-U6-x86_64-webks.iso</a> - Realm Linux AS/WS 4 U6 (Beta) Boot CD (Server and Workstation) for x86_64/EM64T</li>
</ul>

<h3>Non-Production and Testing Products</h3>

<h4>Realm Linux 5.1 - Retired</h4>
<ul>
<li><a href="server5-U1-x86_64-webks.iso">server5-U1-x86_64-webks.iso</a> - Realm Linux 5.1 Server for x86_64</li>
<li><a href="server5-U1-x86-webks.iso">server5-U1-x86-webks.iso</a> - Realm Linux 5.1 Server for i386</li>
<li><a href="client5-U1-x86_64-webks.iso">client5-U1-x86_64-webks.iso</a> - Realm Linux 5.1 Client for x86_64</li>
<li><a href="client5-U1-x86-webks.iso">client5-U1-x86-webks.iso</a> - Realm Linux 5.1 Client for i386</li>
</ul>

<h4>Realm Linux 5.0 - Retired</h4>
<ul>
<li><a href="server5-U0-x86_64-webks.iso">server5-U0-x86_64-webks.iso</a> - Realm Linux 5.0 Server for x86_64 (Production)</li>
<li><a href="server5-U0-x86-webks.iso">server5-U0-x86-webks.iso</a> - Realm Linux 5.0 Server for i386 (Production)</li>
<li><a href="client5-U0-x86_64-webks.iso">client5-U0-x86_64-webks.iso</a> - Realm Linux 5.0 Client for x86_64 (Production)</li>
<li><a href="client5-U0-x86-webks.iso">client5-U0-x86-webks.iso</a> - Realm Linux 5.0 Client for i386 (Production)</li>
</ul>

<h4>Realm Linux 4.4 - Retired</h4>
<ul>
<li><a href="RHEL4-U4-x86-webks.iso">RHEL4-U4-x86-webks.iso</a> - Realm Linux AS/WS 4 U4 (Production) Boot CD (Server and Workstation) for i386</li>
<li><a href="RHEL4-U4-x86_64-webks.iso">RHEL4-U4-x86_64-webks.iso</a> - Realm Linux AS/WS 4 U4 (Production) Boot CD (Server and Workstation) for x86_64/EM64T</li>
</ul>

<h3>End of Life Products</h3>

<h4>Realm Linux 3 (Retired)</h4>
<ul>
<li><a href="RHEL3-U8-x86-webks.iso">RHEL3-U8-x86-webks.iso</a> - Realm Linux AS 3 U8 (Retired) Boot CD (AS Only)  for i386</li>
<li><a href="RHELU4-x86-webks.iso">RHEL3-U4-x86-webks.iso</a> - Realm Linux AS/WS 3 U4 (Retired) Boot CD (Server and Workstation) for i386</li>
</ul>

<h3>Web-Kickstart Tools</h3>

<p>There are several Web-Kickstart Tools available to help you debug
your config files and manage your config files in AFS.  You can view the
kickstart that is generated and sent to your machines and check for
syntax and other errors.  All of these Tools can be found at the:

<ul><li><a href="https://secure.linux.ncsu.edu/webKickstartTools">Web-Kickstart Tools Page</a></li></ul>

This page is SSL'd and WRAP protected for security reasons.</p>

<h3>When Things Go Wrong</h3>

<p>There are several common things that can keep Web-Kickstart from installing
your machine for you.  If the install process starts asking you questions,
like what language to use, then the client didn't receive the kickstart 
from the Web-Kickstart server and is defaulting to a manual install.
Possible causes and solutions:</p>

<ul>
<li>Reboot the machine and try again.</li>
<li>Is the IP of the machine configured for Manual DHCP in QIP?</li>
<li>Does the IP reverse resolve to the domain name yet?</li>
<li>Does the file name exactly match the string that the IP address
reverse resolves too?  It is case sensitive.</li>
</ul>

<p>Another common trouble point is that the installer complains that it
cannot download <tt>stage2.img</tt> at the beginning of the install.
This means that you are using a boot disk for a different version of
Realm Linux compared to what the <tt>version</tt> key says in the 
config file.</p>

<h3>Recent Changes</h3>

<p>The following are some recent changes to the system there were made
after I released it to public testing.  These changes are also
documented in the <a href="docs/keywords.txt">keywords.txt</a> file or
their relivant place.</p>

<p>The <a href="changelog.php">Change Log</a> has grown quite a bit so 
I've moved it to its own page.
Please keep up with the systems as it grows and changes.</p>

<h2>References</h2>

<p>The follow collection of links points to documentation and resources
that you may find useful but are not directly related to setting up a
JumpStart config file for Realm Linux.</p>

<ul>
<li><a href="http://www.redhat.com/docs/manuals/enterprise/RHEL-5-manual/Installation_Guide-en-US/ch-kickstart2.html">Red Hat Enterprise Linux 5 Kickstart Documentation</a></li>
<li><a href="http://www.redhat.com/docs/manuals/enterprise/RHEL-5-manual/Installation_Guide-en-US/s1-kickstart2-options.html">Red Hat Enterprise Linux 5 Kickstart Options</a></li>
<li><a href="http://www.redhat.com/docs/manuals/enterprise/RHEL-4-Manual/sysadmin-guide/ch-kickstart2.html">Red
Hat Enterprise Linux 4 Kickstart Documentation</li>
<li><a
href="http://www.redhat.com/docs/manuals/enterprise/RHEL-4-Manual/sysadmin-guide/s1-kickstart2-options.html">
Red Hat Enterprise Linux 4 Kickstart Options</li>
</ul>

</body>
</html>
