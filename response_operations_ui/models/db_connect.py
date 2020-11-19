import psycopg2


def db_connect_and_query(query):
    try:
        print('Attempting to connect to Database')
        connection = psycopg2.connect(
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432",
            database="ras")
        print('Connection Successful')

        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    
    # Converts the list of tuples to a dict
    result = dict(result)
    
    return result
