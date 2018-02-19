<?php

//create SQL
$fname = "Layan2";
$lname = "shang";
$pass = "ccc";
$cell = "1234";
$loginUsername = "mshangiti";
$loginPassword = "ccc";

//$sql = "SELECT * FROM User WHERE username = '" . $username . "' AND password = '" . $password . "'";
$sql = "UPDATE User SET password = '$pass', fname='$fname', lname='$lname', cell='$cell' WHERE username = '$loginUsername' AND password = '$loginPassword' ";
//echo $sql;

//execute
$result = executeSQLUpdate($sql);

//check result
// if(count($result)>0){
// 	foreach ($result as $row) {
// 		 echo "username: " . $row["username"]. " - Pass: " . $row["password"]. " - Name: " . $row["fname"]. " " . $row["lname"]. "- cell " . $row["cell"]. "<br>";
// 	}
// }
// else{
// 	echo "ops, no matching record found.";
// }

// if(count($result)>0){
// 	$row = $result[0];
// 	echo "username: " . $row["username"]. " - Pass: " . $row["password"]. " - Name: " . $row["fname"]. " " . $row["lname"]. "- cell " . $row["cell"]. "<br>";
// }
// else{
// 	echo "ops, no matching record found.";
// }


if($result){
	echo "success";
}
else{
	echo "failed";
}
































function executeSQLUpdate($sql)
{
	$servername = "localhost";
	$username = "root";
	$password = "root";
	$dbname = "webapp";

	// Create connection
	$conn = new mysqli($servername, $username, $password, $dbname);

	// Check connection
	if ($conn->connect_error) {
	    die("Connection failed: " . $conn->connect_error);
	} 

	//execite
	$result = $conn->query($sql);

	//check if update was successful
	//$count = mysqli_affected_rows($con);
	$count = $conn->affected_rows;
	$status = false;
	if ($count > 0) {
		$status = true;
	} 

	//close connection
	$conn->close();

	return $status;
}//end of function







function executeSQLSelect($sql)
{
	$servername = "localhost";
	$username = "root";
	$password = "root";
	$dbname = "webapp";

	// Create connection
	$conn = new mysqli($servername, $username, $password, $dbname);

	// Check connection
	if ($conn->connect_error) {
	    die("Connection failed: " . $conn->connect_error);
	} 

	
	$result = $conn->query($sql);
	$data = array();

	if ($result->num_rows > 0) {
		while($row = $result->fetch_assoc()){
			$data[] = $row;
		}
	} 

	//close connection
	$conn->close();

	return $data;
}//end of function


?>