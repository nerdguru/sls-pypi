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
  // Generate download of hello.txt file with some content
  console.log('In csv: ' + package);
  var text = 'hello world ' + package;
  var filename = package + '.csv';
  download(filename, text);
}

function list() {
  console.log('Trying: ' + path);
  $.get(path, function (data) {
    console.log('Response: ' + JSON.stringify(data, null, 2));
    packageList = data;
    renderSubmitted();
    renderUnsubmitted();
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
    messageString += '<button type="button" class="btn btn-secondary btn-sm">';
    messageString += '<i class="fa fa-wrench" aria-hidden="true"></i> Update</button> ';
    messageString += '<button type="button" class="btn btn-danger btn-sm">';
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
    messageString += '<button type="button" class="btn btn-primary btn-sm">';
    messageString += '<i class="fa fa-paper-plane-o" aria-hidden="true"></i> Submit</button> ';
    messageString += '</td>';
    messageString += '</tr>';
  }

  document.getElementById('unsubmitted').innerHTML = messageString;
}

list();
