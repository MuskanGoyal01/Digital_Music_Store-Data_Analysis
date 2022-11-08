db = "chinook.db"

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

schema = 'ChinookSchema.png'
image = plt.imread(schema)
plt.figure(figsize = (10, 10))
plt.imshow(image)
plt.show()

def run_query(q):
    with sqlite3.connect('chinook.db') as conn:
        return pd.read_sql(q, conn)

def show_tables():
    view_query = 'SELECT name, type FROM sqlite_master WHERE type IN ("table","view");'
    return run_query(view_query)
print(show_tables(),'\n')

#QUESTION 1:
q1 = '''
WITH USA_sales AS (SELECT genre.name AS genre, COUNT(invoice_line.track_id) AS total_tracks
FROM invoice
JOIN track ON invoice_line.track_id = track.track_id
JOIN genre ON genre.genre_id = track.genre_id
JOIN invoice_line ON invoice.invoice_id = invoice_line.invoice_id
where billing_country like 'USA'
GROUP BY genre.name)
SELECT *, CAST((CAST(total_tracks as float) /(SELECT SUM(total_tracks) FROM USA_sales))*100 AS FLOAT) AS percentage
FROM USA_sales
ORDER BY 2 DESC
'''
USA_GENRE_SALES = run_query(q1)
print(USA_GENRE_SALES)

USA_GENRE_SALES = USA_GENRE_SALES.set_index('genre')
USA_GENRE_SALES['total_tracks'].plot.bar()
plt.title('Number of Tracks Sold in the US per Genre')
plt.show()

#QUESTION 2:
q2 = '''
SELECT employee_id, e.first_name || e.last_name as name,birthdate, reports_to, hire_date, e.country, SUM(total) AS employee_sales
FROM invoice i 
JOIN customer c ON c.customer_id = i.customer_id
JOIN employee e on e.employee_id = c.support_rep_id
GROUP BY 1,2
ORDER BY 6 DESC
'''
employee_sales = run_query(q2)
print(employee_sales)

employee_sales = employee_sales.set_index('name')
employee_sales['employee_sales'].plot.bar()
plt.title('Total Sales per Chinook Employee')
plt.show()

#QUESTION 3:
q3 ='''    
WITH country_sales AS(
    SELECT 
        c.country AS Country,
        SUM(i.total) AS Total_Purchases,
        COUNT(DISTINCT(c.customer_id)) AS Total_Customers,
        COUNT(i.invoice_id) AS Total_Orders
    FROM invoice i
    JOIN customer c ON c.customer_id = i.customer_id
    GROUP BY 1),
    country_sales_agg AS (
        SELECT
            CASE
                WHEN total_Customers = 1 THEN 'Other'
                ELSE country
            END AS country_identification,
            SUM(Total_purchases) AS Total_Sales,
            SUM(Total_customers) AS Total_Customers,
            SUM(Total_Orders) AS Total_Orders
        FROM country_sales
        GROUP BY 1)
    
SELECT
    country_identification as Country,
    Total_Customers,
    Total_Sales, 
    CAST(Total_Sales / Total_Customers as float) AS Average_sales_per_customer, 
    CAST(Total_Sales / Total_Orders as float) AS Average_order_value
    FROM country_sales_agg
    ORDER BY 1
'''
country_sales_data = run_query(q3)
print(country_sales_data)

fig,ax = plt.subplots(1,3)
ax[0].bar(country_sales_data['Country'],country_sales_data['Total_Sales'])
ax[1].bar(country_sales_data['Country'],country_sales_data['Average_order_value'])
ax[2].bar(country_sales_data['Country'],country_sales_data['Average_sales_per_customer'])
ax[0].set_title('Total Chinook Sales per Country')
ax[1].set_title('Average Order Value for each Country')
ax[2].set_title('Average Sales per Customer for each Country')
ax[0].set_xticklabels(country_sales_data['Country'],rotation=90)
ax[1].set_xticklabels(country_sales_data['Country'],rotation=90)
ax[2].set_xticklabels(country_sales_data['Country'],rotation=90)
plt.show()

#QUESTION 4:
q4 = '''
WITH album_tracks_dictionary AS
    (SELECT 
        a.album_id AS album_id,
        t.track_id AS track_id
    FROM album a
    JOIN track t ON a.album_id = t.album_id),
invoice_tracks_album AS
    (SELECT 
        il.invoice_id as invoice_id,
        atd.album_id AS album_id,
        atd.track_id AS track_id
    FROM invoice_line il
    JOIN album_tracks_dictionary atd ON atd.track_id = il.track_id),
invoice_full_dictionary AS
(
SELECT 
    ita.invoice_id AS invoice_id,
    CASE 
        WHEN
            (
            SELECT track_id FROM (SELECT itainv.track_id AS track_id
                                  FROM invoice_tracks_album itainv
                                  WHERE itainv.invoice_id = ita.invoice_id)
            EXCEPT 
            SELECT track_id FROM (SELECT ald.track_id AS track_id
                                  FROM album_tracks_dictionary ald
                                  WHERE ald.album_id = ita.album_id)
            ) IS NULL
            AND
            (
            SELECT track_id FROM (SELECT ald.track_id AS track_id
                                  FROM album_tracks_dictionary ald
                                  WHERE ald.album_id = ita.album_id)
            EXCEPT 
            SELECT track_id FROM (SELECT itainv.track_id AS track_id
                                  FROM invoice_tracks_album itainv
                                  WHERE itainv.invoice_id = ita.invoice_id)
            ) IS NULL
            THEN 1
        ELSE 0
    END AS Full_Album
FROM invoice_tracks_album ita
),
invoice_dictionary AS
(
SELECT 
    invoice_id,
    MAX(Full_Album) as Full_Album
FROM invoice_full_dictionary 
GROUP BY 1
)

SELECT
    COUNT(id.invoice_id) AS Total_invoices,
    SUM(id.Full_Album) AS Total_Full_Album,
    (CAST(SUM(id.Full_Album) / CAST(COUNT(id.invoice_id) as float) * 100 as float)) AS Percentage_Full_Album
FROM invoice_dictionary id 
'''
q4 = run_query(q4)
print(q4)