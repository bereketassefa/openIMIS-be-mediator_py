import requests
from django.conf import settings
import json
from .models import EMRServer
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import re
def fetch_data_from_server():
    EMR_list = EMRServer.objects.all()
    results = []
    
    session = requests.Session()
    
    try:
        for server in EMR_list:
            try:
                response = session.get(server.api_endpoint, timeout=10)
                
                response.raise_for_status()
                
                data = response.json()
                
                results.append(data)
                
                if data:
                    server.last_claim_id = data[-1]['id'] 
                    server.save()
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {server}: {str(e)}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {server}: {str(e)}")
                
    finally:
        session.close()
    print(f"claims length {len(results)}")
    save_claims_to_db(results)
    
    return results


def save_claims_to_db(claims):

    url='http://127.0.0.1:8000/api/graphql'
    login_query = """
        mutation authenticate($username: String!, $password: String!) {
            tokenAuth(username: $username, password: $password) {
              refreshExpiresIn
            }
          }
    """
    credentials = {
        "username": "Admin",
        "password": "admin123"
    }
    try:
        jwt_token = get_jwt_token(url, login_query, credentials)
        print(f"Extracted JWT token: {jwt_token}")
        transport = RequestsHTTPTransport(
            url=url,
            verify=True,
            retries=3,
            headers={'cookie': f'JWT={jwt_token}'}
        )

        client = Client(transport=transport, fetch_schema_from_transport=True)
        mutation = gql("""
            mutation createClaim(
            $code: ClaimCodeInputType!,
            $insureeId: Int!,
            $dateFrom: Date!,
            $icdId: Int!,
            $dateClaimed: Date!,
            $healthFacilityId: Int!
            ) {
            createClaim(
                input: {
                code: $code,
                insureeId: $insureeId,
                dateFrom: $dateFrom,
                icdId: $icdId,
                dateClaimed: $dateClaimed,
                healthFacilityId: $healthFacilityId
                }
            ) {
                clientMutationId
                internalId
            }response
            }
        """)
        for index , claim in claims:
            try:
                mutation_variables = {
                    "code": claim['code'],
                    "insureeId": claim['insuree_id'],
                    "dateFrom": claim['date_from'],
                    "icdId": claim['icd_id'],
                    "dateClaimed": claim['date_claimed'],
                    "healthFacilityId": claim['health_facility_id']
                }
                print("data send" , mutation_variables)
                result = client.execute(mutation, variable_values=mutation_variables)
                print("Mutation response:")
                print(result)
            except Exception as e:
                print(f"Error saving claim {claim}: {str(e)}")
    except Exception as e:
        print(f"Error receiving JWT token: {e}")



def get_jwt_token(url, query, variables=None):

    transport = RequestsHTTPTransport(url=url, verify=True)
    
    client = Client(transport=transport)
    
    gql_query = gql(query)
    
    try:
        response = client.execute(gql_query, variable_values=variables)
        
        set_cookie = transport.session.headers.get('set-cookie', '')
        print(f"Set-Cookie header: {transport.session}")
        
        jwt_match = re.search(r'JWT=([^;]+)', set_cookie)
        
        if jwt_match:
            jwt_token = jwt_match.group(1)
            return jwt_token
        else:
            raise ValueError("No JWT token found in set-cookie header")
            
    except Exception as e:
        raise Exception(f"Error getting JWT token: {str(e)}")
