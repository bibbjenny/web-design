from flask import Flask, render_template

app = Flask(__name__)

# @app.route("/")
# def home():
#     name1 = "Jenny"
#     return render_template("index.html", name = name1)

@app.route("/")
def home():
    names = ["Jenny", "Sophia", "Nora", "John"]
    return render_template("index.html", names = names)



if __name__ == "__main__":
    app.run(debug = True)
