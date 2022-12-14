import urllib.request, urllib.error, urllib.parse, json
from flask import Flask, render_template, request
import logging

app = Flask(__name__)

# Adding methods from previous assignments
def safe_get(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print("The server couldn't fulfill the request.")
        print("Error code: ", e.code)
    except urllib.error.URLError as e:
        print("Failed to reach a server")
        print("Reason: ", e)
    return None

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

# Use separate API function to get the link to the actual recipe & instructions
def get_recipe_info(recipe_id):
    url = "https://api.spoonacular.com/recipes/{id}/information?includeNutrition=false".format(id=recipe_id)
    headers = {"User-Agent": "Miya HCDE310 Project (miyan@uw.edu", "x-api-key": "fd64d81cb370438ea80311d1397e4534"}
    # print(url)
    request = urllib.request.Request(url, headers=headers)
    response = safe_get(request)
    if response is not None:
        json_result = json.load(response)
        recipe_link = json_result['sourceUrl'] # get url link to original recipe
        title = json_result['title'] # get the name of the recipe
        image = json_result['image'] # get image of recipe
        inner_list = [image, title, recipe_link] # store title of recipe and the link to the original recipe in a list
        return inner_list # return this list to recipes_get() to add to list of all recipes

# Base attempt at getting a json dict of data from Spoonacular
#   number = 3 <-- # of recipes returned
#   sort = popularity <-- sorts recipes in terms of most to least popular
def recipes_get(ingredients, diet="none"): 
    if diet == "none": # user didn't include any dietary restrictions
        url = "https://api.spoonacular.com/recipes/complexSearch?includeIngredients={ingredients}" \
          "&number=3&sort=popularity".format(ingredients=ingredients)
    else: 
        url = "https://api.spoonacular.com/recipes/complexSearch?includeIngredients={ingredients}" \
          "&number=3&sort=popularity&diet={diet}".format(ingredients=ingredients, diet=diet)
    
    headers = {"User-Agent":"Miya HCDE310 Project (miyan@uw.edu", "x-api-key":"fd64d81cb370438ea80311d1397e4534"}
    # print(url) # THIS IS A CHECK
    request = urllib.request.Request(url, headers=headers)
    result = safe_get(request)
    if result is not None:
        json_result = json.load(result)
        # print(len(json_result)) # THIS IS A CHECK
        # return json_result
        # Get recipe id's for each recipe returned
        recipes_list = []
        error = ["No results found"]
        for i in range(len(json_result['results'])): # Go through the amount of recipes returned
            recipe_id = json_result['results'][i]['id'] # Get recipe id to put into get_recipe_info()
            one_list = get_recipe_info(recipe_id) # Catch returned list for a single recipe
            recipes_list.append(one_list) # Add single list to larger list of all the recipes
        # print(recipe_list)
        if recipes_list != []:
            return recipes_list # Return this info to the webpage
        else:
            return error

# Base attempt at getting wine pairings from Spoonacular API
# Parameters: 
def wine_get(str_food_type, max_price="none"):
    if max_price == "none": #user didn't set a max price limit for wine
        url = "https://api.spoonacular.com/food/wine/pairing?food={food_type}".format(food_type=str_food_type)
    else:
        url = "https://api.spoonacular.com/food/wine/pairing?food={food_type}&maxPrice={max_price}".format(food_type=str_food_type, max_price=max_price)

    headers = {"User-Agent":"Miya HCDE310 Project (miyan@uw.edu", "x-api-key":"fd64d81cb370438ea80311d1397e4534"}
    # print(url) # THIS IS A CHECK
    request = urllib.request.Request(url, headers=headers)
    result = safe_get(request)
    if result is not None:
        json_result = json.load(result)
        # print(pretty(json_result)) # THIS IS A CHECK
        wine_list = []
        error = ["No results found"]

        paired_wines = json_result["pairedWines"]
        str_paired_wines = ", ".join(paired_wines)
        wine_list += [str_paired_wines]
        # print(str_paired_wines) # THIS IS A CHECK

        pairing_descrip = json_result["pairingText"]
        # print(json_result["pairingText"]) # THIS IS A CHECK
        # print(pairing_descrip) # THIS IS A CHECK
        wine_list += [pairing_descrip]

        wine_name = json_result["productMatches"][0]["title"]
        wine_list += [wine_name]

        wine_descrip = json_result["productMatches"][0]["description"]
        wine_list += [wine_descrip]

        wine_image = json_result["productMatches"][0]["imageUrl"]
        wine_list += [wine_image]

        wine_link = json_result["productMatches"][0]["link"]
        wine_list += [wine_link]

        wine_price = json_result["productMatches"][0]["price"]
        wine_list += [wine_price]

        if wine_list == []:
            return error
        return wine_list
    else: 
        return error

# # HOMEPAGE
@app.route("/")
def main_handler():
    app.logger.info("In MainHandler")
    return render_template("homepage.html", page_title="Home")

# RECIPE FINDER PAGE (getting user input)
@app.route("/recipes")
def ingredients_handler():
    app.logger.info("In MainHandler")
    return render_template("ingredientspage.html", page_title="Discover Recipes")

# WINE PAIRING PAGE (getting user input)
@app.route("/wines")
def wine_handler():
    app.logger.info("In MainHandler")
    return render_template("wines.html", page_title="Wines")

# WINE PAIRING PAGE (returning spoonacular data)
@app.route("/getwines")
def wine_response_handler():
    food_type = request.args.get("food_type") # Will be a string ("steak", "italian", etc)
    app.logger.info(food_type)
    str_food_type = food_type.replace(" ", "_")
    # print(str_food_type) # THIS IS A CHECK

    max_price = request.args.get("max_price")
    app.logger.info(max_price)

    if len(food_type) != 0: # if user inputted a food to wine pair with
        wine_list=wine_get(str_food_type, max_price)

        if wine_list == ["No results found"] or len(wine_list) <= 0:
            return render_template("norecipes.html")

        paired_wines = wine_list[0] # paired wines
        pairing_descrip = wine_list[1] # explanation of pairings
        # wine product
        wine_name = wine_list[2]
        wine_descrip = wine_list[3]
        wine_image = wine_list[4]
        wine_link = wine_list[5]
        wine_price = wine_list[6]
        
        return render_template("winerecs.html", page_title="Selected Wines",
        paired_wines=paired_wines, pairing_descrip=pairing_descrip,
        wine_name=wine_name, wine_descrip=wine_descrip, wine_image=wine_image,
        wine_link=wine_link, wine_price=wine_price)

# RECIPE FINDER PAGE (returning spoonacular data)
@app.route("/getrecipes")
def ingredient_response_handler():
    ingredients = request.args.getlist("ingredients") 
    app.logger.info(ingredients)
    # change the ingredients List to a long string of ingredients
    str_ingredients = "".join(ingredients)
    str_ingredients = str_ingredients.replace(" ", "")

    diet = request.args.get("diet")
    app.logger.info(diet)

    # if (len(ingredients) > 0) and (diet != "none"): # if the user filled in the form, return a list of recipes
    if (len(ingredients) > 0): 
        spoon_data=recipes_get(str_ingredients, diet)
        
        # FIGURE THIS THINGY OUT PLEASE!!!!!
        if len(spoon_data) < 3:
            return render_template("norecipes.html")

        recip_one_image = spoon_data[0][0] 
        recip_one_name = spoon_data[0][1]
        recip_one_link = spoon_data[0][2]

        recip_two_image = spoon_data[1][0]
        recip_two_name = spoon_data[1][1]
        recip_two_link = spoon_data[1][2]

        recip_three_image = spoon_data[2][0]
        recip_three_name = spoon_data[2][1]
        recip_three_link = spoon_data[2][2]

        # go through ingredients list and replace spaces with underline ("black beans" -> "black_beans")
        return render_template("recipespage.html",
                ingredients=str_ingredients,
                diet=diet, 
                page_title="Discovered Recipes",
                recip_one_name=recip_one_name,
                recip_one_image=recip_one_image,
                recip_one_link=recip_one_link,
                recip_two_name=recip_two_name,
                recip_two_image=recip_two_image,
                recip_two_link=recip_two_link,
                recip_three_name=recip_three_name,
                recip_three_image=recip_three_image,
                recip_three_link=recip_three_link
            ) # run recipes_get() method to get the name of the recipes returne
    elif len(ingredients) <= 0:
        return render_template("norecipes.html",
            page_title="Error",
            prompt="No ingredients submitted")
    else: # if form isn't filled, show form again with prompt to user
        return render_template("norecipes.html",
            page_title="Error",
            prompt="No ingredients submitted")

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)