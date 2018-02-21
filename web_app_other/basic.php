<?php
	# Variables are created on the fly
	$x = 'Hello';
	$y = 'World';
	
	# For GET Method; GET is array built as result of apache parsing GET request and breaking down data. Passes to PHP interpreter. Reads data from URL and puts into GET Array
	$name = $_GET['username']; # THIS CAN BE USED FOR XSS
	# ex. 127.0.0.1/basic.php?username=Steve<script>{insert malicious javascript code}</script>
	
	$name = $_POST['username'];
	$ip = $_SERVER['REMOTE_HOST']; # Way to access headers
	
	echo $ip;
	
	# 'echo' Writes Output; '.' concatenates 
	# Any HTLM has to be written as static output
	echo "<b>".$x . "</b>" . " " . $name;
	

?>



<form action="basic.php" method="POST">
	<input type="text" id="username"/> <!-- id must match array index -->
	<input type="submit" />
</form>