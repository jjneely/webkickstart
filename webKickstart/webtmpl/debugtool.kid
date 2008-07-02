<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml"  xmlns:py="http://purl.org/kid/ns#">

<head>
<title>Web-Kickstart Tools</title>

<style type="text/css">
div.code {
    background-color: #dddddd;
    padding: 0.5em;
    border: 1px solid #000000;
    overflow: auto;
}

</style>

</head>
<body>

  <h1>WebKickstart: Debug View</h1>

  <p><b>Host: </b><span py:replace="host"/></p>

  <div class="code">
    <pre py:content="kickstart"/>
  </div>

</body>
</html>

