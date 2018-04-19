from appserver.repository.userRepository import UserRepository


class UserService(object):
    def insert_new_user(self, request_json):
        response = UserRepository().insert(request_json)
        return response
