from fastapi import Depends, HTTPException, status, APIRouter
from host_app.common.response_object import ResponseObject
from host_app.database.schemas import UserInDB, OrderCreate, OrderQuery
from sqlalchemy.orm import Session
import logging
from host_app.database import crud
from host_app.database.database import get_db
from host_app.caching import redis_util
from host_app.caching.redis_constant import RedisConstant
from host_app.common import order_util
from host_app.routes import verification
from host_app.common.exceptions import CustomException


order_router = APIRouter(
    prefix='/order',
    tags=['order']
)


@order_router.post("/create")
async def create_order(order_info: OrderCreate, user: UserInDB = Depends(verification.get_current_active_user)):
    responseObject = ResponseObject()
    try: 
        
        user_id = user["user_id"]
        user_org = user["service_org"]
        order = await order_util.create_order(user_id, user_org, order_info)
        
        if not order:
            exp = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to Create New Order",
                headers={"WWW-Authenticate": "Bearer"}
            )
            responseObject.set_exception(exp)
            return responseObject

        responseObject.set_status(status.HTTP_200_OK)
        responseObject.set_data(order)
        
    except Exception as ex:
        logging.exception("[ORDER_ROUTES][Exception in create_order] {} ".format(ex))
    return responseObject


@order_router.get("/")
async def order(user: UserInDB = Depends(verification.get_current_active_user), db: Session = Depends(get_db)):
    try:
        respObj = ResponseObject()
        user_id = user["user_id"]
        user_org = user["service_org"]
        all_orders_obj = await order_util.get_all_orders(db, user_id, user_org)
        
        if not all_orders_obj:
            exp = CustomException(detail="Orders don't exits")
            respObj.set_exception(exp)
            return respObj

        respObj.set_status(status.HTTP_200_OK)
        respObj.set_data(all_orders_obj)

    except Exception as ex:
        logging.exception("[ORDER_ROUTES][Exception in order] {} ".format(ex))
    return respObj



@order_router.get("/{order_id}")
async def get_single_order_info(order_id: str, user: UserInDB = Depends(verification.get_current_active_user), db: Session = Depends(get_db)):
    try:
        respObj = ResponseObject()
        user_id = user["user_id"]
        service_org = user["service_org"]
        order_obj = await order_util.get_single_order(db, user_id, order_id, service_org)
        
        if not order_obj:
            exp = CustomException(detail="Order doesn't exits")
            respObj.set_exception(exp)
            return respObj
        respObj.set_status(status.HTTP_200_OK)
        respObj.set_data(order_obj)

    except Exception as ex :
        logging.exception("[ORDER_ROUTES][Exception in get_single_order_info] {} ".format(ex))
    return respObj



# update and cancel and all
@order_router.post("/update")
async def update_order_status(order_query: OrderQuery, user: UserInDB = Depends(verification.get_current_active_user), db: Session = Depends(get_db)):
    try:
        respObj = ResponseObject()
        user_id = user["user_id"]
        order_data = order_query.model_dump()
        service_org = user["service_org"]
        
        res = await order_util.update_order_object(db, user_id, order_data, service_org)
        
        if not res:
            exp = CustomException(detail="Failed to Update Order")
            respObj.set_exception(exp)
            return respObj
        
        respObj.set_status(status.HTTP_200_OK)
        respObj.set_data(res)
        return respObj
    
    except Exception as ex:
        logging.exception("[ORDER_ROUTES][Exception in update_order_status] {} ".format(ex))
    


# under construction
@order_router.get("/delete/{order_id}")
async def delete_order(order_id: str, user: UserInDB = Depends(verification.get_current_active_user), db: Session = Depends(get_db)):
    try:
        user_id = user["user_id"]

        if order_id  :
            status = crud.delete_order(db, order_id, user_id)
            if status :
                await redis_util.delete_from_redis(RedisConstant.ORDER_OBJ + order_id)
                return {"user_id" : user_id, "order_id" : order_id, "messege":"Order has been Deleted Sucessfully"}
            else :
                return {"user_id" : user_id, "order_id" : order_id, "messege":"Not Authorized"}
                
    except Exception as ex:
        logging.exception("[MAIN][Exception in delete_order] {} ".format(ex))

