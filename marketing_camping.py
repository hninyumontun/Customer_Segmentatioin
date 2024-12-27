import pandas as pd
import os
from datetime import datetime  # Import datetime if needed for additional operations

# Step 1: Define the directory containing your CSV files
csv_directory = 'D:/GUSTO Bootcamp/Dataset/'

# Step 2: List all the CSV files in the directory
csv_files = [f for f in os.listdir(csv_directory) if f.endswith('.csv')]

# Step 3: Initialize an empty DataFrame to store all data
all_data = pd.DataFrame()

# Step 4: Loop through each CSV file, load it, and append it to the all_data DataFrame
for csv_file in csv_files:
    file_path = os.path.join(csv_directory, csv_file)
    print(f"Processing file: {file_path}")  # Debugging line
    data = pd.read_csv(file_path)
    all_data = pd.concat([all_data, data], ignore_index=True)

# Step 5: Convert necessary columns to numeric
all_data['Quantity'] = pd.to_numeric(all_data['Quantity'], errors='coerce')
all_data['Unit price'] = pd.to_numeric(all_data['Unit price'], errors='coerce')

# Add a Total Spending column
all_data['Total Spending'] = all_data['Quantity'] * all_data['Unit price']

# Step 6: Group data by 'Purchase Address', 'Customer Name', and 'payment_method'
grouped = all_data.groupby(['Gender', 'Customer ID', 'Payment_Method']).agg(
    Total_Orders=('Invoice ID', 'count'),
    Total_Spending=('Total Spending', 'sum')
).reset_index()

# Step 7: Define festivals and their date ranges
festivals = {
    'Thingyan': ('04-10', '04-30'),
    'Thadingyut': ('10-01', '10-31'),
    'Thasaungtine': ('11-01', '11-30'),
    'Christmas': ('12-23', '12-26'),
}

# Step 8: Parse 'Date' and determine festivals
all_data['Date'] = pd.to_datetime(all_data['Date'], errors='coerce')

def check_festival(order_date):
    if pd.isnull(order_date):
        return None
    month_day = order_date.strftime('%m-%d')
    for festival, (start, end) in festivals.items():
        if start <= month_day <= end:
            return festival
    return None

# Add 'Festival' column to the data
all_data['Festival'] = all_data['Date'].apply(check_festival)

# Step 9: Extract Year and Month for monthly grouping
all_data['Year-Month'] = all_data['Date'].dt.to_period('M')  # Extracts year and month as 'YYYY-MM'

# Merge the 'Festival' column back to the grouped DataFrame
grouped = grouped.merge(all_data[['Gender', 'Customer ID', 'Payment_Method', 'Festival', 'Year-Month']], 
                        on=['Gender', 'Customer ID', 'Payment_Method'], 
                        how='left')

# Step 10: Classify customers
def classify_customer(row):
    if row['Total_Orders'] > 1 or row['Total_Spending'] >= 700:
        return 'Loyal Buyer'
    elif row['Festival'] is not None:  # Check if festival exists
        return f"Seasonal Buyer ({row['Festival']})"
    else:
        return 'Occasional Buyer'

# Apply classification to the grouped DataFrame
grouped['Customer Type'] = grouped.apply(classify_customer, axis=1)

# Step 11: Segment customers
loyal_buyers = grouped[grouped['Customer Type'] == 'Loyal Buyer']
seasonal_buyers = grouped[grouped['Customer Type'].str.contains('Seasonal')]
occasional_buyers = grouped[grouped['Customer Type'] == 'Occasional Buyer']

# Step 12: Group data by 'Year-Month' and aggregate the results
grouped_by_month = grouped.groupby('Year-Month').agg(
    Total_Orders=('Total_Orders', 'sum'),
    Total_Spending=('Total_Spending', 'sum')
).reset_index()

# Step 13: Print monthly results
for period, group in grouped_by_month.groupby('Year-Month'):
    print(f"\nResults for {period}:")
    print(group)

# Step 14: Calculate percentage for each customer type
customer_type_totals = grouped.groupby('Customer Type').agg(
    Total_Orders=('Total_Orders', 'sum'),
    Total_Spending=('Total_Spending', 'sum')
).reset_index()

# Calculate the percentage for each customer type in Total Spending
total_spending_sum = customer_type_totals['Total_Spending'].sum()
customer_type_totals['Spending_Percentage'] = (customer_type_totals['Total_Spending'] / total_spending_sum) * 100

# Format the percentage with a % sign
customer_type_totals['Spending_Percentage'] = customer_type_totals['Spending_Percentage'].apply(lambda x: f"{x:.2f}%")

# Print the updated customer type totals with percentage
print("\nCustomer Type Spending Percentages:")
print(customer_type_totals[['Customer Type', 'Total_Spending', 'Spending_Percentage']])

# Step 15: Calculate percentage by month for each customer type
grouped_by_customer_type = grouped.groupby(['Year-Month', 'Customer Type']).agg(
    Total_Orders=('Total_Orders', 'sum'),
    Total_Spending=('Total_Spending', 'sum')
).reset_index()

# Calculate the percentage for each customer type by month
monthly_totals = grouped_by_customer_type.groupby('Year-Month')['Total_Spending'].sum().reset_index()
grouped_by_customer_type = grouped_by_customer_type.merge(monthly_totals, on='Year-Month', suffixes=('', '_Monthly_Sum'))

# Calculate the percentage for each customer type by month
grouped_by_customer_type['Spending_Percentage'] = (grouped_by_customer_type['Total_Spending'] / grouped_by_customer_type['Total_Spending_Monthly_Sum']) * 100

# Format the percentage with a % sign
grouped_by_customer_type['Spending_Percentage'] = grouped_by_customer_type['Spending_Percentage'].apply(lambda x: f"{x:.2f}%")

# Print the updated monthly data with percentage
print("\nMonthly Data by Customer Type with Percentages:")
print(grouped_by_customer_type[['Year-Month', 'Customer Type', 'Total_Spending', 'Spending_Percentage']])

# Optionally, print the segmented buyer categories by month
print("\nLoyal Buyers by Month:")
print(loyal_buyers.groupby('Year-Month').agg(
    Total_Orders=('Total_Orders', 'sum'),
    Total_Spending=('Total_Spending', 'sum')
))

print("\nSeasonal Buyers by Month:")
print(seasonal_buyers.groupby('Year-Month').agg(
    Total_Orders=('Total_Orders', 'sum'),
    Total_Spending=('Total_Spending', 'sum')
))

print("\nOccasional Buyers by Month:")
print(occasional_buyers.groupby('Year-Month').agg(
    Total_Orders=('Total_Orders', 'sum'),
    Total_Spending=('Total_Spending', 'sum')
))
