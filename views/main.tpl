<!DOCTYPE html>
<head>
    <title>Tank Monitor</title>
    <meta http-equiv="refresh" content="900">

    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css">
    
    <!-- Optional theme -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap-theme.min.css">

%#    <link rel="stylesheet" type="text/css" href="{{ url('static', path='main.css') }}">
    <link rel="stylesheet" type="text/css" href="/static/main.css">

    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>    

    <!-- Latest compiled and minified JavaScript -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/js/bootstrap.min.js"></script>

</head>
<body>
    <main class="container-fluid">
    <div class="row store-row">
        <div class="col-md-4">
            <a class="btn {{'btn-default' if not len(alarms) else 'btn-danger'}}"
                href="/alarms">Alarms</a>
        </div>
    </div>
    %i = 0
    %for store in stores:
        %if i % 4 == 0:
            <div class="row store-row">
        %end
        <div class="col-xs-6 col-md-3 col-md-offset-0">
            <div class="row">
                <div class="col-xs-8">
                    <h4>{{store['store_name']}}</h4>
                </div>
                <div class="col-xs-4">
                    <div class="row skinny-row">
                    </div>
                    <div class="row no-margin-b">
                        <div class="col-xs-12 small-font">
                            <span id="time" class="{{'bg-blink' if store['time_expired'] else ''}}">{{store['last_update_time']}}</span>
                        </div>
                    </div>
                    <div class="row no-margin-b">
                        <div class="col-xs-12 tiny-font">
                            <span id="date" class="{{'bg-blink' if store['date_expired'] else ''}}">{{store['last_update_date']}}</span>
                        </div>
                    </div>
                </div>
            </div>
            <table class="table large-font">
                <tr>
                    <th>Volume</th>
                    <th></th>
                    <th>Ullage</th>
                </tr>
            %for tank in store['tanks']:
                <tr class="{{'danger' if tank['tank_low'] else ''}}">
                    <td><span class="{{'bg-blink' if tank['tank_low'] else ''}}">{{tank['gross_volume']}}</span></td>
                    <td>{{'{0} ({1})'.format(tank['tank_name'], tank['product_name'])}}</td>
                    <td>{{tank['ullage']}}</td>
                </tr>
            %end
            </table>
        </div>
        <hr class="spacer-25 hidden-md hidden-lg">
        %if i % 4 == 3:
            </div>
        %end
        %i += 1
    %end
    </main>
</body>