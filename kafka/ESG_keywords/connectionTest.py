from pymongo import MongoClient

try:
    MONGO_URI = "mongodb+srv://jinpang97:MONGOsj!0122@cluster0.bxnwcsi.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(MONGO_URI)
    db = client["CrawlData"]
    collection = db["crawlingPreprocessing"]

    # 테스트 insert
    test_doc = {"test": "connection check"}
    collection.insert_one(test_doc)
    print("✅ MongoDB Atlas 연결 및 저장 성공!")
except Exception as e:
    print("❌ 연결 실패:", e)
