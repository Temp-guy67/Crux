import logging
from host_app.database.sql_constants import CommonConstants
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from host_app.caching import redis_util
from host_app.caching.redis_constant import RedisConstant
from host_app.database import crud, service_crud
from host_app.database.database import get_db
from host_app.common import util
from host_app.routes import verification
from host_app.common.exceptions import Exceptions, CustomException


def update_access_token_in_redis(user_id:str, access_token: str):
    try :
        redis_util.set_str(access_token, user_id, 1800)

    except Exception as ex :
        logging.exception("[common_util][Exception in update_access_token_in_redis] {} ".format(ex))


async def update_user_details_in_redis(user_id:str, user_obj: dict):
    try :
        await redis_util.set_hm(user_id, user_obj, 1800)

    except Exception as ex :
        logging.exception("[common_util][Exception in update_user_details_in_redis] {} ".format(ex))

async def get_user_details(user_id, db: Session = Depends(get_db)):
    try :
        user_details = await redis_util.get_hm(user_id)
        if not user_details :
            user_details = crud.get_user_by_user_id(db,user_id)

        return user_details

    except Exception as ex :
        logging.exception("[common_util][Exception in get_user_details] {} ".format(ex))

        

async def update_password(user:dict, password, new_password, db: Session = Depends(get_db)):
    try:
        user_id = user["user_id"]
        password_obj = await crud.get_password_data(db, user_id)

        if await verification.verify_password(password, password_obj.hashed_password, password_obj.salt):

            new_salt = await util.generate_salt(CommonConstants.SALT_LENGTH)
            new_hashed_password = await util.create_hashed_password(new_password, new_salt)
            data = {"salt": new_salt, "hashed_password" : new_hashed_password} 
            res = await crud.update_password_data(db, user_id, data)
            if res :
                await redis_util.delete_from_redis(user_id)
                
            return {"user_id" : user_id, "messege":"Password has been Updated Sucessfully"}
        else :
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password is wrong",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as ex :
        logging.exception("[common_util][Exception in update_password] {} ".format(ex))
             
        
async def delete_api_cache_from_redis(api_key: str):
    try:
        await redis_util.delete_from_redis(api_key + RedisConstant.IP_PORTS_SET)
        await redis_util.delete_from_redis(api_key + RedisConstant.DAILY_REQUEST_LEFT)
        await redis_util.delete_from_redis(api_key + RedisConstant.SERVICE_ID)
        await redis_util.delete_from_redis(api_key + RedisConstant.IS_SERVICE_VERIFIED)
        print(" Deleted all the cache")

    except Exception as ex :
        logging.exception("[VERIFICATION][Exception in delete_api_cache_from_redis] {} ".format(ex))


async def add_api_cache_to_redis(api_key: str,service_id: str, daily_req_left: int, is_service_verified: int, ip_ports_list: list):
    try:
        redis_util.set_str(api_key + RedisConstant.IS_SERVICE_VERIFIED, str(is_service_verified), 86400) 

        redis_util.set_str(api_key + RedisConstant.SERVICE_ID, service_id , 86400)

        for ip_port in ip_ports_list:
            await redis_util.add_to_set_str_val(api_key + RedisConstant.IP_PORTS_SET, ip_port, 86400)
            
        if daily_req_left > 0 :
            redis_util.set_str(api_key + RedisConstant.DAILY_REQUEST_LEFT, str(daily_req_left - 1), 86400)
        print(" Data added in Redis [Service Id]" ,service_id )

    except Exception as ex :
        logging.exception("[VERIFICATION][Exception in delete_api_cache_from_redis] {} ".format(ex))
        
        

# Common update, it will update anything literally except password and return a boolean 
# But reaching upto here is fuckin impossible without proper authentication.


async def update_account_info(user_id: int, user_update_map_info: dict, db: Session = Depends(get_db)):
    try:
        # username, email and phone
        user_update_map = dict()
        possible_update = ["email", "phone", "username" , "is_verified"]
        
        for k,v in user_update_map_info.items():
            if k == possible_update[0]:
                res = crud.get_user_by_email()
                if res :
                    return Exceptions.EMAIL_HAS_BEEN_REGISTERED
                
            if k == possible_update[1]:
                res = crud.get_user_by_phone()
                if res :
                    return Exceptions.PHONE_NUMBER_HAS_BEEN_REGISTERED
            if k in possible_update :
                user_update_map[k] = v
        
        updated_user_data = await crud.update_account_data(db, user_id, user_update_map)
        
        if updated_user_data :
            update_user_details_in_redis(user_id, updated_user_data)
            return 1
        else :
            return -1
        
        
    except Exception as ex :
        logging.exception("[VERIFICATION][Exception in update_account_info] {} ".format(ex))
        

# under supervision
async def update_service_info(service_id: int, service_update_data: dict, db: Session = Depends(get_db)):
    try:
        # service name and IP ports
        possible_update = ["service_name", "ip_ports"]
        service_update_map = dict()
        
        for k,v in service_update_data.items():
            if k in possible_update :
                if type(v) != str :
                    v = str(v)
                service_update_map[k] = v
        await service_crud.update_service_data(db, service_id, service_update_map)
    except Exception as ex :
        logging.exception("[VERIFICATION][Exception in update_service_info] {} ".format(ex))


async def get_service_details(api_key: str):
    try:
        service_obj = dict()

        service_org = await redis_util.get_str(RedisConstant.SERVICE_ORG + api_key)
        if service_org :
            service_org = await redis_util.get_str(RedisConstant.SERVICE_ORG + api_key)
            is_service_verified = await redis_util.get_str(RedisConstant.IS_SERVICE_VERIFIED + api_key)
            daily_request_count = await redis_util.get_str(RedisConstant.DAILY_REQUEST_LEFT + api_key)
            ip_ports = await redis_util.get_str(RedisConstant.IP_PORTS_SET + api_key)
            
        else :
            service_db_obj = service_crud.get_service_by_api_key(api_key)
            if service_db_obj :
                service_org = service_obj["service_org"]
                is_service_verified = service_obj["is_service_verified"]
                daily_request_count = service_obj["daily_request_count"]
                ip_ports = service_obj["ip_ports"]
            else :
                return CustomException(detail="User Not Available")

        service_obj["service_org"] = service_org
        service_obj["is_service_verified"] = int(is_service_verified)
        service_obj["daily_request_count"] = int(daily_request_count)
        service_obj["ip_ports"] = ip_ports

        await redis_util.set_str(RedisConstant.SERVICE_ORG + api_key, service_org, 86400)
        await redis_util.set_str(RedisConstant.IS_SERVICE_VERIFIED + api_key, str(is_service_verified), 86400)
        await redis_util.set_str(RedisConstant.DAILY_REQUEST_LEFT + api_key, str(daily_request_count), 86400)
        await redis_util.set_str(RedisConstant.IP_PORTS_SET + api_key, ip_ports, 86400)

        return service_obj
    
    except Exception as ex :
        logging.exception("[Common_Util][Exception in get_service_details] {} ".format(ex))


def update_daily_req_counts(api_key:str, daily_req_left:int):
    redis_util.set_str(RedisConstant.DAILY_REQUEST_LEFT + api_key, str(daily_req_left), 86400)


def update_service_verified_api(api_key:str, verification:int):
    redis_util.set_str(RedisConstant.IS_SERVICE_VERIFIED + api_key, str(verification), 86400)