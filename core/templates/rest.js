var path = 'API_PATH';
var userPoolId = 'USERPOOL_ID';
var clientId = 'CLIENT_ID';
var appWebDomain = 'COGNITO_DOMAIN';

var redirectUriSignIn = 'https://pypi.CORE_DOMAIN/my/';
var redirectUriSignOut = 'https://pypi.CORE_DOMAIN/my/';
var sitename = 'CORE_DOMAIN';
var identityProvider = 'GitHub';

var packageList;
var auth;
var author;

function download(filename, text) {
  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}

function csv(package) {
  document.body.style.cursor = 'wait';
  console.log('Trying: ' + path + '/' + package);
  $.get(path + '/' + package, function (data) {
    console.log('Response: ' + data.csv);
    document.body.style.cursor = 'auto';
    download(package + '.csv', decodeURIComponent(data.csv));
  });

}

function remove(id) {
  document.body.style.cursor = 'wait';
  console.log('Delete path: ' + path + '/' + id);
  removeWait = true;
  $.ajax({
    url: path + '/' + id,
    type: 'DELETE',
    success: function (data) {
        console.log('Response: ' + JSON.stringify(data, null, 2));
        document.body.style.cursor = 'auto';
        list();
      },

    error: function (jqXHR, exception)  {
        console.log('Error code: ' + jqXHR.status);
        console.log('Exception: ' + jqXHR.responseText);
        document.body.style.cursor = 'auto';
        alert(jqXHR.responseText);
        list();
      },
  });
}

function publish(id) {
  document.body.style.cursor = 'wait';
  console.log('Post path: ' + path + '/' + id);
  removeWait = true;

  $.ajax({
    url: path + '/' + id,
    type: 'POST',
    success: function (data) {
        console.log('Response: ' + JSON.stringify(data, null, 2));
        document.body.style.cursor = 'auto';
        list();
      },

    error: function (jqXHR, exception)  {
        console.log('Error code: ' + jqXHR.status);
        console.log('Exception: ' + jqXHR.responseText);
        document.body.style.cursor = 'auto';
        alert(jqXHR.responseText);
        list();
      },
  });
}

function confirmRemove(package) {
  var r = confirm('Are you sure you would like to remove ' +
    package + ' from this Python package index?');
  if (r == true) {
    console.log('OK to remove ' + package);
    remove(package);
  } else {
    console.log('Cancelled removeal of ' + package);
  }
}

function confirmUpdate(package) {
  var r = confirm('Are you sure you would like to update ' +
    package + ' on this Python package index?');
  if (r == true) {
    console.log('OK to update ' + package);
    publish(package);
  } else {
    console.log('Cancelled update of ' + package);
  }
}

function confirmSubmit(package) {
  var r = confirm('Are you sure you would like to submit ' +
    package + ' on this Python package index?');
  if (r == true) {
    console.log('OK to submit ' + package);
    publish(package);
  } else {
    console.log('Cancelled submittal of ' + package);
  }
}

function list() {
  document.body.style.cursor = 'wait';
  console.log('Trying: ' + path);

  $.ajax({
    url: path,
    type: 'GET',
    success: function (data) {
        console.log('Response: ' + JSON.stringify(data, null, 2));
        packageList = data;
        renderSubmitted();
        renderUnsubmitted();
        document.body.style.cursor = 'auto';
      },

    error: function (data) {
        console.log('Error Response: ' + JSON.stringify(data, null, 2));
      },

    beforeSend: function (xhr) {
        xhr.setRequestHeader('Authorization',
          auth.getSignInUserSession().idToken.jwtToken);
      },
  });
}

function toggleLogin(data) {
  document.getElementById('loggedIn').style.display = 'block';
  document.getElementById('logout').style.display = 'block';
  document.getElementById('loggedOut').style.display = 'none';

  //console.log('In toggleLogin: ' + JSON.stringify(data, null, 2));
  console.log('In toggleLogin profile ' + data.profile);
  console.log('In toggleLogin picture ' + data.picture);
  console.log('In toggleLogin author ' + data.profile.split('/')[3]);
  author = data.profile.split('/')[3];

  var picString = '<a href="#" data-toggle="tooltip"';
  picString += ' title="' + author + '">';
  picString += '<img src="' + data.picture + '" ';
  picString += 'style="height: 50px;" class="rounded"></a>';
  document.getElementById('pic').innerHTML = picString;
  list();
}

function toggleLogout() {
  document.getElementById('loggedIn').style.display = 'none';
  document.getElementById('logout').style.display = 'none';
  document.getElementById('loggedOut').style.display = 'block';
}

function initCognitoSDK() {
  var authData = {
    ClientId: clientId,
    AppWebDomain: appWebDomain,
    TokenScopesArray: ['openid'],
    RedirectUriSignIn: redirectUriSignIn,
    RedirectUriSignOut: redirectUriSignOut,
    IdentityProvider: identityProvider,
    UserPoolId: userPoolId,
    AdvancedSecurityDataCollectionFlag: false,
  };
  var auth = new AmazonCognitoIdentity.CognitoAuth(authData);
  auth.userhandler = {
    onSuccess: function (result) {
      $.ajax({
        url: 'https://' + auth.getAppWebDomain() + '/oauth2/userInfo',
        type: 'GET',
        success: function (data) {
            console.log('Success Response: ' + JSON.stringify(data, null, 2));
            toggleLogin(data);
          },

        error: function (data) {
            console.log('Error Response: ' + JSON.stringify(data, null, 2));
          },

        beforeSend: function (xhr) {
            xhr.setRequestHeader('Authorization', 'Bearer ' +
              auth.getSignInUserSession().getAccessToken().jwtToken);
          },
      });
      toggleLogin();
    },

    onFailure: function (err) {
      alert('Error!' + err);
    },
  };
  return auth;
}

function renderSubmitted() {
  var messageString = '';
  for (var i = 0; i < packageList.submitted.length; i++) {
    messageString += '<tr>';
    messageString += '<td>' + packageList.submitted[i].package;
    messageString += ' <a href="http://github.com/' + author + '/';
    messageString += packageList.submitted[i].package;
    messageString += '" data-toggle="tooltip" title="Goto GitHub repo" target="_blank">';
    messageString += '<i class="fa fa-github" aria-hidden="true" style="font-size:20px"></i>';
    messageString += '</a>';
    messageString += ' <a href="http://' + sitename + '/' + packageList.submitted[i].package;
    messageString += '" data-toggle="tooltip" title="Goto package page" target="_blank">';
    messageString += ' <i class="fa fa-gift" style="font-size:20px"></i>';
    messageString += '</a>';
    messageString += ' <a href="#" data-toggle="tooltip"';
    messageString += ' title="Get CSV of download data">';
    messageString += ' <i id="download-' + packageList.submitted[i].package;
    messageString += '" class="fa fa-file-excel-o" style="font-size:14px"></i>';
    messageString += '</a>';
    messageString += '</td>';
    versionList = '';
    for (var j = 0; j < packageList.submitted[i].versions.length; j++) {
      versionList += packageList.submitted[i].versions[j] + '\n';
    }

    messageString += '<td><a href="#" data-toggle="tooltip"';
    messageString += ' title="' + versionList + '">';
    messageString += packageList.submitted[i].versions.length + '</a></td>';
    messageString += '<td>' + packageList.submitted[i].downloads.number + '</td>';
    messageString += '<td>' + packageList.submitted[i].downloads.locations + '</td>';
    messageString += '<td>' + packageList.submitted[i].downloads.requestIPs + '</td>';
    messageString += '<td>';
    messageString += '<button type="button" class="btn btn-secondary btn-sm"';
    messageString += 'id="update-' + packageList.submitted[i].package + '">';
    messageString += '<i class="fa fa-wrench" aria-hidden="true"></i> Update</button> ';
    messageString += '<button type="button" class="btn btn-danger btn-sm"';
    messageString += 'id="remove-' + packageList.submitted[i].package + '">';
    messageString += '<i class="fa fa-times" aria-hidden="true"></i> Remove</button>';
    messageString += '</td>';
    messageString += '</tr>';
  }

  document.getElementById('submitted').innerHTML = messageString;

  for (var i = 0; i < packageList.submitted.length; i++) {
    console.log('Event listener: ' + packageList.submitted[i].package);

    document.getElementById('download-' + packageList.submitted[i].package).
      addEventListener('click', function (event) {
          console.log(event.target.id);
          csv(event.target.id.replace('download-', ''));
        }, false);

    document.getElementById('remove-' + packageList.submitted[i].package).
      addEventListener('click', function (event) {
          console.log(event.target.id);
          confirmRemove(event.target.id.replace('remove-', ''));
        }, false);

    document.getElementById('update-' + packageList.submitted[i].package).
      addEventListener('click', function (event) {
          console.log(event.target.id);
          confirmUpdate(event.target.id.replace('update-', ''));
        }, false);
  }
}

function renderUnsubmitted() {
  var messageString = '';
  for (var i = 0; i < packageList.unsubmitted.length; i++) {
    messageString += '<tr>';
    messageString += '<td>' + packageList.unsubmitted[i];
    messageString += ' <a href="http://github.com/' + author + '/';
    messageString += packageList.unsubmitted[i];
    messageString += '" data-toggle="tooltip" title="Goto GitHub repo" target="_blank">';
    messageString += '<i class="fa fa-github" aria-hidden="true" style="font-size:20px"></i>';
    messageString += '</a>';
    messageString += '</td>';
    messageString += '<td>';
    messageString += '<button type="button" class="btn btn-primary btn-sm"';
    messageString += 'id="submit-' + packageList.unsubmitted[i] + '">';
    messageString += '<i class="fa fa-paper-plane-o" aria-hidden="true"></i> Submit</button> ';
    messageString += '</td>';
    messageString += '</tr>';
  }

  document.getElementById('unsubmitted').innerHTML = messageString;

  for (var i = 0; i < packageList.unsubmitted.length; i++) {
    console.log('Event listener: ' + packageList.unsubmitted[i]);
    document.getElementById('submit-' + packageList.unsubmitted[i]).
      addEventListener('click', function (event) {
          console.log(event.target.id);
          confirmSubmit(event.target.id.replace('submit-', ''));
        }, false);
  }
}

toggleLogout();
auth = initCognitoSDK();
document.getElementById('loggedOut').addEventListener('click', function () {
      console.log('Attempting login');
      auth.getSession();
    });

document.getElementById('logout').addEventListener('click', function () {
      console.log('Attempting logout');
      auth.signOut();
      toggleLogout();
    });

auth.parseCognitoWebResponse(window.location.href);
console.log('done with first pass');
