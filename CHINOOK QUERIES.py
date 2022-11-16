import sqlite3
import pandas as pd

db = "Statics/chinook.db"


def run_query(q):
    with sqlite3.connect('Statics/chinook.db') as conn:
        return pd.read_sql(q, conn)


# Question 1: Which countries have the most Invoices?
q1 = ''' 
SELECT billing_country,COUNT(billing_country) AS Invoice_Number
FROM invoice
GROUP BY billing_country
ORDER BY Invoice_Number DESC
'''
q1 = run_query(q1)
print('\n', q1)


# Question 2: Which city has the best customers?
# We would like to throw a promotional Music Festival in the city we made the most money.
# Write a query that returns the 1 city that has the highest sum of invoice totals.
# Return both the city name and the sum of all invoice totals.
q2 = '''
SELECT billing_city,SUM(total) AS InvoiceTotal
FROM invoice
GROUP BY billing_city
ORDER BY InvoiceTotal DESC
LIMIT 1
'''
q2 = run_query(q2)
print('\n', q2)


# Question 3: Who is the best customer?
# The customer who has spent the most money will be declared the best customer.
# Build a query that returns the person who has spent the most money.
# Invoice, InvoiceLine, and Customer tables to retrieve this information.
q3 = '''
SELECT customer.customer_id, first_name, last_name, SUM(total) AS total_spending
FROM customer
JOIN invoice ON customer.customer_id = invoice.customer_id
GROUP BY (customer.customer_id)
ORDER BY total_spending DESC
LIMIT 1 
'''
q3 = run_query(q3)
print('\n', q3)


# Use your query to return the email, first name, last name, and Genre of all Rock Music listeners.
# Return your list ordered alphabetically by email address starting with A.
q4 = '''
SELECT DISTINCT email ,first_name , last_name , genre.name
FROM customer
JOIN invoice ON invoice.customer_id = customer.customer_id
JOIN invoice_line ON invoice_line.invoice_id = invoice.invoice_id
JOIN track ON track.track_id = invoice_line.track_id
JOIN genre ON genre.genre_id = track.genre_id
WHERE genre.name LIKE 'Rock'
ORDER BY email
'''
q4 = run_query(q4)
print('\n', q4)


# Question 5: Who is writing the rock music?
# Now that we know that our customers love rock music, we can decide which musicians to invite to play at the concert.
# Let's invite the artists who have written the most rock music in our dataset.
# Write a query that returns the Artist name and total track count of the top 10 rock bands.
q5 = '''
SELECT DISTINCT artist.name, COUNT(track.genre_id) AS total_tracks
FROM artist
JOIN album ON artist.artist_id = album.artist_id
JOIN track ON track.album_id = album.album_id
WHERE genre_id IN(
           SELECT genre_id 
           FROM genre 
           WHERE name LIKE 'Rock'
)
GROUP BY artist.artist_id
ORDER BY total_tracks DESC
LIMIT 10        
'''
q5 = run_query(q5)
print('\n', )


# Question 6: Now use this artist to find which customer spent the most on this artist.
# For this query, you will need to use the Invoice, InvoiceLine, Track, Customer, Album, and Artist tables.
# Notice, this one is tricky because the Total spent in the Invoice table might not be on a single product,
# so you need to use the InvoiceLine table to find out how many of each product was purchased,
# and then multiply this by the price for each artist.
q6 = '''
WITH best_selling_artist AS(
	SELECT artist.artist_id AS artist_id,artist.name AS artist_name,SUM(invoice_line.unit_price*invoice_line.quantity) AS total_sales
	FROM invoice_line
	JOIN track ON track.track_id = invoice_line.track_id
	JOIN album ON album.album_id = track.album_id
	JOIN artist ON artist.artist_id = album.artist_id
	GROUP BY 1
	ORDER BY 3 DESC
	LIMIT 1
)
SELECT bsa.artist_name,SUM(il.unit_price*il.quantity) AS amount_spent,c.customer_id,c.first_name,c.last_name
FROM invoice i
JOIN customer c ON c.customer_id = i.customer_id
JOIN invoice_line il ON il.invoice_id = i.invoice_id
JOIN track t ON t.track_id = il.track_id
JOIN album alb ON alb.album_id = t.album_id
JOIN best_selling_artist bsa ON bsa.artist_id = alb.artist_id
GROUP BY 1,3,4,5
ORDER BY 2 DESC
'''
q6 = run_query(q6)
print('\n',q6)


# Question 7:
# We want to find out the most popular music Genre for each country.
# We determine the most popular genre as the genre with the highest amount of purchases.
# Write a query that returns each country along with the top Genre.
# For countries where the maximum number of purchases is shared return all Genres.
q7 = '''
WITH RECURSIVE
	sales_per_country AS(
		SELECT COUNT(*) AS purchases_per_genre, customer.country, genre.name, genre.genre_id
		FROM invoice_line
		JOIN invoice ON invoice.invoice_id = invoice_line.invoice_id
		JOIN customer ON customer.customer_id = invoice.customer_id
		JOIN track ON track.track_id = invoice_line.track_id
		JOIN genre ON genre.genre_id = track.genre_id
		GROUP BY 2,3,4
		ORDER BY 2
	)
	,max_genre_per_country AS(SELECT MAX(purchases_per_genre) AS max_genre_number, country
		FROM sales_per_country
		GROUP BY 2
		ORDER BY 2)

SELECT sales_per_country.* 
FROM sales_per_country
JOIN max_genre_per_country ON sales_per_country.country = max_genre_per_country.country
WHERE sales_per_country.purchases_per_genre = max_genre_per_country.max_genre_number
'''
q7 = run_query(q7)
print('\n', q7)


# Question 8:
# Return all the track names that have a song length longer than the average song length.
# Though you could perform this with two queries.
# Imagine you wanted your query to update based on when new data is put in the database.
# Therefore, you do not want to hard code the average into your query.
# You only need the Track table to complete this query.
# Return the Name and Milliseconds for each track. Order by the song length with the longest songs listed first.
q8 = '''
SELECT name,milliseconds
FROM track
WHERE milliseconds > (
	SELECT AVG(milliseconds)
	FROM track)
ORDER BY milliseconds DESC
'''
q8 = run_query(q8)
print('\n', q8)


# Question 9:
# Write a query that determines the customer that has spent the most on music for each country.
# Write a query that returns the country along with the top customer and how much they spent.
# For countries where the top amount spent is shared, provide all customers who spent this amount.
# You should only need to use the Customer and Invoice tables.
q9 = '''
WITH RECURSIVE 
	customter_with_country AS (
		SELECT customer.customer_id,first_name,last_name,billing_country,SUM(total) AS total_spending
		FROM invoice
		JOIN customer ON customer.customer_id = invoice.customer_id
		GROUP BY 1,2,3,4
		ORDER BY 5 DESC),

	country_max_spending AS(
		SELECT billing_country,MAX(total_spending) AS max_spending
		FROM customter_with_country
		GROUP BY billing_country)

SELECT cc.billing_country, cc.total_spending,cc.first_name,cc.last_name,cc.customer_id
FROM customter_with_country cc
JOIN country_max_spending ms
ON cc.billing_country = ms.billing_country
WHERE cc.total_spending = ms.max_spending
ORDER BY 1
'''
q9 = run_query(q9)
print('\n', q9)
