import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog

@st.cache_data
def fetch_data():
    food_database = pd.read_excel(r"2019-2020 FNDDS At A Glance - FNDDS Nutrient Values.xlsx", 
                                header = 1 #set column headers
                                )
    return food_database

food_database = fetch_data()

####Nutrient selection section
micronutrient_preload = pd.read_excel("pre_loaded_options.xlsx",sheet_name="Micro Table Optimizer")
vitamin_preload = pd.read_excel("pre_loaded_options.xlsx",sheet_name="Vitamin Table Optimizer")


#for easy testing
pre_loaded_data = pd.read_excel(r"pre_loaded_diet.xlsx", sheet_name="Foods", 
                              header = 0 #set column headers
                              )

state_cols = ["Food Code", "Food Description", "Food Minimum Amount", "Food Maximum Amount", "Delete?"]

if "selected_foods" not in st.session_state:
    #st.session_state["selected_foods"] = pd.DataFrame(columns=state_cols)
    
    #to make testing easy this set up pulls from pre_loaded_data so don't have to constantly input stuff
    st.session_state["selected_foods"] = pd.DataFrame(columns=state_cols)
    st.session_state["selected_foods"]["Food Code"] = pre_loaded_data["Food Code"]
    st.session_state["selected_foods"]["Food Minimum Amount"] = pre_loaded_data["Food Req"]
    st.session_state["selected_foods"]["Food Maximum Amount"] = pre_loaded_data["Food Limits"]

    #for some reason have to convert the final dataframe to list to make it work
    st.session_state["selected_foods"]["Food Description"] = food_database.set_index('Food code').loc[pre_loaded_data.set_index("Food Code").index.values.tolist()]["Main food description"].tolist()
    st.session_state["selected_foods"]["Delete?"] = False
if "selected_foods_editor" not in st.session_state:
    st.session_state["selected_foods_editor"] = ''


st.subheader("Welcome to [Name TBD] version alpha!")
st.markdown("This is a tool for designing a diet that meets your macros, vitamin, and micronutrient needs.")
st.markdown("First, you tell us a little bit about yourself, then pick foods you'd like to eat.")
st.markdown("Then, we do the math, and tell you where your diet is lacking and suggest how to update it.")
st.markdown("""The philosophy behind this tool: 
            1) Avoid Obsessive Calorie Tracking - this tool replaces calorie tracking with weighing your food.
            When you are cooking, you simply weigh out the amount of food you're supposed to eat and that's it - the 
            calories were already calculated in advance.
            2) Eat Nutrient Dense Foods - Unlike some other dieting approaches, we favor nutrient dense foods. This way
            you can get all your required nutrients in (and then some) and still meet calorie targets. These nutrient 
            rich foods will leave you more full/satisfied after a meal.
            3) Eat Whole Foods - Pick whole/unprocessed foods during your optimization. You'll have to get creative - for example,
            if you want to add chia seeds, you could also potentially add greek yogurt too (to make a healthy parfait). A recipe/meal designer
            feature is TBD.""")

st.subheader("More about you")
st.markdown("***Please provide your gender, age, and weight.*** The optimizer will use your gender and age to optmize your micronutrient and vitamin intake based on the recommended values for your age and gender. Recommended values are sourced from the U.S. National Library of Medicine. Your weight will be used to help calculate your macronutrient intake needs.")

col3, col4, col5 = st.columns(3)

with col3:
    gender = st.radio("Select your gender:",["Male", "Female"])

with col4:
    age = st.slider("How old are you?",18,130,18)
with col5:
    your_weight = st.number_input("Please provide your weight in lbs:",0,1000,165)



st.markdown("***Please provide your desired daily caloric and marconutrient intake.***")
st.markdown("If you don't know how many calories you need, visit this website: https://www.calculator.net/calorie-calculator.html")
st.markdown("If you don't know how many other macros you need, you may use our defaults. They adjust automatically with your provided weight and gender.")

calories = st.number_input("Please provide how many calories you'd like to eat",0,10000,2000)



st.write("Macronutrients are defined in grams per pound of bodyweight. The slider will adjust how many grams per pound of body weight you'd like to eat. For example, if you weigh 100lbs and wanted to eat 50 grams of protein per day, you'd set the slider to .5. Again, you may use our defaults if you are unsure how much you need.")

col50, col51 = st.columns(2)
with col50:
    protein = st.slider("Protein: How many grams/lb. bodyweight in a day?",0.0,1.2,.8)
with col51:
    st.write(f"{round(protein*your_weight)} grams of protein per day.")

col52, col53 = st.columns(2)
with col52:
    total_fat = st.slider("Fat: How many grams/lb. bodyweight in a day?",.25,.5,.35)
with col53:
    st.write(f"{round(total_fat*your_weight)} grams of fat per day.")

col54, col55 = st.columns(2)
with col54:
    carbohydrate = st.slider("Carbs: How many grams/lb. of bodyweight in a day?",.5,3.0,1.0)
with col55:
    st.write(f"{round(carbohydrate*your_weight)} grams of carbs per day.")

st.write("Fiber will just be defined in grams per day. Females are generally recommended 25 grams per day, and males are recommended to have 38 grams per day.")
fiber_start = 38 if gender == "Male" else 25
fiber = st.slider("How many grams of fiber in a day?",20,50,fiber_start)

micro_values = micronutrient_preload[(micronutrient_preload["Gender"] == gender) & (micronutrient_preload["Max Age"] >= age) & (micronutrient_preload["Min Age"] <= age)] 
vitamin_values = vitamin_preload[(micronutrient_preload["Gender"] == gender) & (vitamin_preload["Max Age"] >= age) & (vitamin_preload["Min Age"] <= age)]



st.header("Select Foods")
st.markdown("Use the search box below to select your foods. You may either search by food code or food name. You can see the foods you have selected and their quantities below. Also, foods may be named differently - for example, marinara or tomato sauce is called spaghetti sauce here and tofu is called soybean curd. There is a default semi-optimal diet pre-loaded, but please add and remove foods to make it your own.") 
st.markdown("The default minimum and maximum for foods is 0 and 1 (remember 1 = 100 grams). However you may change these as you please.") 
st.markdown("Just keep in mind that the optimizer has no concept of what a human can feasibly eat. If you do not put limits on your foods, it might tell you to eat 1000 grams of spinach, which is quite a lot.") 
st.markdown("Also, it does not have a concept of taste or know what foods you like. For example, if you like to eat pasta with spaghetti sauce, or use olive oil to cook, make sure you add these as well and set appropriate minimum and maximum amounts. Otherwise, it may deem the foods unoptimal and say you should eat 0 grams.")
st.markdown("Finally, when you have a successully optimized diet, please review the resulting nutrient quantities. They will be provided to you below if the optimization is successful. The optimizer may not have been able to get all the nutrient values to their targets, so consider adding foods that may boost the intake of that nutrient. For example, if you need more calcium, add milk to your diet.")


min_help_msg = """Double click the boxes in this column to edit them. Force the optimizer to give you at least this much of a food. 
                   Enter the quantity in 100s of grams. For example: if you want to eat at least 100 grams of a food, put a 1 in that food's box."""

max_help_msg = """Double click the boxes in this column to edit them. Stop the optimizer giving you more than a quantity of a food. 
                   Enter the quantity in 100s of grams. For example: if you want to eat 100 grams or less of a food, put a 1 in that food's box."""

st.session_state["selected_foods_editor"] = st.data_editor(st.session_state["selected_foods"],
                                                column_config = {"Food Minimum Amount": 
                                                                    st.column_config.NumberColumn("Food Minimum Amount (in 100gs)", 
                                                                                                help = min_help_msg), 
                                                                    "Food Maximum Amount": 
                                                                    st.column_config.NumberColumn("Food Maximum Amount (in 100gs)", 
                                                                                                help = max_help_msg),
                                                                    "Delete?": st.column_config.CheckboxColumn()
                                                                    },disabled = state_cols[:2],hide_index=True, num_rows="fixed")

selected_food = st.selectbox("Type here to select foods",
                             options=food_database["Food code"].astype(str)+" - "+food_database["Main food description"],
                             placeholder="Choose your foods here")

col1, col2 = st.columns(2)
#add foods to cached list
with col1:
    if st.button("Add Food"):
        if st.session_state["selected_foods"]["Food Code"].isin([selected_food[:8]]).any():
            st.write("You've already selected this food.")
        else:
            new_food = pd.DataFrame([[selected_food[:8], 
                                    food_database[food_database["Food code"] == int(selected_food[:8])]["Main food description"].reset_index(drop=True)[0],
                                    0, 1, False]], columns=state_cols)
            st.session_state["selected_foods"] = pd.concat([st.session_state["selected_foods_editor"], new_food], ignore_index=True)
            st.rerun()

with col2:
    if st.button("Delete"):
        st.session_state["selected_foods_editor"] = st.session_state["selected_foods_editor"][st.session_state["selected_foods_editor"]["Delete?"] == False]
        st.session_state["selected_foods"] = st.session_state["selected_foods_editor"].copy()
        st.rerun()


# only optimizing macros and vitamins for now, however this will need to be much more flexible I think
#macros are straight from database titles - the vitamins are grabbing the vitamin_preload columns => returns df, which we => list, then slice off the front values which is age, gender, etc.
#the vitamin col titles map directly to the food database titles


if st.button("Optimize"):
    
    #macros are straight from database titles - the vitamins are grabbing the vitamin_preload columns => returns df, which we => list, then slice off the front values which is age, gender, etc.
    #the vitamin col titles map directly to the food database titles  
    optimization_col_titles = ["Energy (kcal)",'Protein (g)','Total Fat (g)','Carbohydrate (g)','Fiber, total dietary (g)'] + vitamin_preload.columns.tolist()[3:]
    
    #for some reason streamlit stores values as objects in data_editor so need to convert them to int searching across food code dataframe
    food_data = food_database[food_database["Food code"].isin(st.session_state["selected_foods_editor"]["Food Code"].astype("int"))]
    food_data = food_data[["Food code"] + optimization_col_titles]
    food_data = food_data.set_index("Food code")
    optimization_frame = food_data.join(st.session_state["selected_foods_editor"].astype({'Food Code':'int32'}).set_index("Food Code"))
    #st.write(optimization_frame.index)
    target_values = [calories, protein*your_weight, total_fat*your_weight, carbohydrate*your_weight, fiber] + vitamin_values.iloc[0].tolist()[3:] #actual values of what the optimizer is targeting, clip the front 3 because these are just gender, age,etc.
    
    greater_than = optimization_col_titles[1:] #everything but calories
    equal_to = [optimization_col_titles[0]] #calories MUST PASS AS LIST TO DATAFRAME TO GET 2D array, that is why its bracketed

    c = np.zeros_like(optimization_frame["Energy (kcal)"].to_numpy())
    A_ub = -optimization_frame[greater_than].to_numpy().T
    b_ub = -np.array(target_values[1:]) #clipping off calories
    A_eq = optimization_frame[equal_to].to_numpy().T
    b_eq = target_values[0]
    bounds = [(req, limit) for req, limit in zip(optimization_frame['Food Minimum Amount'].to_numpy(), optimization_frame['Food Maximum Amount'].to_numpy())]
    results = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs-ipm")

    st.header("Your Optimized Diet")
    st.markdown(f"Optimization Status: {results.message}")

    if results.message == "Optimization terminated successfully. (HiGHS Status 7: Optimal)":
        results_frame = optimization_frame[["Food Description"]].copy()
        results_frame["Amount in 100g"] = results.x

        st.header("Your Food Quantities")
        st.markdown("The table below shows how much of each food you should eat in 100gs. So 1 = 100gs.")
        st.markdown("If you hover over the table, there will be a small pop-up on the top right of the table where you may download the results in a spreadsheet.")
        st.dataframe(results_frame)

        st.header("Nutrient Quantities")
        st.markdown("The table below shows how much of each nutrient you are getting, relative to the target values above.")

        nutrient_values_results = pd.DataFrame()
        combined_constraints = equal_to + greater_than
        additional_values = micronutrient_preload.columns.tolist()[3:]

        nutrient_values_results["Nutrient"] = combined_constraints + additional_values

        nutrient_values_results["optimizer reults"] = np.dot(results.x, food_database[food_database["Food code"].isin(results_frame.index.to_list())][combined_constraints + additional_values].to_numpy())
        nutrient_values_results["target values"] = target_values + micro_values.iloc[0].tolist()[3:]
        
        sub_optimal_nutrients = nutrient_values_results["Nutrient"][nutrient_values_results["target values"]*.99 > nutrient_values_results["optimizer reults"]]
        sub_optimal_nutrients = "The following nutrients are below their target values: " + ', '.join(map(str, sub_optimal_nutrients))
        st.markdown(sub_optimal_nutrients)

        st.dataframe(nutrient_values_results)
    else:
        st.markdown("Your diet could not be optimized. Please add more foods or adjust your food quantities.")
