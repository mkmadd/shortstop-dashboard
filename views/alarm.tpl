<!DOCTYPE html>
<head>
    <title>Tank Alarms</title>
    <meta http-equiv="refresh" content="900">

    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css">
    
    <!-- Optional theme -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap-theme.min.css">

%#    <link rel="stylesheet" type="text/css" href="/static/main.css">

    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>    

    <!-- Latest compiled and minified JavaScript -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/js/bootstrap.min.js"></script>
</head>
<body>
    <main class="container-fluid">
        <div class="row store-row">
            <div class="col-md-4">
                <a class="btn btn-default btn-xs" href='/'>Back</a>
            </div>
            <div class="col-md-4 col-centered"><h4 class="text-center">Active Alarms</h4></div>
        </div>
        <div class="row">
            <div class="col-md-12">
                <table style="width:100%">
                    <tr>
                        <th>Site Name</th>
                        <th>Category</th>
                        <th>Device</th>
                        <th>Device Name</th>
                        <th>Description</th>
                        <th>Status</th>
                        <th>Date Time</th>
                        <th>Last Updated</th>
                    </tr>
                %for alarm in alarms:
                    <tr>
                        %for item in alarm:
                            <td>{{item}}</td>
                        %end
                    </tr>
                %end
                </table>
            </div>
        </div>
    </main>
</body>