import os
from flask import ( Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    # import pdb; pdb.set_trace()
    recipes = mongo.db.recipes.find()
    cuisines = mongo.db.cuisine.find()
    categories = mongo.db.categories.find()
    return render_template("recipes.html", cuisines=cuisines, categories=categories, recipes=recipes)


@app.route("/category/<category>")
def get_recipes_by_category(category):
    recipes = mongo.db.recipes.find({'category_name': category})
    cuisines = mongo.db.cuisine.find()
    categories = mongo.db.categories.find()
    return render_template("recipes.html", cuisines=cuisines, categories=categories, recipes=recipes)


@app.route("/recipe/<recipe_id>")
def get_recipe_detail(recipe_id):
    # breakpoint()
    recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template("check_recipe.html", recipe=recipe)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    return render_template("recipes.html", recipes=recipes)


@app.route("/add_recipes", methods=["GET","POST"])
def add_recipes(): 
    if  request.method == "POST":
        recipe ={
            "recipe_name": request.form.get("recipe_name"),
            "category_name": request.form.get("category_name"),
            "description_name": request.form.get("description_name"),
            "cook_time": request.form.get("cook_time"),
            "ingredients": request.form.get("ingredients"),
            "methods": request.form.get("methods"),  
            "created_by ": session["user"]                      
          }
          
        mongo.db.recipes.insert_one(recipe)
        flash("New Recipe Added")
        return redirect (url_for("home"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_recipes.html",  categories=categories)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            #  To ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    #  session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return render_template("profile.html", username=username)

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))



def edit_recipes ():
    return render_template("edit_recipe.html")

def check_recipe():
    return render_template("check_recipe.html")    


@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.cuisine.find().sort("cuisine_name", 1))
    return render_template("cuisine_category.html", categories=categories)


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_cuisine_category", methods=["GET", "POST"])
def add_cuisine_category():
     if request.method == "POST":
        category = {
            "cuisine_name": request.form.get("cuisine_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New  Cuisine Category Added")
        return redirect(url_for("get_categories"))

     return render_template("add__cuisine_category.html")   

@app.route("/cookware")
def cookware():
    return render_template("cookware.html")     


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
