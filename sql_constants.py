class CommonConstants:
    SALT_LENGTH=8
    RANDOM_ID_LENGTH=4

class Roles:
    USER=1
    ADMIN=2
    SUPER_ADMIN=3

class OrderStatus:
    IN_CART=1
    ORDERED=2
    IN_TRANSIT=3
    DELIVERED=4
    FAILED=5
    CANCELLED=6

class PaymentStatus:
    DUE=1
    PAID=2
    FAILED=3


class RedisConstant:
    PREFIX="ECOMMERCE_"
    
    TOKEN="TOKEN_"
    TTL=""
    


# to get a string like this run: openssl rand -hex 32
SECRET_KEY="5d2755f031972f15d8bbc2ab4c286a7230cb17034366bce0e9dda19096319c0e"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60


