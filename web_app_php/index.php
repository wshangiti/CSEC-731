<?php

session_start();
//first: check if user is logged in

  //if logged in
  if(isset($_SESSION["isLoggedIn"])){
      //read user information and show it
      $fname = $_SESSION["fname"];
      $lname = $_SESSION["lname"];
      $pass  = $_SESSION["pass"];
      $cell  = $_SESSION["cell"];
      echo getProfileHTML($fname,$lname,$pass,$cell);
  }
  else
  {

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

          //1. check username/pass in database
          $dbstatus = true;

          if($dbstatus){
              //if correct
               $fname2 = "weeam";
               $lname2 = "alshangiti";
               $pass2 = "mypass";
               $cell2 = "5403130402";
              //save session
              $_SESSION["isLoggedIn"] = true;
              $_SESSION["fname"] = $fname2;
              $_SESSION["lname"] = $lname2;
              $_SESSION["pass"] = $pass2;
              $_SESSION["cell"] = $cell2;
          }
          else{
              //incorrect username/password
            echo getLoginHTML("Username or password is incorrect.");
          }
          
      }
    }

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
                <form method='GET' action='./'>
                  <p>Username:   <input type='text' name='username' ></p>
                  <p>Password:   <input type='password' name='password'></p>
                  <p class='submit'><input type='submit'  value='Login' >  </p>
                </form>
                <p style='color:red;text-align:center;'>$message</p>
            </div>  
          </section> 
        </body>
      </html>";
}


function getProfileHTML($firstname, $lastname, $password, $cell)
{
  echo "<!DOCTYPE html>
        <html lang='en'> 
          <head> 
              <title>Profile Form</title>
              <link rel='stylesheet' href='./css/style.css'>
          </head>
          <body>
            <section class='container'>
              <div class='login'>
                <h1>*** Your Profile Info ***</h1>
                  <form method='post' action='login.html'>
                    <div><span>First name:</span><input type='text' name='fname' value='$firstname'></div>
                    <div><span>Last name:</span><input type='text' name='lname' value='$lastname'></div>
                    <div><span>Password:</span><input type='password' name='pass' value='$password'></div>
                    <div><span>Cell#:</span><input type='text' name='cell' value='$cell'></div>
                   <!--  <p>First name:   <input type='text' name='Profile' ></p>
                    <p>Last name:   <input type='password' name='password'></p>
                    <p>Password:   <input type='text' name='Profile' ></p>
                    <p>Phone #:   <input type='text' name='Profile' ></p> -->

                    <p class='submit'><input type='submit' name='commit' value='Update Info'></p>
                    <p class='submit'><input type='submit' name='commit' value='Log out'></p>
                  </form>
              </div> 
            </section> 
          </body>
        </html>";
}
?>