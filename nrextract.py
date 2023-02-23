#!/usr/bin/env python
import requests, argparse, tempfile, json, os, uuid, time
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from config import newrelic_user_key, newrelic_account_id, azure_connection_string, azure_container, queries

def nerdgraph_nrql(anum, key, q):
    query = """
    {
      actor {
        account(id: %s) {
          nrql(query: "%s", async: true) {
            results
            queryProgress {
              queryId
              completed
              retryAfter
              retryDeadline
              resultExpiration
            }
          }
        }
      }
    }""" % (anum, q)

    endpoint = "https://api.newrelic.com/graphql"
    headers = {'API-Key': f'{key}'}
    response = requests.post(endpoint, headers=headers, json={"query": query})

    if response.status_code == 200:
        dict_response = json.loads(response.content)['data']['actor']['account']['nrql']
        if dict_response['queryProgress']['completed']:
            return json.dumps(dict_response['results'], indent=4)
        else:
            print("Query requires more time to complete, waiting for results...")
            completed = False
            retryAfter = dict_response['queryProgress']['retryAfter']
            queryid = dict_response['queryProgress']['queryId']
            print(f'queryId is {queryid}')
            query = """
            {
              actor {
                account(id: %s) {
                  nrqlQueryProgress(queryId: "%s") {
                    results
                    queryProgress {
                      queryId
                      completed
                      retryAfter
                      retryDeadline
                      resultExpiration
                    }
                  }
                }
              }
            }""" % (anum, queryid)
            while not completed:
                print(f'Sleeping for {retryAfter} seconds...')
                time.sleep(retryAfter)
                response = requests.post(endpoint, headers=headers, json={"query": query})
                if response.status_code == 200:
                    dict_response = json.loads(response.content)['data']['actor']['account']['nrqlQueryProgress']
                    completed = dict_response['queryProgress']['completed']
                    retryAfter = dict_response['queryProgress']['retryAfter']
                    if completed:
                        return json.dumps(dict_response['results'], indent=4)
                else:
                    raise Exception(f'Nerdgraph query failed with a {response.status_code}.')
    else:
        raise Exception(f'Nerdgraph query failed with a {response.status_code}.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract Learn Production New Relic data and push to Azure.')
    parser.add_argument('-p', '--path', default=None, help='Path to save JSON files; default is to only push to Azure')
    parser.add_argument('-l', '--localonly', action='store_true', help='Skip uploading to Azure')
    args = parser.parse_args()
    if args.path:
        tmpdirname = args.path
        print('Files will be saved.')
    else:
        tmpdir = tempfile.TemporaryDirectory()
        tmpdirname = tmpdir.name
    print(f'Writing files to "{tmpdirname}"')
    if args.localonly:
        print('Files will not be uploaded to Azure.')

    try:
        blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
        print(f'A total of {len(queries)} queries will be run.')
        for q in queries:
            print(f'Running query for {q["name"]}')
            jsondata = nerdgraph_nrql(newrelic_account_id, newrelic_user_key, q['query'])
            data=json.loads(jsondata)
            print(f'Query returned {len(data)} results.')
            filename = f'{q["name"]}.json'
            filepath = os.path.join(tmpdirname, filename)
            print(f'Writing file "{filepath}"')
            f = open(filepath, 'w')
            f.write(jsondata)
            f.close()
            if not args.localonly:
                blob_client = blob_service_client.get_blob_client(container=azure_container, blob=filename)
                print(f'Uploading to Azure Storage in container "{azure_container}" as blob "{filename}"')
                with open(file=filepath, mode="rb") as data:
                    blob_client.upload_blob(data)

    except Exception as ex:
        print('Exception:')
        print(repr(ex))
