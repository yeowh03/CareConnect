# # backend/examples/auth_strategy_usage.py
# """
# Example usage of authentication strategies in CareConnect.
# This demonstrates how the strategy pattern allows for flexible authentication methods.
# """

# from ..services.auth_strategies import AuthenticationContext, GoogleOAuthStrategy, PasswordStrategy


# class AuthenticationExamples:
#     """Examples of how to use different authentication strategies"""
    
#     @staticmethod
#     def google_oauth_login():
#         """Example: Google OAuth login"""
#         auth_context = AuthenticationContext()
#         auth_context.set_strategy(GoogleOAuthStrategy())
        
#         result, status = auth_context.authenticate({})
#         return result, status
    
#     @staticmethod
#     def password_login(email, password):
#         """Example: Email/password login"""
#         auth_context = AuthenticationContext()
#         auth_context.set_strategy(PasswordStrategy())
        
#         result, status = auth_context.authenticate({
#             "email": email,
#             "password": password
#         })
#         return result, status
    
#     @staticmethod
#     def dynamic_strategy_selection(auth_type, **kwargs):
#         """Example: Dynamic strategy selection based on request type"""
#         auth_context = AuthenticationContext()
        
#         if auth_type == "google":
#             auth_context.set_strategy(GoogleOAuthStrategy())
#         elif auth_type == "password":
#             auth_context.set_strategy(PasswordStrategy())
#         else:
#             return {"error": f"Unsupported authentication type: {auth_type}"}, 400
        
#         result, status = auth_context.authenticate(kwargs)
#         return result, status