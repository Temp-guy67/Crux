from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from host_app.common.util import zipper,unzipper


class Account(Base):
    class Verification:
        NOT_VERIFIED=0
        VERIFIED=1

    class Role:
        USER=1
        ADMIN=2
        SUPER_ADMIN=3

    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    user_id = Column(String, index=True, unique=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    is_verified = Column(Integer, default=Verification.NOT_VERIFIED)
    created_time = Column(DateTime, default=func.now())
    role = Column(Integer, default=Role.USER)
    last_login_time = Column(DateTime, onupdate=func.now())
    service_org = Column(String, unique=True, nullable=False)

    # items = relationship("Order", back_populates="owner")
    async def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'is_verified': self.is_verified,
            'role': self.role,
            'service_org' : self.service_org
        }


class Password(Base):
    __tablename__ = "password"
    id = Column(Integer,  primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, ForeignKey("account.user_id"))
    hashed_password = Column(String)
    salt = Column(String, unique=True, nullable=False)
    last_updated_time = Column(DateTime, onupdate=func.now())


class Orders(Base):
    class PaymentStatus:
        DUE=1
        PAID=2
        FAILED=3

    class OrderStatus:
        IN_CART=1
        ORDERED=2
        IN_TRANSIT=3
        DELIVERED=4
        FAILED=5
        CANCELLED=6


    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(String, unique=True)
    product_id = Column(String, nullable=False)
    order_quantity = Column(Integer, default=1)
    order_status = Column(Integer, default=OrderStatus.ORDERED)
    payment_status = Column(Integer, default= PaymentStatus.DUE)
    receivers_mobile = Column(String, nullable=False)
    delivery_address = Column(String, nullable=False)
    owner_id = Column(String, ForeignKey("account.user_id"))
    created_time = Column(DateTime, default=func.now())
    last_update_time = Column(DateTime, onupdate=func.now(), nullable=True)
    service_org = Column(String, unique=True, nullable=False)

    # owner = relationship("Account", back_populates="order")



    def to_dict(self):
        return {
            'order_id': self.order_id,
            'product_id': self.product_id,
            'order_status': self.order_status,
            'payment_status': self.payment_status,
            'delivery_address': self.delivery_address,
            'created_time' : str(self.created_time),
            'owner_id' : self.owner_id,
            'receivers_mobile' : self.receivers_mobile,
            'order_quantity' : self.order_quantity,
            'last_update_time' : str(self.last_update_time),
            'service_org' : self.service_org
        }



class Service(Base):
    class Subsription:
        TEST="TEST"
        FREE="FREE"
        NOOB="NOOB"
        PRO="PRO"
        ULTRA_PRO="ULTRA_PRO"

    class RequestCounts:
        TEST=5
        FREE=50
        NOOB=500
        PRO=1000
        ULTRA_PRO=2000
    
    class ClientVerification:
        NOT_VERIFIED=0
        VERIFIED=1

    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    service_id = Column(String, unique=True, nullable=False)              #zsoid
    service_org = Column(String, nullable=False, unique=True)
    service_name = Column(String, nullable=False)
    subscription_mode = Column(String, default=Subsription.TEST)
    daily_request_counts = Column(Integer, default=RequestCounts.TEST)
    registration_time = Column(DateTime, default=func.now())
    registration_mail = Column(String, nullable=False)
    ip_ports = Column(String)
    last_update_time = Column(DateTime, onupdate=func.now(), nullable=True)
    is_verified = Column(Integer, default=ClientVerification.NOT_VERIFIED)
    api_key = Column(String, nullable=False)
    

    # owner = relationship("Account", back_populates="order")

    def get_ipports(s:str):
        return 

    def to_dict(self):
        return {
            'service_id': self.service_id,
            'service_org': self.service_org,
            'service_name': self.service_name,
            'subscription_mode': self.subscription_mode,
            'daily_request_counts': self.daily_request_counts,
            'registration_time': str(self.registration_time),
            'registration_mail' : self.registration_mail,
            'last_update_time' : str(self.last_update_time),
            'ip_ports' : self.ip_ports,
            'api_key' : self.api_key
        }