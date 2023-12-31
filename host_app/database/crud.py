import logging, random
from host_app.database.schemas import UserSignUp, UserSignUpResponse
from host_app.database.models import Account, Password
from host_app.common.util import create_hashed_password, generate_salt
from host_app.database.sql_constants import CommonConstants
from sqlalchemy.orm import Session
from host_app.common import util
from typing import Optional


def get_user_by_user_id(db: Session, user_id: str, org: Optional[str] = None):
    try:
        if org :
            return db.query(Account).filter(Account.user_id == user_id, Account.service_org == org, Account.account_state == Account.AccountState.ACTIVE).first()

        return db.query(Account).filter(Account.user_id == user_id).first()
    except Exception as ex :
        logging.exception("[CRUD][Exception in get_user_by_user_id] {} ".format(ex))


def get_user_by_email(db: Session, email: str):
    try:
        return db.query(Account).filter(Account.email == email, Account.account_state == Account.AccountState.ACTIVE).first()
    except Exception as ex :
        logging.exception("[CRUD][Exception in get_user_by_email] {} ".format(ex))


# only used for login cases
def get_user_by_email_login(db: Session, email: str):
    try:
        joined_data = (
            db.query(Account, Password)
            .join(Password, Account.user_id == Password.user_id)
            .filter(Account.email == email)
            .all()
        )
        return joined_data
    except Exception as ex :
        logging.exception("[CRUD][Exception in get_user_by_email_login] {} ".format(ex))


async def get_user_by_username(db: Session, username: str):
    try:
        user = db.query(Account).filter(Account.username == username, Account.account_state == Account.AccountState.ACTIVE).first()
        return user

    except Exception as ex :
        logging.exception("[CRUD][Exception in get_user_by_username] {} ".format(ex))


def get_user_by_phone(db: Session, phone: str):
    try:
        return db.query(Account).filter(Account.phone == phone).first()
    except Exception as ex :
        logging.exception("[CRUD][Exception in get_user_by_phone] {} ".format(ex))

async def create_new_user(db: Session, user: UserSignUp):
    try:
        username = user.username
        service_org = user.service_org
        password = user.password
        role = user.role
        if not role :
            role = Account.Role.USER
        role = int(role)
            
        alpha_int = random.randint(1,26)
        if not username :
            username = "User_" + service_org + "_" + str(role) + await util.generate_secure_random_string()

        user_id = service_org + "_" + str(role) + "_" +chr(64 + alpha_int)+ str(random.randint(1000,9999))
        
        db_user = Account(email=user.email, phone=user.phone, user_id=user_id, username=username, service_org=service_org, role=role)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        test_response = {"email":user.email, "phone":user.phone, "user_id":user_id,"username":username, "is_verified" : db_user.is_verified , "role" : db_user.role, "service_org" : db_user.service_org}
        await create_password(db, user_id, password)

        response = UserSignUpResponse.model_validate(test_response)
        return response

    except Exception as ex :
        logging.exception("[CRUD][Exception in create_new_user] {} ".format(ex))
    return None


async def create_password(db:Session, user_id:str, password : str):
    try:
        salt = await generate_salt(CommonConstants.SALT_LENGTH)
        hashed_password = await create_hashed_password(password, salt)
        db_user = Password(user_id=user_id, hashed_password=hashed_password, salt=salt )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


    except Exception as ex :
        logging.exception("[CRUD][Exception in create_password] {} ".format(ex))


async def get_password_data(db: Session, user_id: str):
    try :
        password_data = db.query(Password).filter(Password.user_id == user_id).first()
        return password_data

    except Exception as ex :
        logging.exception("[CRUD][Exception in get_password_data] {} ".format(ex))


async def update_password_data(db: Session, user_id: int, user_update_map: dict):
    try :
        db_user = db.query(Password).filter(Password.user_id == user_id).first()
        if db_user:
            for key, value in user_update_map.items():
                setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
            return db_user
        return None
    except Exception as ex :
        logging.exception("[CRUD][Exception in update_user] {} ".format(ex))


async def update_account_data(db: Session, user_id: int, user_update_map: dict):
    try :
        db_user = db.query(Account).filter(Account.user_id == user_id, Account.account_state == Account.AccountState.ACTIVE).first()
        if db_user:
            for key, value in user_update_map.items():
                setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
            return db_user.to_dict()
        return None
    except Exception as ex :
        logging.exception("[CRUD][Exception in update_user] {} ".format(ex))



def delete_user(db: Session, user_id: str, service_org: str):
    try:
        db_user = db.query(Account).filter(Account.user_id == user_id, Account.service_org == service_org, Account.account_state == Account.AccountState.ACTIVE).first()
        if db_user:
            setattr(db_user, Account.account_state, Account.AccountState.DELETED)
            # db.delete(db_user)
            db.commit()
            obj = db.query(Password).filter(Password.user_id == user_id).first()
            if obj:
                db.delete(obj)
                db.commit()

                return True
        return False
    except Exception as ex :
        logging.exception("[CRUD][Exception in delete_user] {} ".format(ex))


async def get_all_users(db: Session, org: Optional[str] = None, skip: int = 0, limit: int = 100):
    try:
        # Jani na keno ei join krsi 
        # res =  db.query(Account, Orders).join(Orders).filter(Account.id == Orders.owner_id).all()
        # for e in res :
        if org :
            res = db.query(Account).filter(Account.service_org == org, Account.account_state == Account.AccountState.ACTIVE).all()
        else :
            res = db.query(Account).filter(Account.account_state == Account.AccountState.ACTIVE).all()

        res_arr = {}
        for e in res :
            dicu = await e.to_dict()
            res_arr[dicu["user_id"]] = dicu

        return res_arr
    except Exception as ex :
        logging.exception("[CRUD][Exception in get_all_users] {} ".format(ex))


async def get_all_unverified_users(db: Session, org: Optional[str] = None, skip: int = 0, limit: int = 100):
    try:
        # Jani na keno ei join krsi 
        # res =  db.query(Account, Orders).join(Orders).filter(Account.id == Orders.owner_id).all()
        # for e in res :
        if org :
            res = db.query(Account).filter(Account.is_verified == Account.Verification.NOT_VERIFIED, Account.service_org == org, Account.account_state == Account.AccountState.ACTIVE).all()
        else :
            res = db.query(Account).filter(Account.is_verified == Account.Verification.NOT_VERIFIED, Account.account_state == Account.AccountState.ACTIVE).all()

        res_arr = {}
        for e in res :
            dicu = await e.to_dict()
            res_arr[dicu["user_id"]] = dicu

        return res_arr
    except Exception as ex :
        logging.exception("[CRUD][Exception in get_all_users] {} ".format(ex))


