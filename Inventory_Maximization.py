from Inventory_func import maximize_profit
from Inventory_func import approximate_max_profit
from Sales_pred_func import sales_prediction

def inventory_maximizer(budget,num_products,product_data,max_quantities,total_qty):

    if total_qty*budget<10000000:
        max_profit, chosen_products = maximize_profit(budget, num_products, product_data, max_quantities)
    else:
        max_profit, chosen_products = approximate_max_profit(budget, num_products, product_data, max_quantities)

    return max_profit,chosen_products
    
    


