import requests
from django.conf import settings
import json
from .models import EMRServer
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
    
    save_claims_to_db(results)
    
    return results


def save_claims_to_db(claims):

    url='http://127.0.0.1:8000/api/graphql'
    
    try:
        credentialresponse = get_jwt_token(url)
        print(f"Credential response: {credentialresponse.len()}")
        jwt , session = credentialresponse.values()
        csrf_token = get_csrf_token(url ,jwt , session)
        for index , claim in claims:
            try:
                print(f"Saving claim {index} to database")
                print(f"Claim data: {claim}")
                mutation_variables = {
                    "input": {
                        "clientMutationLabel": f"Create Claim - {claim['code']}",
                        "code": claim["code"],
                        "insureeId": claim["insureeId"],
                        "dateFrom": claim["dateFrom"],
                        "icdId": claim["icdId"],
                        "dateClaimed": claim["dateClaimed"],
                        "healthFacilityId": claim["healthFacilityId"],
                        "services": [
                            {
                                "serviceId": service["serviceId"],
                                "priceAsked": service["priceAsked"],
                                "qtyProvided": service["qtyProvided"],
                                "serviceServiceSet": service.get("serviceServiceSet", []),
                                "serviceItemSet": service.get("serviceItemSet", []),
                                "status": service["status"]
                            }
                            for service in claim["services"]
                        ]
                    }
                }
                query = """
                   type Mutation {
                        createClaim(input: {
                            clientMutationLabel: String
                            code: String!
                            insureeId: Int!
                            dateFrom: String!
                            icdId: Int!
                            dateClaimed: String!
                            healthFacilityId: Int!
                            services: [{
                                serviceId: Int!
                                priceAsked: String!
                                qtyProvided: String!
                                status: Int!
                            }]!
                        }){
                            clientMutationId: String
                            internalId: String
                        }
                    }"""
                headers = {
                    "Cookie": f"JWT={jwt}; openimis_session={session}",
                    'Content-Type': 'application/json',
                    'x-csrftoken': csrf_token
                }
                print("Mutation response:")
                response = requests.post(url, headers=headers, json={'query': query, 'variables': mutation_variables})
                response.raise_for_status()
                result = response.json()
                print("Mutation response:")
                print(result)
            except Exception as e:
                print(f"Error saving claim {claim}: {str(e)}")
    except Exception as e:
        print(f"Error receiving JWT token: {e}")

def get_jwt_token(url):
    query = """
        mutation authenticate($username: String!, $password: String!) {
            tokenAuth(username: $username, password: $password) {
              refreshExpiresIn
            }
          }
    """
    variables = {
        "username": "Admin",
        "password": "admin123"
    }
    try:

        response = requests.post(url, json={"query": query,"variables":variables}) 
        response.raise_for_status() 
        
        set_cookie_value = response.headers.get('Set-Cookie', '')

      
        jwt_match = re.search(r'JWT=([^;]+)', set_cookie_value)
        session_match = re.search(r'openimis_session=([^;]+)', set_cookie_value)
        if jwt_match and session_match:
            jwt_token = jwt_match.group(1)
            session_token = session_match.group(1)
            print(f"jwt_token: {jwt_token}")
            print(f"session_token: {session_token}")
            return (jwt_token , session_token)
        else:
            raise ValueError("No JWT token or session found in set-cookie header")
            
    except Exception as e:
        print(f"Error getting JWT token: {str(e)}")

def get_csrf_token(url ,jwt , session):
    query = """
        mutation {
        getCsrfToken {
            csrfToken
        }
        }
    """
    headers = {
        "Cookie": f"JWT={jwt}; openimis_session={session}"
    }
    try:
        response = requests.post(url, json={"query": query}, headers=headers)
        response.raise_for_status()

        data = response.json()
        csrf_token = data.get('data', {}).get('getCsrfToken', {}).get('csrfToken')

        if not csrf_token:
            raise ValueError("No CSRF token found in response")
        return csrf_token

    except requests.exceptions.RequestException as e:
        raise Exception(f"HTTP error occurred: {str(e)}") from e
    except json.JSONDecodeError as e:
        raise Exception("Response content is not valid JSON") from e
