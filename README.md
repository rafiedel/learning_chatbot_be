# Learning Chatbot BE

_with_ **Django**

## Clean Architecture

```text
app/
├── apps.py              
├── admin.py             
├── entities.py          
├── repositories.py      
├── models.py           
├── serializers.py   
├── services.py     
├── views.py           
├── urls.py             
└── tests.py 
```

This diagram shows that the app is using clean architecture pattern:
- entities.py defines pure business data structures.
- models.py defines ORM tables.
- repositories.py maps between models and entities.
- services.py orchestrates domain logic and external clients.
- views.py handles HTTP requests, delegating to services.
- urls.py routes endpoints to views.

```text
E --> R
M --> R
R --> S
S --> V
V --> U
```