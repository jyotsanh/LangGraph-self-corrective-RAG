from pymilvus import connections, utility

# Connect to Milvus
connections.connect("default", host="192.168.1.100", port="19530")

# List all collections
collections = utility.list_collections()
print("Collections in Milvus:", collections)
