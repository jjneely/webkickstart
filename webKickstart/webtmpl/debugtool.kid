<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
  py:extends="'master.kid'">

<head>
<title>Web-Kickstart Tools</title>

</head>
<body>

  <p>This page processes the WebKickstart config for the below host.  It will display any errors that may be present or the generated Red Hat Kickstart as it will be sent to the host.</p>

  <h2>Host: <span py:replace="host"/></h2>

  <div class="code">
    <pre py:content="kickstart"/>
  </div>

</body>
</html>

