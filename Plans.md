
SuperAdmin Activity :
1. get all users
2. get all orders
3. update order - trying user
4. cancel order - already there need mod
4. veryfy users - upodate user
5. update user  - trying user
5. delete user - trying user



User Activity :
1. signup - [DONE]
2. login - [DONE]
3. user homepage: me - [DONE]
3. update
    a. update password - [DONE]
    b. for phone and email.. raise ticket - [DONE]
4. deleteaccount - [DONE]



Order Activity :
1. create order  - [DONE]
2. get only orderstatus - incart , ordered, shipped , delivered, failed, cancelled - [DONE] 
3. cancelorder  - [DONE] 
4. update status - [DONE] 


To work on



1. Introduce Roles in account table - [Done]
2. Response object Design - [almost]
3. Update user data and admin all user method not working [High priority check tommorow]

4. write verify api - [ Will work on tomorrow]
5. security 
    - user id , order id will be sent as path variable , will be checked on basis of role
    - Exception return model
    - Study



1. ID AND STATUS will be integer only



Caching
------------------
1. Login data will be stored and there will be caching check
    a. key =  access_token
    b. ip and user-agent will be added there. and will be checked while passing request
    b. will check what will happen on basis of token expired
        redis update
2. Order data will be stored
    a. key = user_id + prefix
    b. on update / cancel order, redis update will be happend










FLOW =
sIGNUP - LOGIN 
update anything - LOGIN

create, update and delete order - redis update and delete

