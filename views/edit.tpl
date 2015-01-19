<!DOCTYPE html>
<head>
    <title>Edit Warning Levels</title>

    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css">
    
    <!-- Optional theme -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap-theme.min.css">

    <link rel="stylesheet" type="text/css" href="{{ url('static', path='test_template.css') }}">

    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>    

    <!-- Latest compiled and minified JavaScript -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/js/bootstrap.min.js"></script>
</head>
<body>
    <main class="container-fluid">
    <div class="row store-row">
        <div class="col-md-4">
            <a class="btn btn-default btn-xs"
                href="/">Back</a>
            <button class="btn btn-default btn-xs" formmethod="post"
                form="warn-edit" formaction="/edit" type="submit">Save</a>
        </div>
    </div>
    <form id="warn-edit">
    %i = 0
    %for store in stores:
        %if i % 4 == 0:
            <div class="row store-row">
        %end
        <div class="col-md-3">
            <div class="row">
                <div class="col-md-8">
                    <h4>{{store['store_name']}}</h4>
                </div>
            </div>
            <table style="width:100%">
                <tr>
                    <th>Warning Level</th>
                    <th>Tank</th>
                </tr>
            %for tank in store['tanks']:
                <tr>
                    <td>{{'{0} ({1})'.format(tank['tank_name'], tank['product_name'])}}</td>
                    <td><input name="id_{{tank['site_id']}}_{{tank['storage_id']}}" type="text" value="{{tank['warning_level']}}"/></td>
                </tr>
            %end
            </table>
        </div>
        %if i % 4 == 3:
            </div>
        %end
        %i += 1
    </form>
    %end
    </main>
</body>