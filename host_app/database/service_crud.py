
import logging
from .schemas import ServiceSignup
from .models import Service
from host_app.common.util import create_hashed_password, generate_salt, create_order_id
from .sql_constants import CommonConstants
from host_app.caching.redis_constant import RedisConstant
import random
from sqlalchemy.orm import Session
from host_app.common import util
from host_app.routes import verification



def get_service_by_service_id(db: Session, service_id: str):
    try:
        return db.query(Service).filter(Service.service_id == service_id).first()
    except Exception as ex :
        logging.exception("[SERVICE_CRUD][Exception in get_service_by_service_id] {} ".format(ex))


def get_service_by_email(db: Session, email: str):
    try:
        return db.query(Service).filter(Service.registration_mail == email).first()
    except Exception as ex :
        logging.exception("[SERVICE_CRUD][Exception in get_service_by_email] {} ".format(ex))


def get_service_by_service_org(db: Session, service_org: str):
    try:
        return db.query(Service).filter(Service.service_org == service_org).first()
    except Exception as ex :
        logging.exception("[SERVICE_CRUD][Exception in get_service_by_service_org] {} ".format(ex))



async def create_new_service(db: Session, service_user: ServiceSignup):
    try:
        ip_ports = service_user.ip_ports
        ip_ports_str = await util.zipper(ip_ports)
        service_org = service_user.service_org
        alpha_int = random.randint(1,26)

        service_id = service_org + "_" + chr(64 + alpha_int) + str(random.randint(1,999))

        api_key = await verification.get_api_key()
        
        db_user = Service(service_org=service_org, service_id=service_id, service_name = service_user.service_name, registration_mail=service_user.registration_mail, ip_ports=ip_ports_str, api_key=api_key)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        enc_api_key = await verification.get_encrypted_api_key(api_key, ip_ports_str)

        response = await ServiceSignupResponse(db_user, enc_api_key)
        return response

    except Exception as ex :
        logging.exception("[SERVICE_CRUD][Exception in create_new_service] {} ".format(ex))
    return None


async def ServiceSignupResponse(data: Service, enc_api_key):
    # Your processing logic here
    return {
        "service_name": data.service_name,
        "service_org": data.service_org,
        "service_id": data.service_id,
        "enc_api_key": enc_api_key,
        "subscription_mode": data.subscription_mode,
        "daily_request_counts": data.daily_request_counts
    }