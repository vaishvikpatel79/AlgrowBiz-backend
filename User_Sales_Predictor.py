from Sales_pred_func import sales_prediction

# Get user inputs
state = input("Enter your state: ")
item_category = input("Enter the item category: ")
subcategory = input("Enter the subcategory: ")
months = int(input("How many months of inventory (between 1 and 6)? "))
prev_sale = int(input("what was the previous sales of your shop in the same time period? "))

user_sales_prediction = sales_prediction(state, item_category, subcategory, months,prev_sale)

print(f"predicted sales for next {months} months is: {user_sales_prediction}")

