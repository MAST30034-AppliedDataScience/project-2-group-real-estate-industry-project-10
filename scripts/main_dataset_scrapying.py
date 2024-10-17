import requests
from pyquery import PyQuery as pq
import json
import re
import pandas as pd
from fake_useragent import UserAgent

# Define output file path
output_csv = '../data/landing/domain_data/rent_data.csv'

# Create a fake UserAgent
user_agent = UserAgent()

# Create a session and set User-Agent to Chrome
session = requests.Session()
session.headers.update({'User-Agent': user_agent.chrome})

# To store all property data
total_data = []

# Iterate over the range of postcodes
for postcode in range(3000, 3997):
    for page_num in range(1, 51):
        print('-' * 50)
        print(f"Current postcode: {postcode}, page {page_num}")
        
        general_url = f"https://www.domain.com.au/rent/?excludedeposittaken=1&ssubs=0&sort=suburb-asc&postcode={postcode}&page={page_num}"
        # Send the request and parse the response as HTML
        response = session.get(general_url)
        html_content = pq(response.text)
        
        # Search for the string containing the necessary information and parse it as JSON
        try:
            aim_str = re.findall(r'application/json">(.*?)</script', response.text, re.S)[0]
            info = json.loads(aim_str)
        except IndexError:
            print("JSON data not found, skipping this page.")
            continue
        
        # Retrieve the room IDs and information on the current page
        room_ids = info['props']['pageProps']['componentProps']['listingSearchResultIds']
        if not room_ids:
            break  # Exit the loop if there are no listings
        
        room_infos = info['props']['pageProps']['componentProps']['listingsMap']
        
        # Iterate through each room and extract the relevant information
        for room_id in room_ids:
            cur = room_infos.get(str(room_id), {})
            cur_sum = cur.get('listingModel', {})
            
            address = cur_sum.get('address', {})
            features = cur_sum.get('features', {})
            price = cur_sum.get('price', '')
            
            # Construct the URL for the listing details and send a request for more information
            sub_url = 'https://www.domain.com.au' + cur_sum.get('url', '')
            sub_response = session.get(sub_url)
            sub_html = pq(sub_response.text)
            
            # Get property features
            property_list = sub_html('ul.css-4ewd2m>li')
            property_features = ','.join([item.text() for item in property_list.items()])
            
            # Get distances to nearby schools
            school_list = sub_html('li[data-testid="fe-co-school-catchment-school"]')
            school = ','.join([item.text().replace('\n', '') for item in school_list.items()])
            
            # Store the extracted information in a dictionary
            single_room = {
                'price': price,
                'bathrooms': features.get('bath', 0),
                'bedrooms': features.get('beds', 0),
                'parking': features.get('parking', 0),
                'type': features.get('propertyTypeFormatted', ''),
                'street': address.get('street', ''),
                'suburb': address.get('suburb', ''),
                'postcode': address.get('postcode', ''),
                'latitude': address.get('lat', ''),
                'longitude': address.get('lng', ''),
                'school': school,
                'features': property_features
            }
            
            # Add the room information to the total data list
            total_data.append(single_room)

# Convert the data into a DataFrame and save it as a CSV file
df = pd.DataFrame(total_data, dtype=str)
df.to_csv(output_csv, index=False)


print(f"Data successfully saved to {output_csv}")