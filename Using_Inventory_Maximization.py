from Inventory_Maximization import inventory_maximizer
from Sales_pred_func import sales_prediction

# budget = int(input("Enter Budget: "))
# num_products = int(input("Enter Number of Products: "))
# product_data = []
# max_quantities = []
# state = input("Enter your state: ")
# months = int(input("How many months of inventory (between 1 and 6)? "))

# product_list=[]
# total_qty=0



def maxProfit(budget,num_products,state,months,products):
    product_data = []
    max_quantities = []
    product_list=[]
    total_qty=0
    for i in range(num_products):
    
        # item_category = input(f"Enter the item category for product {i+1}: ")
        item_category = str(products[i]["category"])
        # subcategory = input(f"Enter the subcategory for product {i+1}: ")
        subcategory = str(products[i]["subcategory"])
        # prev_sale = int(input(f"what was the previous sales of {subcategory} in the same time period? "))
        prev_sale = int(products[i]["prevSale"])
        product_list.append(subcategory)

        user_sales_prediction = sales_prediction(state, item_category, subcategory, months,prev_sale)

        max_qty = user_sales_prediction
        total_qty = total_qty + max_qty

        # cost = int(input(f"Enter cost of {subcategory}: "))
        cost = int(products[i]["cost"])
        # profit = int(input(f"Enter profit on {subcategory}: "))
        profit = int(products[i]["profit"])

        product_data.append((cost, profit))
        max_quantities.append(max_qty)

    # max_profit,chosen_products = inventory_maximizer(budget,num_products,product_data,max_quantities,total_qty)
    return inventory_maximizer(budget,num_products,product_data,max_quantities,total_qty)

    # print("Maximum Profit:", max_profit)

    # print("To maximize profit, buy the following list of items")
    # for (item_index,qty) in chosen_products:
    #     prod=product_list[item_index]
    #     print(f"{qty} {prod}")


# for i in range(num_products):
    
#     item_category = input(f"Enter the item category for product {i+1}: ")
#     subcategory = input(f"Enter the subcategory for product {i+1}: ")
#     prev_sale = int(input(f"what was the previous sales of {subcategory} in the same time period? "))
#     product_list.append(subcategory)

#     user_sales_prediction = sales_prediction(state, item_category, subcategory, months,prev_sale)

#     max_qty = user_sales_prediction
#     total_qty = total_qty + max_qty

#     cost = int(input(f"Enter cost of {subcategory}: "))
#     profit = int(input(f"Enter profit on {subcategory}: "))
#     product_data.append((cost, profit))
#     max_quantities.append(max_qty)

# max_profit,chosen_products = inventory_maximizer(budget,num_products,product_data,max_quantities,total_qty)

# print("Maximum Profit:", max_profit)

# print("To maximize profit, buy the following list of items")
# for (item_index,qty) in chosen_products:
#     prod=product_list[item_index]
#     print(f"{qty} {prod}")


    
