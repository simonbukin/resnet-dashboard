# Resnet Dashboard
Dashboard for ResNet

Current Stuff:
- [x] Choose stack (Flask + jQuery)
- [x] Draw out data flow for the app (Flask->Python->jQuery)
- [ ] Figure out how to use ServiceNow API
- [ ] Figure out how to use WhenIWork API

How to actually launch the website:
1. Make sure you have pipenv installed, alongside Python 3.6.4. You should be able to to run "pipenv install" in the project directory to install dependencies.
2. Run "pipenv shell". This opens a virtual environment with all the packages installed.
3. Run "flask run" to start the website. You can now navigate to the address listed in the output of that command to see the site (for me it was http://127.0.0.1:5000/)

How the main update loop works:
We want to update information on the main page without reloading it every single time something is changed (like an API call returns a new ticket).
We start by adding a new route in `app.py`. This is done as follows:
```python
@app.route('/_loop')
def loop():
  return jsonify(result=some_data_maybe)
```
The route is the string inside of `@app.route`. This basically means that this function will be called whenever someone navigates to `www.whatever-this-website-is-named.com/_loop`. In reality, no user will actually do this, but we can use this as a dummy route to trigger a function call in python when we want to.

Next, we go into `dashboard.html`. We need to include some `script` tags at the bottom of the `<body>` for importing/including various files we need.

```javascript
<script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
```

This connects the `dashboard.html` with our `dashboard.js` file.

```javascript
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
```

This imports jQuery using the Google CDN.

```javascript
<script type=text/javascript>
  $SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
</script>
```

This points `$SCRIPT_ROOT` to be the name of the site when it starts running.

Now that `dashboard.html` is hooked up to our `dashboard.js` file, we can start working on the Javascript side of things.

Here, we define a `timer` variable that runs the `timing_loop` function on a set interval. `timing_loop` itself calls getJSON on `$SCRIPT_ROOT/_loop`, which is hte equivalent of navigating to that URL on the site itself. This triggers the dummy route we set up before, which returns a JSON string with a result in it. We then update the text of the element in `dashboard.html` with the result we got from the getJSON call.

This is the basic loop we want to use for updating the dashboard with new tickets or information we get from our API calls. We write our API calls and such within the dummy route, and then return the data as a JSON string for use in `dashboard.js`. We can then update elements on the page itself with the new data from the dummy route method.
