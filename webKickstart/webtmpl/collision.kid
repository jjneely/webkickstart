<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
  py:extends="'master.kid'">

<head>
<title>Web-Kickstart Tools</title>

</head>
<body>

  <p>This page will alert you if there are colliding configurations
    present for the below host.</p>

  <h2>Host: <span py:replace="host"/></h2>

  <div class="code">
    <pre py:content="output"/>
  </div>

</body>
</html>

