<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'swimaster.kid'">
<head>
	<link rel="stylesheet" type="text/css" href="/static/css/style2.css"></link>
	<link rel="stylesheet" type="text/css" href="/static/css/lasvegastoo.css"></link>
	<link rel="stylesheet" type="text/css" href="/static/css/webadmin.css"></link>
	<link rel="stylesheet" type="text/css" href="/static/css/tform.css"></link>
	<title>SPADE WebAdmin Tool</title>
</head>
<body>
	<div id="content">
		<div id="posts">
			<div class="post">
				<div id="status_block" class="flash" py:if="value_of('tg_flash', None)" py:content="tg_flash"></div>
			</div>
			<div class="post">
				<h2 class="title">Main Control Panel</h2>
				<div class="meta">
				</div>
				<div class="story">
					<table><tr><td>
		            	<table class="titulo"><tr><td colspan="2">Server Configuration</td></tr></table>
		                <table class="linea"><tr><td>Agent Platform address:</td><td class="der"><span py:replace="servername">#SERVERNAME#</span></td></tr></table>
		                <table class="linea"><tr><td>System Platform:</td><td class="der"><span py:replace="platform">#PLATFORM#</span></td></tr></table>
		                <table class="linea"><tr><td>Python Version:</td><td class="der"><span py:replace="version">#PYTHONVERSION#</span></td></tr></table>
		                <table class="linea"><tr><td>Server Time:</td><td class="der"><span py:replace="time">#TIME#</span></td></tr></table>
		                <table class="linea"><tr><td>Restart Platform:</td><td class="der">
		                	<form action="/restart" method="POST"><input type="hidden" name="restart" value="true"></input>
		                		<input type="submit" value="Restart"></input></form></td></tr></table>
		            </td></tr></table>
					
				</div>
			</div>
		</div>
	</div>
</body>
</html>