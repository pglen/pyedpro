"<script>"

// Submit - and check

function buttpress()
{
    alert("Pressed");
    //console.log("user name len " + document.getElementById("user").value.length)
    if(document.getElementById("user").value.length < 4)
        {
        alert("User name must be 4 characters or more.");
        return;
        }
    var passx = document.getElementById("pass").value;

    if(passx.length == 0)
        {
        alert("Password cannot be empty.");
        return;
        }

    // Only go through hoops if there is a pass
    if(passx.length > 1)
        {
        if(passx.length < 6)
            {
            alert("Pass must be 6 characters or more.");
            return;
            }
        if(!hasUpperCase(passx) || !hasLowerCase(passx))
            {
            alert("Pass must have upper and lower case characters.");
            return;
            }
        }
    document.getElementById("frm").submit()
}

// Submit - and check

function passpress()
{
    //alert("Pressed pass button");
    console.log("Passpress");

    var passx = document.getElementById("new_pass").value;

    if(passx.length == 0)
        {
        alert("Password cannot be empty.");
        return;
        }

    // Only go through hoops if there is a pass
    if(passx.length > 1)
        {
        if(passx.length < 6)
            {
            alert("Pass must be 6 characters or more.");
            return;
            }
        if(!hasUpperCase(passx) || !hasLowerCase(passx))
            {
            alert("Pass must have upper and lower case characters.");
            return;
            }
        }
    document.getElementById("passfrm").submit()
}


function hasUpperCase(parola){
 for(i = 0; i < parola.length; i++){
    if(parola[i] === parola[i].toUpperCase()){
        return true;
    }
   }
  }

function hasLowerCase(parola){
 for(i = 0; i < parola.length; i++){
    if(parola[i] === parola[i].toLowerCase()){
        return true;
     }
   }
}

<!--
    // #$sss = <<<EOL
    // #
    // #<script>
    // #   function onFormSubmission(e){
    // #       //console.log("Submitted " + e.submitter);
    // #       return confirm("Do you want to delete Y/N");
    // #
    // #   }
    // #   //console.log("Inited");
    // #   var frm = document.getElementById('frm');
    // #   frm.addEventListener("submit", onFormSubmission);
    // #
    // #</script>
    // #
    // #EOL;
    // #echo $sss2;
-->

"</script>"



