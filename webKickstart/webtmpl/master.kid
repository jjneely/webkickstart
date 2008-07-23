<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml"  xmlns:py="http://purl.org/kid/ns#">

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'">
  <title>Web-Kickstart Tools</title>

  <link rel="stylesheet" type="text/css" 
    href="static/css/navbar.css" /> 
  <link rel="stylesheet" type="text/css" 
    href="static/css/common.css" /> 

  <meta py:replace="item[:]" />

</head>
<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'">

<div class="oitnavbar">
  <div class="oit_logo">
      <a href="http://oit.ncsu.edu/"><img alt="OIT Web Site"
          src="static/oit_logo_cartoon_30.png"/></a></div>
  <div class="ncsu_brick">
      <a href="http://www.ncsu.edu/"><img src="static/brick_black.gif"
          alt="NC State University"/></a></div>
  <div class="oitcontainer">
    <ul>
      <li><a href="http://oit.ncsu.edu">Office of Information Technology</a>
        &nbsp;|&nbsp;</li>
      <li><a href="http://sysnews.ncsu.edu">SysNews</a>
        &nbsp;|&nbsp;</li>
      <li><a href="http://www.linux.ncsu.edu">Campus Linux Services</a>
        &nbsp;|&nbsp;</li>
      <li><a href="http://help.ncsu.edu">NC State Help Desk</a></li>
    </ul>
  </div>
</div>

  <ul class="makemenu">
    <li class="title">Liquid Dragon Menu</li>
    <li><a href="index">Front Page</a></li>
    <li><a href="http://web-kickstart.linux.ncsu.edu">Web-Kickstart</a></li>
    <li><a href="https://secure.linux.ncsu.edu/rlmtools">
        Realm Linux Management Tools</a></li>
    <li py:for="name, href in value_of('backlinks', [])">
      <a href="" py:attrs="'href':href" py:content="name">Backwards</a>
    </li>
  </ul>

  <div class="content">

  <h1>Web-Kickstart Tools</h1>

  <div py:content="item[:]" />

  </div>

  <p><font size="-1"><i>Part of the Liquid Dragon project.</i></font></p>

</body>

</html>

