from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import numpy as np

# Milvus 서버에 연결
connections.connect("default", host='localhost', port='19530')

# 컬렉션 생성을 위한 스키마 정의
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=128)
]
schema = CollectionSchema(fields, description="Test collection")

# 컬렉션 생성
collection_name = "example_collection"
if not utility.has_collection(collection_name):
    collection = Collection(name=collection_name, schema=schema)

# 랜덤 벡터 데이터 생성 및 삽입
num_vectors = 1000
dimension = 128
data = np.random.random((num_vectors, dimension)).astype(np.float32).tolist()
mr = collection.insert([data])

# 인덱스 생성 (예: IVF_FLAT)
collection.create_index(field_name="embedding", index_params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 100}})

# 데이터 삽입 후 검색 수행
collection.load()
search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
query_vectors = np.random.random((10, dimension)).astype(np.float32).tolist() # 10개의 쿼리 벡터 생성
results = collection.search(query_vectors, "embedding", search_params, limit=5)

for i, result in enumerate(results):
    print(f"Query {i}:")
for res in result:
    print(f" - ID: {res.id}, Distance: {res.distance}")

collection.release()

connections.disconnect("default")
