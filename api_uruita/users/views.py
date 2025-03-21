from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import UserRegisterSerializer, VerifyEmailSerializer, LoginSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    View para registrar usuário
    """
    
    serializer_class = UserRegisterSerializer

class VerifyEmailView(APIView):
    """
    View para validar o código de verificação
    """

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']

            try:
                user = User.objects.get(email=email)
                if user.verification_code == code:
                    user.is_verified_email = True
                    user.verification_code = None
                    user.save()
                    return Response({'message': 'Email verificado com sucesso!'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Código inválido!'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'Usuário não encontrado!'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenRefreshView(APIView):
    """
    View para o refresh do auth
    """
    
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token) 
            return Response({"access": access_token}, status=status.HTTP_200_OK)
        except Exception as e: 
            return Response({"error": "Token inválido ou expirado"}, status=status.HTTP_401_UNAUTHORIZED)

class LoginView(APIView):
    """
    View para login de usuário
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            cpf = serializer.validated_data['cpf']
            password = serializer.validated_data['password']
            
            user = authenticate(request, cpf=cpf, password=password)
            
            if user:
                if not user.is_verified_email:
                    return Response({'error': 'Email não verificado!'}, status=status.HTTP_403_FORBIDDEN)

                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({'error': 'Credenciais inválidas!'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """
    View para logout
    """

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout realizado com sucesso!'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': 'Token inválido!'}, status=status.HTTP_400_BAD_REQUEST)