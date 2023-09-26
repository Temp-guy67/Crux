class CommonConstants:
    SALT_LENGTH=8
    RANDOM_ID_LENGTH=4

class OrderStatus:
    IN_CART=1
    ORDERED=2
    IN_TRANSIT=3
    DELIVERED=4
    PREVIOUS_BUY=5

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "5d2755f031972f15d8bbc2ab4c286a7230cb17034366bce0e9dda19096319c0e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


