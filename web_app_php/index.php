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
        //save session
        $_SESSION["fname"] = $_POST['fname'];
        $_SESSION["lname"] = $_POST['lname'];
        $_SESSION["pass"] = $_POST['pass'];
        $_SESSION["cell"] = $_POST['cell'];

        //save new information to database
        $status = setUserInfo($_SESSION["fname"], $_SESSION["lname"], $_SESSION["pass"], $_SESSION["cell"]);

        if($status == true){
          //update has been successful
          $message = "Update was successful";
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
              header("Refresh:0");
          }
          else{
              //incorrect username/password
            echo getLoginHTML("Username or password is incorrect.");
          }
          
      }
    }

  }

function setUserInfo($fname, $lname, $pass, $cell){
  //save to DB
  return true;
}
function getUserInfo(){
  $info = array('fname' => $fname,
                'lname' => $lname,
                'pass'  => $pass, 
                'cell' => $cell);
  return $info;
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


function getProfileHTML($firstname, $lastname, $password, $cell, $message)
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
?>