import json

class StorePendingId:
    def __init__(self):
        if not json.loads(self.read_file()):
            with open("pending.db", "w") as db:
                db.write(json.dumps("[]", indent = 4))
    def read_file(self):
        with open("pending.db") as db:
            data = db.read()
            return json.loads(data)
    def write_file(self, updated_content):
        with open("pending.db", "w") as db:
            db.write(json.dumps(updated_content))
    def save_data(self, data):
        db = json.loads(self.read_file())
        print("Saved Data", db)
        print(type((db)))
        db.append(data) # prev_db_content = db
        self.write_file(json.dumps(db)) # update db
    def delete_data(self, id):
        db = json.loads(self.read_file())
        updated_content = filter(lambda data: data['id'] != id, db)
        new_updated_content_bucket = list()
        for content in updated_content:
            new_updated_content_bucket.append(content)
        self.write_file(json.dumps(new_updated_content_bucket))
    def find_id(self, id):
        db = json.loads(self.read_file())
        for data in db:
            if data['id'] == id:
                return data
    def clear():
        with open("pending.db", "w") as db:
            db.write(json.dumps("[]", indent = 4))
insert = False
store_pending = StorePendingId()
dummy_data1 = {"id": "lkja2oi2hao2l", "name": "mark"}
dummy_data2 = {"id": "asdlkfjalka", "name": "david"}
dummy_data3 = {"id": "ekwlkjekoslsblx", "name": "solomon"}
if insert:
    store_pending.save_data(dummy_data1)
    store_pending.save_data(dummy_data2)
    store_pending.save_data(dummy_data3)
print(store_pending.find_id("lkja2oi2hao2l"))
store_pending.delete_data("lkja2oi2hao2l")
