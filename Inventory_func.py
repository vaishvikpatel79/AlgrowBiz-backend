def maximize_profit(budget, num_products, product_data, max_quantities):  
    dp = [0] * (budget + 1) 
    keep = [None] * (budget + 1)
    
    for i in range(num_products):
        cost, profit = product_data[i]
        max_quantity = max_quantities[i]

        for b in range(budget, cost - 1, -1):
            for q in range(1, max_quantity + 1):
                if q * cost <= b:
                    current_profit = dp[b - q * cost] + q * profit
                    if current_profit > dp[b]:
                        dp[b] = current_profit
                        
                        if keep[b - q * cost] is not None:
                            keep[b] = keep[b - q * cost][:]
                        else:
                            keep[b] = []
                        keep[b].append((i, q))
                else:
                    break  
    
    max_profit = dp[budget]    
    chosen_products = [0] * num_products
    if keep[budget] is not None:
        for idx, qty in keep[budget]:
            chosen_products[idx] += qty

    result = [(i, chosen_products[i]) for i in range(num_products)]
    return max_profit, result


def approximate_max_profit(budget, num_products, product_data, max_quantities):
    product_ratios = []
    for i in range(num_products):
        cost, profit = product_data[i]
        if profit > 0:  # Only consider products with non-negative profit
            ratio = profit / cost
            product_ratios.append((ratio, i, cost, profit, max_quantities[i])) 

    product_ratios.sort(reverse=True, key=lambda x: x[0])

    total_profit = 0
    chosen_products = [0] * num_products  # Initialize quantities to 0 for all products
    for _, index, cost, profit, max_qty in product_ratios:
        quantity = min(max_qty, budget // cost)
        if quantity > 0:
            total_profit += quantity * profit
            budget -= quantity * cost
            chosen_products[index] += quantity
        
        if budget <= 0:
            break

    result = [(i, chosen_products[i]) for i in range(num_products)]
    return total_profit, result

