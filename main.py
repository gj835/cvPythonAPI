from flask import Flask, render_template, request, json, make_response, redirect, url_for
import os

app = Flask(__name__)

@app.route("/")
def start():
     return render_template('login.html')
  
# /accout post create accout
# /accout get get current user memberships
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
		# username = request.username
		# email = request.email
        username = request.form['username']
        email = request.form['email']
        
        # excute a curl through api
        # tmp = os.popen('ls').readlines()
        jsonString = '{"name":"'+username+'","attributes":{"lastName":"<none>","email":"'+email+'"}}'

        command = 'curl -u admin:password -X POST --data \''+ jsonString +'\' -H "Content-Type: application/json" http://10.145.96.50/api/account'
        tmp = os.popen(command)
        tmp = json.load(tmp)

        # return username + " " + email
        try:
            tmp['id']
        except:
            # return tmp['message']
            return str(tmp)
        else:
            return tmp['id']

@app.route("/login", methods=['POST'])
def login():
    # call an api and varify if the username and password is good to go
    username = request.form['username']
    password = request.form['password']
    jsonString = '{"password":"'+ password +'", "username":"'+ username +'"}'

    # /auth/login [post]
    command = 'curl -X POST --data \'' + jsonString + '\' -H "Content-Type: application/json" http://10.145.96.50/api/auth/login'
    # this is the token
    tmp = os.popen(command)
    tmp = json.load(tmp)

    try:                # check if the server respond with token
        tmp['value']
    except:
        return 'fail'
    else:
        # get account information to get workspace id
        command = 'curl -H "Authorization: '+tmp['value']+'" http://10.145.96.50/api/account'
            # curl -H "Authorization: r5uXzWfTuH9XmqC04GajPi0m9iP4TvPCCnmj5jPWr5TX8HKvWDDry4iuu0K4ynjzb90a1STea5vzDXrmfTS9rebb4i1mGWa49OfGbOb9P5yOOK88a0Tr5zOO9Kr0fyjL0GW5CP5r85fn4imrrzXfi9XHXPePvTjS9bi1zDn95uWW8mzimCrWD0HGWmKCbqLa1muWyCy5OzCuz9ebO50ie5PGr1KWnLySfmz0XiTXCqqb01u0Lv18WXyn9GHrbTm" http://10.145.96.50/api/account
        accountInfo = os.popen(command)
        accountInfo = json.load(accountInfo)

        userId = accountInfo[0]['userId']
        workspaceName = accountInfo[0]['accountReference']['name']
        accountId = accountInfo[0]['accountReference']['id']
        
        # get workspace id by workspaceName
        command = 'curl -H "Authorization: '+tmp['value']+'" http://10.145.96.50/api/workspace?name=' + workspaceName
        workspaceInfo = os.popen(command)
        workspaceInfo = json.load(workspaceInfo)
        
        workspaceId = workspaceInfo['id']

        command = 'curl -H "Authorization: '+tmp['value']+'" http://10.145.96.50/api/project/' + workspaceId
        projectInfo = os.popen(command)
        projectInfo = json.load(projectInfo)

        # set cookie
        respond = make_response(render_template('success.html', projectList = projectInfo, workspaceName = workspaceName))
        respond.set_cookie('token', tmp['value'])
        return respond
        # return render_template('success.html', projectList = projectInfo, workspaceName = workspaceName)
        # return str(projectInfo)

@app.route("/logout")
def logout():
    #/auth/logout
    token = request.cookies.get('token')
    command = 'curl -X POST http://10.145.96.50/api/auth/logout?token=' + token
    os.popen(command)
    return render_template('login.html')

@app.route("/projects", methods=['GET'])
def loadProjects():
    #load project basic on the token, still working
    return 'test'

@app.errorhandler(404)
def not_found(error):
    resp = make_response('404, page not found', 404)
    resp.headers['X-Something'] = 'A value'
    return resp

@app.errorhandler(405)
def not_found(error):
    resp = make_response('Please login first', 404)
    resp.headers['X-Something'] = 'A value'
    return resp

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)