
import requests
from requests.auth import HTTPBasicAuth

def reset_leaderboard():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    url = 'https://5269989.pythonanywhere.com/delete_all_scores'
    
    try:
        # Send the DELETE request with the Authentication
        response = requests.delete(url, auth=HTTPBasicAuth(username, password))

        if response.status_code == 200:
            print("All scores have been deleted successfully!")
        else:
            try:
                error_data = response.json()
                print(f"Failed to delete scores. Error: {error_data}")
            except requests.exceptions.JSONDecodeError:
                # If decoding fails, prints the error
                print(f"Failed to delete scores. Reason: {response.text}")

    except requests.RequestException as e:
        print(f"An error occurred: {e}")

reset_leaderboard()
