<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml"  xmlns:py="http://purl.org/kid/ns#">

<head>
<title>Web-Kickstart Tools</title>
</head>
<body>

<h1>Web-Kickstart Tools</h1>

<p>Welcome to the Web-Kickstart Tools page.  This page gives you access
to some additional tools to help you debug you config files and manage
your config files in AFS space.  If you do not have access to these tools
or otherwise feel your access permissions are in error, please send us
a note to <a href="mailto:linux@help.ncsu.edu">linux@help.ncsu.edu</a>.</p>

<p>Also, if you need assistance with any of these tools or have ideas
for future enhancments of Web-Kickstart, please open a Remedy ticket by
the above email address.</p>

<h2>Config File Debugging Or Kickstart Preview</h2>

<p>To debug your config file for a host enter the IP or FQDN of the host
in the box below.  This will show you the kickstart that will be sent
to that host when it is Web-Kickstarted.  If there is an error a
hopefully helpful message will appear.</p>

<form action="$url" method="post">
<p>IP or host name: <input type="text" name="debugtool">
<input type="submit"></p>
</form>

<h2>Collision Detection</h2>

<p>What happens when there are two or more config files for the same
host?  Well, its not good.  Enter in the the IP or FQDN of a host name
to this tool and it will report config file collisions.</p>

<?php
    
    if ( $acl ) {
        echo "<form action=\"$url\" method=\"post\">";
        echo "<p>IP or host name: <input type=\"text\" name=\"collision_detection\">";
        echo "<input type=\"submit\"></p>";
        echo "</form>";
    } else {
        echo "<p>Access to form denied.</p>";
    }

?>

<h2>Old Config Files</h2>

<p>To help folks be able to clean out old config files this tool will list
all the config files for hosts that no longer resolve in DNS.  Click the 
submit button.</p>

<?php
    
    if ( $acl ) {
        echo "<form action=\"$url\" method=\"post\">";
        echo "<input type=\"hidden\" name=\"dns_config_check\" value=\"1\">";
        echo "<input type=\"submit\">";
        echo "</form>";
    } else {
        echo "<p>Access to form denied.</p>";
    }

?>

</body>
</html>