import pandas as pd
import os

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

# Strip leading/trailing spaces from column names (if any)
all_data.columns = all_data.columns.str.strip()

# Rename columns for easier reference
all_data.rename(columns={
    'Product_Name': 'Product_Name',
    'Unit price': 'Price'
}, inplace=True)

# Convert 'Quantity' and 'Price' to numeric
all_data['Quantity'] = pd.to_numeric(all_data['Quantity'], errors='coerce')
all_data['Price'] = pd.to_numeric(all_data['Price'], errors='coerce')

# Convert 'Date' column to datetime format
all_data['Date'] = pd.to_datetime(all_data['Date'], errors='coerce')

# Extract Year and Month for grouping
all_data['Year-Month'] = all_data['Date'].dt.to_period('M')

# Calculate the Total Price (Quantity * Price Each)
all_data['Total Price'] = all_data['Quantity'] * all_data['Price']

# Step 5: Calculate monthly metrics by payment method
monthly_payment_metrics = all_data.groupby(['Year-Month', 'Payment_Method']).agg({
    'Total Price': 'sum',  # Total revenue per month by payment method
    'Invoice ID': 'nunique',  # Number of unique orders per month by payment method
    'Product_Name': 'count',  # Number of products sold per month by payment method
}).rename(columns={
    'Total Price': 'Monthly Revenue',
    'Invoice ID': 'Monthly Unique Orders',
    'Product_Name': 'Monthly Products Sold'
}).reset_index()

# Display one month at a time
print("\nOne-by-One Monthly Metrics by Payment Method:")
for month, group in monthly_payment_metrics.groupby('Year-Month'):
    print(f"\nMetrics for {month}:")
    print(group)

# Step 6: Calculate average metrics for each payment method across all months
average_payment_metrics = monthly_payment_metrics.groupby('Payment_Method')[['Monthly Revenue', 'Monthly Unique Orders', 'Monthly Products Sold']].mean()

# Display the average metrics for each payment method
print("\nAverage Monthly Metrics by Payment Method:")
print(average_payment_metrics)
