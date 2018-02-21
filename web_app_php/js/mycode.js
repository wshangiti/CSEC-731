// //read this when the page is loaded
$( document ).ready(function() {

	//listening to form submissions
	$("#loginForm").submit(function(e){

		//read user input
	    var email = $('[name="username"]').val();
	    var password = $('[name="password"]').val();

	    //clear any existing message
	    $("#loginMessage").text("");

	    //check if user has types something
	    if(email.length>0 && password.length>0)
	    {
	    	
	    	//check email is valid
	    	if(ValidateEmail(email))
	    	{
	    		return true;
	    	}
	    	else
	    	{
	    		//show err message: invalid email
	    		$("#loginMessage").text("Please type in a valid email address.");
	    	}
	    }
	    else
	    {
	    	//show error: empty fields
	    	$("#loginMessage").text("Please complete all fields.");
	    }
       
       return false;
    });
});




//function to validate email
function ValidateEmail(inputText)
{
	var mailformat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
	if(inputText.match(mailformat)){return true;}
	else{return false;}
}