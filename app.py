from flask import Flask

app=Flask(__name__)

app.config['ENV'] = 'Development'
app.config['Debug'] = True

@app.route('/')
def index():

    return "hellow Hi my name is gabriel kim"


app.run(port='8000')