from azure.cosmos import CosmosClient, PartitionKey, exceptions,ContainerProxy

def get_container(Cosmos_Endpoint:str,Cosmos_Key:str,Cosmos_Database:str,Cosmos_Container:str)->ContainerProxy:
    cosmos_client = CosmosClient(Cosmos_Endpoint, credential=Cosmos_Key)
    database_client = cosmos_client.get_database_client(Cosmos_Database)
    container_client = database_client.get_container_client(Cosmos_Container)  
    return container_client