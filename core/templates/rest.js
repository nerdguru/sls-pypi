path = 'https://qnuglnxidb.execute-api.us-east-1.amazonaws.com/dev/packages';
author = 'nerdguru';
sitename = 'nerdguru.net';

var packageList;

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

    error: function (data) {
        console.log('Response: ' + JSON.stringify(data, null, 2));
        document.body.style.cursor = 'auto';
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

    error: function (data) {
        console.log('Response: ' + JSON.stringify(data, null, 2));
        document.body.style.cursor = 'auto';
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
  $.get(path, function (data) {
    console.log('Response: ' + JSON.stringify(data, null, 2));
    packageList = data;
    renderSubmitted();
    renderUnsubmitted();
    document.body.style.cursor = 'auto';
  });
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

list();
