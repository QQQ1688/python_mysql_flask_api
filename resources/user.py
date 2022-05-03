import pymysql
from flask_apispec import MethodResource, marshal_with, doc, use_kwargs
import util
from . import user_model
from flask_jwt_extended import create_access_token, jwt_required
from datetime import timedelta


def db_init():
    db = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='root',
        port=3307,
        db='test'
    )

    cursor = db.cursor(pymysql.cursors.DictCursor)
    return db, cursor

def get_access_token(account):
    token = create_access_token(
        identity={"account": account},
        expires_delta=timedelta(days=1)
    )
    return token

####### API Action #########
# Items - shopping functions

class Login(MethodResource):
    @doc(description='User Login', tags=['Login'])
    @use_kwargs(user_model.LoginSchema, location="form")
    @marshal_with(user_model.UserGetResponse, code=200)
    def post(self, **kwargs):
        db, cursor = db_init()
        account, password = kwargs["account"], kwargs["password"]
        sql = f"SELECT * FROM test.member WHERE account = '{account}' AND password = '{password}';"
        cursor.execute(sql)
        user = cursor.fetchall()
        db.close()

        if user != ():
            token = get_access_token(account)
            data = {
                "message": f"Welcome back {user[0]['name']}",
                "token": token}
            return util.success(data)
        
        return util.failure({"message":"Account or password is wrong"})


class Items(MethodResource):
    # GET_ALL
    @doc(description='Get all items.', tags=['Items']) 
    @use_kwargs(user_model.ItemGetSchema, location="query")
    @marshal_with(user_model.UserGetResponse, code=200)
    @jwt_required()
    def get(self, **kwargs):
        db, cursor = db_init()
        prod_name = kwargs.get("prod_name")
        if prod_name is not None:
            sql = f"SELECT * FROM test.items WHERE name = '{prod_name}';"
        else:
            sql = 'SELECT * FROM test.items;'
        cursor.execute(sql)
        users = cursor.fetchall()
        db.close() #一定要加close,不然db會爆掉
        return util.success(users)

    # POST
    @doc(description='Add item.', tags=['Items'])
    @use_kwargs(user_model.ItemPostSchema, location="form")
    @marshal_with(user_model.UserCommonResponse, code=201)
    def post(self, **kwargs):
        db, cursor = db_init()
        item = {
            'prod_name': kwargs['prod_name'],
            'price': kwargs['price'],
            'qty': kwargs['qty'],
            'category': kwargs['category'],
            'note': kwargs.get('note'),
        }

        sql = """

        INSERT INTO `test`.`items` (`prod_name`,`price`,`qty`,`category`,`note`)
        VALUES ('{}','{}','{}','{}','{}');

        """.format(
            item['prod_name'], item['price'], item['qty'], item['category'],  item['note'])
        result = cursor.execute(sql)
        db.commit()  # 測試,將執行成功的結果存進database裡
        db.close()

        if result == 0:
            return util.failure({"message": "error"})

        return util.success()

class Cart(MethodResource):
    # shopping cart
    @doc(description='Add single item to cart.', tags=['Cart'])
    @use_kwargs(user_model.ItemBuySchema, location="form")
    @marshal_with(user_model.UserCommonResponse, code=201)
    @jwt_required()
    def post(self, **kwargs):
        db, cursor = db_init()
        account, password = kwargs["account"], kwargs["password"] 
        item = {
            'prod_name': kwargs['prod_name'],
            'price': kwargs['price'],
            'qty': kwargs['qty'],
            'category': kwargs['category'],
            'note': kwargs.get('note'),
        }
        
        # 創建顧客購物車 table
        sql = f"""
            CREATE TABLE IF NOT EXISTS cart_{account} (
                _id int NOT NULL AUTO-INCREMENT, 
                prod_name    VARCHAR(50)     NOT NULL,
                price   int NOT NULL,
                qty     int NOT NULL),
            PRIMARY KEY (_id)
            );
            """ 
        cursor.execute(sql)

        # 檢查庫存
        
        sql2 = f"SELECT qty FROM test.items WHERE name = {item['name']}"
        cursor.execute(sql2)
        stock = cursor.fetchone()
        if stock < item['qty']:  
            return "庫存不足"
        else:
            # 如果庫存 > 訂購數量，則將商品加入顧客的專屬購物車表格
            sql3 = f"INSERT INTO `test`.`cart_{account}` (`name`, `price`, `qty`) VALUES \
                ({item['name']}, {item['price']}, {item['qty']});"
            cursor.execute(sql3)
            update_stock = f"""
            
                UPDATE `test`.'cart_{account}`
                SET qty = qty - {item['qty']}
  
            """
            cursor.execute(update_stock)

            # 算出顧客購物清單內商品總價
            sql4 = f"SELECT SUM(qty * price) FROM test.cart{account}"
            result = cursor.execute(sql4)
            amount = cursor.fetchall()
            db.commit()  # 測試,將執行成功的結果存進database裡
            db.close()
            
            

        if result == 0:
            return util.failure({"message": "error"})

        return util.success({'message': f'shopping amount = {amount}'})

 


class Item(MethodResource):
    @doc(description='Get Single item info.', tags=['Item'])
    @marshal_with(user_model.UserGetResponse, code=200)
    @jwt_required()
    def get(self, _id):
        db, cursor = db_init()
        sql = f"SELECT * FROM test.member WHERE _id = '{_id}';"
        cursor.execute(sql)
        users = cursor.fetchall()
        db.close()
        return util.success(users)

    @doc(description='Update item info.', tags=['item'])
    @use_kwargs(user_model.ItemPatchSchema, location="form")
    @marshal_with(user_model.UserCommonResponse, code=201)
    def patch(self, _id, **kwargs):
        db, cursor = db_init()
        item = {
            'prod_name': kwargs['name'],
            'price': kwargs['price'],
            'qty': kwargs['qty'],
            'category': kwargs['category'],
            'note': kwargs.get('note'),
        }
        query = []
        for key, value in item.items():
            if value is not None:
                query.append(f"{key} = '{value}'")
        query = ",".join(query)

        sql = """
            UPDATE `test`.`items`
            SET {}
            WHERE id = {};
        """.format(query, _id)

        result = cursor.execute(sql)
        db.commit()
        db.close()
        if result == 0:
            return util.failure({"message": "error"})

        return util.success()

    @doc(description='Delete item info.', tags=['item'])
    @marshal_with(None, code=204)
    def delete(self, _id):
        db, cursor = db_init()
        sql = f'DELETE FROM `test`.`items` WHERE _id = {_id};'
        result = cursor.execute(sql)
        db.commit()
        db.close()



# Users - member functions
class Login(MethodResource):
    @doc(description='User Login', tags=['Login'])
    @use_kwargs(user_model.LoginSchema, location="form")
    @marshal_with(user_model.UserGetResponse, code=200)
    def post(self, **kwargs):
        db, cursor = db_init()
        account, password = kwargs["account"], kwargs["password"]
        sql = f"SELECT * FROM test.member WHERE account = '{account}' AND password = '{password}';"
        cursor.execute(sql)
        user = cursor.fetchall()
        db.close()

        if user != ():
            token = get_access_token(account)
            data = {
                "message": f"Welcome back {user[0]['name']}",
                "token": token}
            return util.success(data)
        
        return util.failure({"message":"Account or password is wrong"})


class Users(MethodResource):
    # GET_ALL
      
    @use_kwargs(user_model.UserGetSchema, location="query")
    @marshal_with(user_model.UserGetResponse, code=200)
    @jwt_required()
    def get(self, **kwargs):
        db, cursor = db_init()
        name = kwargs.get("name")
        if name is not None:
            sql = f"SELECT * FROM test.member WHERE name = '{name}';"
        else:
            sql = 'SELECT * FROM test.member;'
        cursor.execute(sql)
        users = cursor.fetchall()
        db.close() #一定要加close,不然db會爆掉
        return util.success(users)

    # POST
    @doc(description='Create User.', tags=['User'])
    @use_kwargs(user_model.UserPostSchema, location="form")
    @marshal_with(user_model.UserCommonResponse, code=201)
    def post(self, **kwargs):
        db, cursor = db_init()
        user = {
            'name': kwargs['name'],
            'account': kwargs['account'],
            'password': kwargs['password'],
            'gender': kwargs['gender'],
            'birth': kwargs.get('birth') or '1900-01-01',
            'note': kwargs.get('note'),
        }

        sql = """

        INSERT INTO `test`.`member` (`name`,`gender`,`account`,`password`,`birth`,`note`)
        VALUES ('{}','{}','{}','{}','{}','{}');

        """.format(
            user['name'], user['gender'], user['account'], user['password'], user['birth'], user['note'])
        result = cursor.execute(sql)
        db.commit()  # 測試,將執行成功的結果存進database裡
        db.close()

        if result == 0:
            return util.failure({"message": "error"})

        return util.success()


class User(MethodResource):
    @doc(description='Get Single user info.', tags=['User'])
    @marshal_with(user_model.UserGetResponse, code=200)
    @jwt_required()
    def get(self, id):
        db, cursor = db_init()
        sql = f"SELECT * FROM test.member WHERE id = '{id}';"
        cursor.execute(sql)
        users = cursor.fetchall()
        db.close()
        return util.success(users)

    @doc(description='Update User info.', tags=['User'])
    @use_kwargs(user_model.UserPatchSchema, location="form")
    @marshal_with(user_model.UserCommonResponse, code=201)
    def patch(self, id, **kwargs):
        db, cursor = db_init()
        user = {
            'name': kwargs.get('name'),
            'account': kwargs.get('account'),
            'password': kwargs.get('password'),
            'gender': kwargs.get('gender'),
            'birth': kwargs.get('birth') or '1900-01-01',
            'note': kwargs.get('note')
        }

        query = []
        for key, value in user.items():
            if value is not None:
                query.append(f"{key} = '{value}'")
        query = ",".join(query)

        sql = """
            UPDATE `test`.`member`
            SET {}
            WHERE id = {};
        """.format(query, id)

        result = cursor.execute(sql)
        db.commit()
        db.close()
        if result == 0:
            return util.failure({"message": "error"})

        return util.success()

    @doc(description='Delete User info.', tags=['User'])
    @marshal_with(None, code=204)
    def delete(self, id):
        db, cursor = db_init()
        sql = f'DELETE FROM `member`.`users` WHERE id = {id};'
        result = cursor.execute(sql)
        db.commit()
        db.close()
        if result == 0:
            return util.failure({"message": "error"})

        return util.success()        
        

