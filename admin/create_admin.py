from app import db
from app import user_datastore
from models import Role, User

email = input('email: ')
password = input('password: ')


user_datastore.create_user(email=email, password=password)
user_datastore.create_role(name='admin', description='administrator')
db.session.commit()
user = User.query.filter(User.email == email).first()
role = Role.query.filter(Role.name == 'admin').first()
user_datastore.add_role_to_user(user, role)
db.session.commit()
print('ok')
