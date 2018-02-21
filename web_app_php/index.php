<?php


session_start();
//first: check if user is logged in

  //check if logged in
  if(isset($_SESSION["isLoggedIn"])){
      //user is logged in
      $message = "";
      //option1: user clicked on logout
      if(isset($_POST["logout"])){
        //user clicked logout button
        logout();
        header("Refresh:0");
      }

      //option2: user clicked on update
      if(isset($_POST['update'])){
        //read POST
        $fname = $_POST['fname'];
        $lname = $_POST['lname'];
        $pass = $_POST['pass'];
        $cell = $_POST['cell'];
        //user info in session
        $loginUsername = $_SESSION["username"];
        $loginPassword = $_SESSION["pass"];

        //save new information to database
        $status = setUserInfo($fname, $lname, $pass, $cell, $loginUsername, $loginPassword);

        if($status == true){
          //update session
            $_SESSION["fname"] = $fname;
            $_SESSION["lname"] = $lname;
            $_SESSION["pass"] = $pass;
            $_SESSION["cell"] = $cell;
            $message = "Thank you, update was successful";
        }
        else{
          //update was NOT successful
          $message = "Sorry, update was NOT successful";
        }
      }

        //user did not click on anything
        //read user information and show it
        $fname = $_SESSION["fname"];
        $lname = $_SESSION["lname"];
        $pass  = $_SESSION["pass"];
        $cell  = $_SESSION["cell"];
        echo getProfileHTML($fname,$lname,$pass,$cell, $message);
      
  }
  else
  {//user has not logged in

    //check if user has submitted form or not 
    if (empty($_GET)){
      //first time to open the page, did not click on submit button
      //show login page
       echo getLoginHTML();
    }
    else
    {
      //user clicked on submit button
      $username = $_GET["username"];
      $pass = $_GET["password"];
      if($username=="" || $pass==""){
        //show error
        echo getLoginHTML("Please fill both the username and password.");
      }else{
        //no errors

          //check if user/password is correct
          $sql = "SELECT * FROM User WHERE username = '" . $username . "' AND password = '" . $pass . "'";

          //execute
          $result = executeSQLSelect($sql);

          //1. check username/pass in database
          if(count($result)>0){
              $row = $result[0];
              //if correct
               $fname2 = $row["fname"];
               $lname2 = $row["lname"];
               $cell2 = $row["cell"];
              //save session
              $_SESSION["isLoggedIn"] = true;
              $_SESSION["fname"] = $fname2;
              $_SESSION["lname"] = $lname2;
              $_SESSION["username"] = $username;
              $_SESSION["pass"] = $pass;
              $_SESSION["cell"] = $cell2;
              header("Refresh:0");
          }
          else{
              //incorrect username/password
            echo getLoginHTML("Username or password is incorrect.");
          }
          
      }
    }

  }

function setUserInfo($fname, $lname, $pass, $cell, $loginUsername, $loginPassword){
  //save to DB
  $sql = "UPDATE User SET password = '$pass', fname='$fname', lname='$lname', cell='$cell' WHERE username = '$loginUsername' AND password = '$loginPassword' ";

  return executeSQLUpdate($sql);
}

function logout()
{
  unset($_SESSION["isLoggedIn"]);
  unset($_SESSION["fname"]);
  unset($_SESSION["lname"]);
  unset($_SESSION["pass"]);
  unset($_SESSION["cell"]);
  session_unset();
  session_destroy();
}

//function to load the HTML of the login page
function getLoginHTML($message="")
{
  echo "<!DOCTYPE html>
      <html lang='en'> 

        <head> 
            <title>Login Form</title>
            <link rel='stylesheet' href='./css/style.css'>
            <script src='./js/jquery-3.3.1.min.js'></script>
            <script src='./js/mycode.js'></script>
        </head>
        <body>
          <section class='container'>
            <div class='login'>
              <h1>*** Login to Web App ***</h1>
                <form method='GET' action='./' id='loginForm'>
                <div><span>Email:</span><input type='text' name='username' ></div>
                <div><span>Password:</span><input type='password' name='password'></div>
                  <p class='submit'><input type='submit'  value='Login' id='login'>  </p>
                </form>
                <p style='color:red;text-align:center;' id ='loginMessage'>$message</p>
            </div>  
          </section> 
        </body>
      </html>";
}


function getProfileHTML($firstname, $lastname, $password, $cell, $message)
{
  echo "<!DOCTYPE html>
        <html lang='en'> 
          <head> 
              <title>Profile Form</title>
              <link rel='stylesheet' href='./css/style.css'>
              <script src='./js/jquery-3.3.1.min.js'></script>
              <script src='./js/mycode.js'></script>
          </head>
          <body>
            <section class='container'>
              <div class='login'>
                <h1>*** Your Profile Info ***</h1>
                  <form method='post' action='./'>
                    <div><span>First name:</span><input type='text' name='fname' value='$firstname'></div>
                    <div><span>Last name:</span><input type='text' name='lname' value='$lastname'></div>
                    <div><span>Password:</span><input type='password' name='pass' value='$password'></div>
                    <div><span>Cell#:</span><input type='text' name='cell' value='$cell'></div>
                   <!--  <p>First name:   <input type='text' name='Profile' ></p>
                    <p>Last name:   <input type='password' name='password'></p>
                    <p>Password:   <input type='text' name='Profile' ></p>
                    <p>Phone #:   <input type='text' name='Profile' ></p> -->

                    <p class='submit'><input type='submit' name='update' value='Update Info'></p>
                    <p class='submit'><input type='submit' name='logout' value='Log out'></p>
                  </form>
                  <p style='color:red;text-align:center;'>$message</p>
              </div> 
            </section> 
          </body>
        </html>";
}





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




?>