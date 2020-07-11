var CognitoUserPool = AmazonCognitoIdentity.CognitoUserPool;
var CognitoUser = AmazonCognitoIdentity.CognitoUser;
var AuthenticationDetails = AmazonCognitoIdentity.AuthenticationDetails;
//var AWS = require('aws-sdk-2.693.0.min')

//Get information for cognito setup
var poolData = {
	UserPoolId : 'UserPoolId', // Your user pool id here
    ClientId : 'ClientId' // Your client id here
};

//Function for signing in
function signIn () {
    //Extract username and password from the signin form
    var username = $('#sign_in_username').val();
    var password = $('#sign_in_password').val();

    var authenticationData = {
        Username : username,
        Password : password,
    };

    //Enable authentication for the user
    var authenticationDetails = new AuthenticationDetails(authenticationData);
    var userPool = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserPool(poolData);

    var userData = {
        Username : username,
        Pool : userPool
    };

    //Create a new user object to draw information from and then redirect the user to the welcom page after successful login
    var cognitoUser = new CognitoUser(userData);
    cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: function (result) {
            window.location.href = "/welcome";
        },

        onFailure: function(err) {
            alert(err);
        }
    });
}

//Function for registering an admin
function registerAdmin () {
    //Extract all necessary information needed for registration from the HTML page
    var username = $('#registration_username').val();
    var password = $('#registration_password').val();
    var email = $('#registration_email').val();
    //var tenant = $('#registration_tenant').val();
    var name = $('#registration_name').val();
    var address = $('#registration_address').val();

    var userPool = new CognitoUserPool(poolData);
    var attributeList = [];
    var privateEmailProvider = ["web.de", "gmail.com", "gmx.de", "t-online.de"];

    var substr = email.substring(email.indexOf("@")+1);

    //Check if email is private or organisation email (e.g. daimler)
    function isPrivate(substring){
        for (i = 0; i < privateEmailProvider.length; i++){
            if (privateEmailProvider[i] == substring){
                return true;
            }
        }
        return false;
    }

    if (isPrivate(substr)==true) {
        console.log("Error: Usage of a private mail-account!");
        window.location.href = "/";
        return;
    }

    var dataEmail = {
        Name : 'email',
        Value : email
    };

    var dataIsAdmin = {
        Name : 'custom:isAdmin',
        Value : "true"
    };

    var dataMultiUserTenant = {
        Name : 'custom:multi-user-tenant',
        Value : "true"
    };

    var dataTenant = {
        Name : 'custom:tenant',
        Value : substr
    };

    var dataName = {
        Name : 'name',
        Value : name
    };

    var dataAddress = {
        Name : 'address',
        Value : address
    };

    //Add all attributes to the new tenant
    var attributeTenant = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserAttribute(dataTenant);
    var attributeEmail = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserAttribute(dataEmail);
    var attributeName = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserAttribute(dataName);
    var attributeAddress = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserAttribute(dataAddress);
    var attributeMultiUserTenant = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserAttribute(dataMultiUserTenant);
    var attributeIsAdmin = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserAttribute(dataIsAdmin);

    attributeList.push(attributeTenant);
    attributeList.push(attributeEmail);
    attributeList.push(attributeName);
    attributeList.push(attributeAddress);
    attributeList.push(attributeMultiUserTenant);
    attributeList.push(attributeIsAdmin);

    //After successful signup, redirect to validate the account
    userPool.signUp(username, password, attributeList, null, function(err, result){
        if (err) {
            alert(err);
            return;
        }
        cognitoUser = result.user;
        console.log('user name is ' + cognitoUser.getUsername());

        for (i = 0; i <= 100000000; i++){
        if (i == 100000000) {
            window.location.href = "/validate";
        }
    }
    });
}

//Function for reigstering a new user
function register () {
    //Extract all necessary information needed for registration from the HTML page
    var username = $('#registration_username').val();
    var password = $('#registration_password').val();
    var email = $('#registration_email').val();
    //var tenant = $('#registration_tenant').val();
    var name = $('#registration_name').val();
    var address = $('#registration_address').val();

    var userPool = new CognitoUserPool(poolData);
    var attributeList = [];
    var privateEmailProvider = ["web.de", "gmail.com", "gmx.de", "t-online.de"];

    var substr = email.substring(email.indexOf("@")+1);

    //Check if email is private or organisation email (e.g. daimler)
    function isPrivate(substring){
        for (i = 0; i < privateEmailProvider.length; i++){
            if (privateEmailProvider[i] == substring){
                return true;
            }
        }
        return false;
    }

    var dataEmail = {
        Name : 'email',
        Value : email
    };

    var dataIsAdmin = {
        Name : 'custom:isAdmin',
        Value : "false"
    };

    if (isPrivate(substr)==true)
    {
        var dataTenant = {
        Name : 'custom:tenant',
        Value : username
        };

        var dataMultiUserTenant = {
        Name : 'custom:multi-user-tenant',
        Value : "false"
        };
    }
    else {
        var dataTenant = {
        Name : 'custom:tenant',
        Value : substr
        };

        var dataMultiUserTenant = {
        Name : 'custom:multi-user-tenant',
        Value : "true"
        };
    }

    var dataName = {
        Name : 'name',
        Value : name
    };

    var dataAddress = {
        Name : 'address',
        Value : address
    };

    //Add all attributes to the new tenant
    var attributeTenant = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserAttribute(dataTenant);
    var attributeEmail = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserAttribute(dataEmail);
    var attributeName = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserAttribute(dataName);
    var attributeAddress = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserAttribute(dataAddress);
    var attributeMultiUserTenant = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserAttribute(dataMultiUserTenant);
    var attributeIsAdmin = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserAttribute(dataIsAdmin);

    attributeList.push(attributeTenant);
    attributeList.push(attributeEmail);
    attributeList.push(attributeName);
    attributeList.push(attributeAddress);
    attributeList.push(attributeMultiUserTenant);
    attributeList.push(attributeIsAdmin);

    //After successful signup, redirect to validate the account
    userPool.signUp(username, password, attributeList, null, function(err, result){
        if (err) {
            alert(err);
            return;
        }
        cognitoUser = result.user;
        console.log('user name is ' + cognitoUser.getUsername());

        for (i = 0; i <= 100000000; i++){
        if (i == 100000000) {
            window.location.href = "/validate";
        }
    }
    });
}

function validate () {
    //Extract the username and code from the HTML
    var username = $('#code_username').val();
    var code = $('#code_code').val();

    var userPool = new CognitoUserPool(poolData);

    var userData = {
        Username: username,
        Pool: userPool
    };

    //Check if the registration code is correct, if yes, redirect the the login page
    var cognitoUser = new CognitoUser(userData);
    cognitoUser.confirmRegistration(code, true, function(err, result) {
        if (err) {
            alert(err);
            return;
        }
        console.log('call result: ' + result);

        for (i = 0; i <= 100000000; i++){
        if (i == 100000000) {
            window.location.href = "/login";
        }
    }
    });
}

//Function for signing out
function signOut () {
    var userPool = new CognitoUserPool(poolData);
    var cognitoUser = userPool.getCurrentUser();

    //Completing signout
    if (cognitoUser !== null) {
        cognitoUser.signOut();
    }
    window.location.href = "/";
}

//Function for the welcome page
function setWelcome () {
    var userPool = new CognitoUserPool(poolData);
    var cognitoUser = userPool.getCurrentUser();

    if (cognitoUser != null) {
        cognitoUser.getSession(function(err, session) {
            if (err) {
                alert(err);
                return;
            }
            console.log(cognitoUser.signInUserSession.accessToken.jwtToken);
            //Set the username to be displayed in the top right-hand corner
            $('#username').html(cognitoUser.username);
            $('#username_href').html("/dashboard/" + cognitoUser.username);
        });
    }
    var folder_url = "/createfolder";

    //Post request to create the S3 and DynamoDB resources for the user
    $.post(folder_url, {
        'username': cognitoUser.getUsername()},
        function(data, status)
        {
            console.log("Data: " + data + "\nStatus: " + status);
        });

    //Protected API request
    var url = "/api/protected_api";

    $.post(url, {'access_token':
        cognitoUser.signInUserSession.accessToken.jwtToken})
    .done(function (data) {
        $('#data_from_protected_api').html(data);
    });
}

//Function to search for a username in the admin dashboard
function userSearch() {
    var username = $('#search_username').val();
    var period = $('#search_period').val();
    console.log("Searched username: "+username);
    console.log("Searched username: "+period);
    window.location.href = "/dashboardAdmin/" + username + "_" + period;
    //window.location.href = "/dashboardAdmin/" + username;
}

//Function for the dashboard redirect. This makes sure no user/tenant accesses foreign dashboards
function ToDashboard () {
    var userPool = new CognitoUserPool(poolData);
    var cognitoUser = userPool.getCurrentUser();

    if (cognitoUser != null) {
        cognitoUser.getSession(function(err, session) {
            if (err) {
                alert(err);
                return;
            }
            console.log(cognitoUser.signInUserSession.accessToken.jwtToken);
            $('#username').html(cognitoUser.username);
            $('#username_href').html("/dashboard/" + cognitoUser.username);
        });
    }
    cognitoUser.getUserAttributes(function (err, result) {
        if(err)
        {
            //console.log(err);
            return "Error"
        }
        console.log("++++++++");
        //If the user is an admin, redirect him to the admin dashboard
        if (cognitoUser.username == "admin"){
            window.location.href = "/dashboardAdmin";
        }
        //If there is a tenant, go to the tenant dashboard
        else if (result[7].getValue() == "true"){
            window.location.href = "/dashboardTenant/"+result[5].getValue();
        }
        //If it is just a user, redirect to his user dashboard
        else{
            window.location.href = "/dashboard/" +result[5].getValue()+"_"+result[3].getValue()+"_"+ cognitoUser.username;
        }
    });
}

//Function to check if the user is the admin
function userCheckAdmin() {
    var userPool = new CognitoUserPool(poolData);
    var cognitoUser = userPool.getCurrentUser();

    if (cognitoUser.username != "admin"){
        window.location.href = "/welcome";
    }
}

//Function to check if there is a tenant, if that is the case, redirect to the tenant dashboard
function userCheckTenant() {
    var userPool = new CognitoUserPool(poolData);
    var cognitoUser = userPool.getCurrentUser();
    var current_url = window.location.toString();
    var hostname = window.location.hostname;
    var protocol = window.location.protocol;
    var dashboard = "/dashboardTenant/"

    if (cognitoUser != null) {
        cognitoUser.getSession(function(err, session) {
            if (err) {
                alert(err);
                return;
            }
           // console.log(cognitoUser.signInUserSession.accessToken.jwtToken);
        });
    }

    cognitoUser.getUserAttributes(function (err, result) {
        if(err)
        {
            //console.log(err);
            return "Error"
        }
        //Create the correct url for the tenant dashboard
        correct_tenant_url = protocol+"//"+hostname+dashboard+result[5].getValue();
        array = Array.from(correct_tenant_url);
        current_url_short = current_url.substring(0,(array.length));
        console.log("Current url: "+current_url);
        console.log("Current url Short: "+current_url_short);
        console.log("Correct url: "+current_url);
        console.log("Array Length: "+array.length);

        //Direct the tenant to the correct dashboard
        if (current_url_short != correct_tenant_url){
            window.location.href = "/dashboardTenant/"+result[5].getValue();
        }
    });

}

function userCheck() {
    var userPool = new CognitoUserPool(poolData);
    var cognitoUser = userPool.getCurrentUser();
    var current_url = window.location;
    var hostname = window.location.hostname;
    var protocol = window.location.protocol;
    var dashboard = "/dashboard/";
    var dashboardAdmin = "/dashboardAdmin";
    var correct_url_admin = protocol+"//"+hostname+dashboardAdmin;

    // Output
    console.log("Aktuelle URL: "+current_url);
    console.log("User: "+cognitoUser);
    console.log("Hostname: "+hostname);
    console.log("Protokoll: "+protocol);
    console.log("Username: "+cognitoUser.username);

    if (cognitoUser != null) {
        cognitoUser.getSession(function(err, session) {
            if (err) {
                alert(err);
                return;
            }
           // console.log(cognitoUser.signInUserSession.accessToken.jwtToken);
        });
    }

    cognitoUser.getUserAttributes(function (err, result) {
        if(err)
        {
            //console.log(err);
            return "Error"
        }
        console.log("Attribut 0: "+result[0]);
        console.log("Attribut 1: "+result[1]); // address
        console.log("Attribut 2: "+result[2]); //
        console.log("Attribut 3: "+result[3]); // multi-user-tenant
        console.log("Attribut 4: "+result[4]); // name
        console.log("Attribut 5: "+result[5]); // Tenant
        console.log("Attribut 6: "+result[6]); // eMail
        console.log("Attribut 7: "+result[7]); // isAdmin

        var correct_url = protocol+"//"+hostname+dashboard+result[5].getValue()+"_"+result[3].getValue()+"_"+cognitoUser.username;
        console.log("Correct URL: " + correct_url);
        if (cognitoUser.username == "admin"){
            if (current_url != correct_url_admin){
                window.location.href = "/dashboardAdmin";
            }
        }
        else if (result[7].getValue() == "true"){
            window.location.href = "/dashboardTenant/"+result[5].getValue();
        }
        else if (correct_url == current_url){
            console.log("Current url und correct url stimmen ueberein!");
        }
        else{
            console.log("+++Current url und correct url stimmen NICHT ueberein!");
            window.location.href = "/dashboard/" +result[5].getValue()+"_"+result[3].getValue()+"_"+ cognitoUser.username;
        }
    });
}

//Function for tenant searching
function tenantSearch() {
    var tenant = $('#search_tenant').val();
    var period = $('#search_period').val();
    console.log("Searched tenant: "+tenant);
    console.log("Searched period: "+period);
    //Redirect the tenant to the correct admin dashboard
    if (tenant == "" || period == ""){
        window.location.href = "/dashboardAdmin/";
    }
    window.location.href = "/dashboardAdmin/" + tenant + "_" + period;
}

function userSearchTenant() {
    var userPool = new CognitoUserPool(poolData);
    var cognitoUser = userPool.getCurrentUser();
    var username = $('#search_username').val();
    var period = $('#search_period').val();
    console.log("Searched username: "+username);
    console.log("Searched period: "+period);

    if (cognitoUser != null) {
        cognitoUser.getSession(function(err, session) {
            if (err) {
                alert(err);
                return;
            }
           // console.log(cognitoUser.signInUserSession.accessToken.jwtToken);
        });
    }

    cognitoUser.getUserAttributes(function (err, result) {
        if(err)
        {
            //console.log(err);
            return "Error"
        }
        if (username == "" || period == "")
        {
            window.location.href = "/dashboardTenant/"+result[5].getValue();
        }
        window.location.href = "/dashboardTenant/"+result[5].getValue()+"_"+username+"_"+period;
    });
}

function dashboard () {
    var userPool = new CognitoUserPool(poolData);
    var cognitoUser = userPool.getCurrentUser();

    if (cognitoUser != null) {
        cognitoUser.getSession(function(err, session) {
            if (err) {
                alert(err);
                return;
            }
            console.log(cognitoUser.signInUserSession.accessToken.jwtToken);
            $('#username').html(cognitoUser.username);

        });
    }
}
