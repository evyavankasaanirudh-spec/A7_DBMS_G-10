class User:
    def __init__(
        self,
        user_id,
        username,
        password_hash,
        role,
        customer_id=None
    ):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.customer_id = customer_id